const LIMIT_WINDOW_MS=10*60*1000;
const LIMIT_COUNT=20;
const MAX_BODY_BYTES=50000;
const allowedForms=new Set(['appraisal','contact','property-management','rental-register','referral','property-105-tungsten-drive-kalkallo','property-27-design-way-kalkallo','property-31-roseneath-way-mickleham','property-6-alisterus-road-kalkallo','property-6-mathoura-road-mickleham','property-7-rulingia-road-donnybrook']);

const staticSecurity={
  'Cache-Control':'no-store',
  'X-Content-Type-Options':'nosniff',
  'X-Frame-Options':'DENY',
  'Referrer-Policy':'strict-origin-when-cross-origin',
  'Permissions-Policy':'camera=(), microphone=(), geolocation=()',
  'Content-Security-Policy':"default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
};
const headersFor=(request,extra={})=>{
  const h={...staticSecurity,...extra};
  try{if(new URL(request.url).hostname.endsWith('.pages.dev'))h['X-Robots-Tag']='noindex, nofollow'}catch{}
  return h;
};
const json=(request,body,status=200,extra={})=>Response.json(body,{status,headers:headersFor(request,extra)});
const htmlResponse=(request,html,status=400,extra={})=>new Response(html,{status,headers:headersFor(request,{'Content-Type':'text/html; charset=utf-8',...extra})});

const scalar=(value)=>{
  if(value===null||value===undefined)return '';
  if(typeof value==='string'||typeof value==='number'||typeof value==='boolean')return String(value);
  return '';
};
const clean=(value)=>scalar(value).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g,'').trim();
const field=(body,key,max,{required=false}={})=>{
  const v=clean(body[key]);
  if(required&&!v)throw new Error(`required:${key}`);
  if(v.length>max)throw new Error(`length:${key}`);
  return v;
};
const esc=s=>clean(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const canonicalSource=(value,fallback)=>{
  const raw=clean(value)||clean(fallback);
  if(!raw)return '';
  try{const u=new URL(raw);return `${u.origin}${u.pathname}`}catch{return ''}
};

async function ipKey(ip){
  const bytes=new TextEncoder().encode(`northedge-leads-v1:${ip}`);
  const digest=await crypto.subtle.digest('SHA-256',bytes);
  return [...new Uint8Array(digest)].map(b=>b.toString(16).padStart(2,'0')).join('');
}

async function rateLimited(env,ip){
  if(!env.LEADS_DB)return false;
  const now=Date.now();
  const windowStart=Math.floor(now/LIMIT_WINDOW_MS)*LIMIT_WINDOW_MS;
  const key=await ipKey(ip);
  await env.LEADS_DB.prepare(`INSERT INTO lead_rate_limits (key, window_start, count) VALUES (?, ?, 1)
    ON CONFLICT(key, window_start) DO UPDATE SET count = count + 1`).bind(key,windowStart).run();
  const row=await env.LEADS_DB.prepare('SELECT count FROM lead_rate_limits WHERE key = ? AND window_start = ?').bind(key,windowStart).first();
  if(Math.random()<0.02){try{await env.LEADS_DB.prepare('DELETE FROM lead_rate_limits WHERE window_start < ?').bind(windowStart-(6*LIMIT_WINDOW_MS)).run()}catch{}}
  return Number(row?.count||0)>LIMIT_COUNT;
}

async function sendResend(env,lead,subject,html){
  if(!(env.RESEND_API_KEY&&env.LEAD_FROM_EMAIL))return {configured:false,ok:false};
  const to=env.LEAD_TO_EMAIL||'admin@northedgerealestate.com.au';
  const r=await fetch('https://api.resend.com/emails',{method:'POST',headers:{Authorization:`Bearer ${env.RESEND_API_KEY}`,'Content-Type':'application/json'},body:JSON.stringify({from:env.LEAD_FROM_EMAIL,to:[to],reply_to:lead.email||undefined,subject,html})});
  return {configured:true,ok:r.ok,status:r.status};
}

async function sendWebhook(env,lead){
  if(!env.LEAD_WEBHOOK_URL)return {configured:false,ok:false};
  const headers={'Content-Type':'application/json'};
  if(env.LEAD_WEBHOOK_TOKEN)headers.Authorization=`Bearer ${env.LEAD_WEBHOOK_TOKEN}`;
  const r=await fetch(env.LEAD_WEBHOOK_URL,{method:'POST',headers,body:JSON.stringify(lead)});
  return {configured:true,ok:r.ok,status:r.status};
}

function browserFailure(request,message,status=400){
  const body=`<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Enquiry not sent | NorthEdge Real Estate</title></head><body><main><h1>We could not receive your enquiry.</h1><p>${esc(message)}</p><p><a href="javascript:history.back()">Go back</a> or call <a href="tel:0430595481">0430 595 481</a>.</p></main></body></html>`;
  return htmlResponse(request,body,status);
}

async function parseBody(request){
  const type=(request.headers.get('content-type')||'').toLowerCase();
  const raw=await request.text();
  if(new TextEncoder().encode(raw).byteLength>MAX_BODY_BYTES)throw new Error('too-large');
  if(type.includes('application/json')){
    try{return {body:JSON.parse(raw),html:false}}catch{throw new Error('invalid-json')}
  }
  if(type.includes('application/x-www-form-urlencoded')){
    return {body:Object.fromEntries(new URLSearchParams(raw)),html:true};
  }
  throw new Error('unsupported');
}

export async function onRequestPost({request,env}){
  const acceptHtml=!(request.headers.get('accept')||'').includes('application/json');
  const origin=request.headers.get('origin');
  if(origin){try{if(new URL(origin).host!==new URL(request.url).host)return acceptHtml?browserFailure(request,'Invalid request origin.',403):json(request,{ok:false,error:'Invalid origin.'},403)}catch{return acceptHtml?browserFailure(request,'Invalid request origin.',403):json(request,{ok:false,error:'Invalid origin.'},403)}}

  let parsed;
  try{parsed=await parseBody(request)}catch(e){
    const code=e.message==='too-large'?413:(e.message==='unsupported'?415:400);
    const message=e.message==='too-large'?'Request too large.':(e.message==='unsupported'?'Unsupported request type.':'Invalid request.');
    return acceptHtml?browserFailure(request,message,code):json(request,{ok:false,error:message},code);
  }
  const body=parsed.body;
  if(!body||typeof body!=='object'||Array.isArray(body))return acceptHtml?browserFailure(request,'Invalid request.',400):json(request,{ok:false,error:'Invalid request.'},400);
  if(clean(body.website))return acceptHtml?Response.redirect(new URL('/thank-you',request.url),303):json(request,{ok:true,botFiltered:true});

  const requireDb=String(env.REQUIRE_LEAD_DB||'false').toLowerCase()==='true';
  if(!env.LEADS_DB&&requireDb)return acceptHtml?browserFailure(request,'Enquiry storage is temporarily unavailable. Please call 0430 595 481.',503):json(request,{ok:false,error:'Enquiry storage is not configured. Please call 0430 595 481.'},503);

  if(env.LEADS_DB){
    try{
      const ip=request.headers.get('CF-Connecting-IP')||'unknown';
      if(await rateLimited(env,ip))return acceptHtml?browserFailure(request,'Too many requests. Please wait before trying again.',429):json(request,{ok:false,error:'Too many requests. Please wait before trying again.'},429,{'Retry-After':'600'});
    }catch(e){
      console.error(JSON.stringify({event:'lead_rate_limit_error',errorClass:e?.name||'Error'}));
      if(requireDb)return acceptHtml?browserFailure(request,'Enquiry storage is temporarily unavailable. Please call 0430 595 481.',503):json(request,{ok:false,error:'Enquiry storage is temporarily unavailable. Please call 0430 595 481.'},503);
    }
  }

  let form,name,email,phone,address,timeframe,enquiry,message,introduction,property_context,referral_consent;
  try{
    form=field(body,'form',100,{required:true});
    if(!allowedForms.has(form))throw new Error('unknown-form');
    name=field({...body,name:body.name||body.referrer_name},'name',120,{required:true});
    email=field({...body,email:body.email||body.referrer_email},'email',254,{required:true});
    phone=field({...body,phone:body.phone||body.referrer_phone},'phone',80,{required:true});
    address=field(body,'address',300);timeframe=field(body,'timeframe',120);enquiry=field(body,'enquiry',200);
    message=field(body,'message',3000);introduction=field(body,'introduction',1000);property_context=field(body,'property_context',1500);
    referral_consent=field(body,'referral_consent',30);
  }catch(e){
    const msg=e.message==='unknown-form'?'Unknown enquiry form.':(e.message.startsWith('length:')?'One of the submitted fields is too long.':'Please complete all required contact fields.');
    return acceptHtml?browserFailure(request,msg,400):json(request,{ok:false,error:msg},400);
  }
  if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))return acceptHtml?browserFailure(request,'Please check your email address.',400):json(request,{ok:false,error:'Please check your email address.'},400);
  if(form==='referral'&&referral_consent!=='confirmed')return acceptHtml?browserFailure(request,'Please confirm the referral terms before submitting.',400):json(request,{ok:false,error:'Please confirm the referral terms before submitting.'},400);

  const id=crypto.randomUUID();
  const receivedAt=new Date().toISOString();
  const page=canonicalSource(body.page,request.headers.get('referer'));
  const lead={id,receivedAt,form,name,email,phone,page,address,timeframe,enquiry,message,introduction,property_context,referral_consent};
  const payloadJson=JSON.stringify(lead);
  let stored=false;
  if(env.LEADS_DB){
    try{
      await env.LEADS_DB.prepare('INSERT INTO leads (id, received_at, form_type, name, email, phone, payload_json, source_url, delivery_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)').bind(id,receivedAt,form,name,email,phone,payloadJson,page,'pending').run();
      stored=true;
    }catch(e){
      console.error(JSON.stringify({event:'lead_storage_error',id,form,errorClass:e?.name||'Error'}));
      if(requireDb)return acceptHtml?browserFailure(request,'Enquiry storage is temporarily unavailable. Please call 0430 595 481.',503):json(request,{ok:false,error:'Enquiry storage is temporarily unavailable. Please call 0430 595 481.'},503);
    }
  }

  const fields=Object.entries(lead).filter(([,v])=>v).map(([k,v])=>`<tr><th align="left" style="padding:6px 12px 6px 0">${esc(k)}</th><td style="padding:6px 0">${esc(v)}</td></tr>`).join('');
  const subject=`NorthEdge website enquiry — ${form}`;
  const emailHtml=`<h2>New NorthEdge website enquiry</h2><table>${fields}</table><p>Lead ID: ${esc(id)}</p>`;
  const deliveries=[];
  try{deliveries.push(await sendResend(env,lead,subject,emailHtml))}catch(e){deliveries.push({configured:true,ok:false});console.error(JSON.stringify({event:'lead_delivery_error',id,form,channel:'email',errorClass:e?.name||'Error'}))}
  try{deliveries.push(await sendWebhook(env,lead))}catch(e){deliveries.push({configured:true,ok:false});console.error(JSON.stringify({event:'lead_delivery_error',id,form,channel:'webhook',errorClass:e?.name||'Error'}))}
  const configured=deliveries.some(x=>x.configured),delivered=deliveries.some(x=>x.ok);
  const status=delivered?'delivered':(stored?'stored':'failed');
  if(env.LEADS_DB&&stored){try{await env.LEADS_DB.prepare('UPDATE leads SET delivery_status = ? WHERE id = ?').bind(status,id).run()}catch(e){console.error(JSON.stringify({event:'lead_status_update_error',id,form,errorClass:e?.name||'Error'}))}}
  console.log(JSON.stringify({event:'lead_submission',id,form,stored,delivered,status}));

  if(!configured&&!stored)return acceptHtml?browserFailure(request,'Enquiry delivery is not configured. Please call 0430 595 481.',503):json(request,{ok:false,error:'Enquiry delivery is not configured. Please call 0430 595 481.'},503);
  if(acceptHtml){
    if(stored||delivered)return Response.redirect(new URL('/thank-you',request.url),303);
    return browserFailure(request,'We could not receive your enquiry. Please call 0430 595 481.',503);
  }
  if(!delivered&&stored)return json(request,{ok:true,id,stored:true,delivered:false,status:'stored'},202);
  if(!delivered)return json(request,{ok:false,error:'We could not deliver the enquiry. Please call 0430 595 481.'},503);
  return json(request,{ok:true,id,stored,delivered:true,status:'delivered'},201);
}

export async function onRequest({request}){
  return json(request,{ok:false,error:'Method not allowed.'},405,{'Allow':'POST'});
}
