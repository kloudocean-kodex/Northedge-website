const LIMIT_WINDOW_MS=10*60*1000;
const LIMIT_COUNT=8;
const buckets=new Map();
const allowedForms=new Set(['appraisal','contact','property-management','rental-register','referral','property-105-tungsten-drive-kalkallo','property-27-design-way-kalkallo','property-31-roseneath-way-mickleham','property-6-alisterus-road-kalkallo','property-6-mathoura-road-mickleham','property-7-rulingia-road-donnybrook']);

const clean=(value,max=2000)=>String(value??'').replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g,'').trim().slice(0,max);
const esc=s=>clean(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const json=(body,status=200)=>Response.json(body,{status,headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});

function rateLimited(ip){
  const now=Date.now();let b=buckets.get(ip);
  if(!b||now-b.start>LIMIT_WINDOW_MS){b={start:now,count:0};buckets.set(ip,b)}
  b.count++;return b.count>LIMIT_COUNT;
}

async function sendResend(env, lead, subject, html){
  if(!(env.RESEND_API_KEY&&env.LEAD_FROM_EMAIL))return {configured:false,ok:false};
  const to=env.LEAD_TO_EMAIL||'admin@northedgerealestate.com.au';
  const r=await fetch('https://api.resend.com/emails',{method:'POST',headers:{Authorization:`Bearer ${env.RESEND_API_KEY}`,'Content-Type':'application/json'},body:JSON.stringify({from:env.LEAD_FROM_EMAIL,to:[to],reply_to:lead.email||undefined,subject,html})});
  return {configured:true,ok:r.ok,status:r.status};
}

async function sendWebhook(env, lead){
  if(!env.LEAD_WEBHOOK_URL)return {configured:false,ok:false};
  const headers={'Content-Type':'application/json'};
  if(env.LEAD_WEBHOOK_TOKEN)headers.Authorization=`Bearer ${env.LEAD_WEBHOOK_TOKEN}`;
  const r=await fetch(env.LEAD_WEBHOOK_URL,{method:'POST',headers,body:JSON.stringify(lead)});
  return {configured:true,ok:r.ok,status:r.status};
}

export async function onRequestPost({ request, env }) {
  const type=request.headers.get('content-type')||'';
  if(!type.includes('application/json'))return json({ok:false,error:'Unsupported request type.'},415);
  const len=Number(request.headers.get('content-length')||0);if(len>50000)return json({ok:false,error:'Request too large.'},413);
  const origin=request.headers.get('origin');
  if(origin){try{if(new URL(origin).host!==new URL(request.url).host)return json({ok:false,error:'Invalid origin.'},403)}catch{return json({ok:false,error:'Invalid origin.'},403)}}
  const ip=request.headers.get('CF-Connecting-IP')||'unknown';
  if(rateLimited(ip))return json({ok:false,error:'Too many requests. Please wait before trying again.'},429);

  let body;try{body=await request.json()}catch{return json({ok:false,error:'Invalid request.'},400)}
  if(clean(body.website,200))return json({ok:true}); // honeypot: silently accept bot noise
  const form=clean(body.form,100);
  if(!allowedForms.has(form))return json({ok:false,error:'Unknown enquiry form.'},400);
  const name=clean(body.name||body.referrer_name,120);
  const email=clean(body.email||body.referrer_email,254);
  const phone=clean(body.phone||body.referrer_phone,80);
  if(!name)return json({ok:false,error:'Please provide your name.'},400);
  if(!email&&!phone)return json({ok:false,error:'Please provide an email address or phone number.'},400);
  if(email&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))return json({ok:false,error:'Please check your email address.'},400);

  const id=crypto.randomUUID();
  const lead={id,receivedAt:new Date().toISOString(),form,name,email,phone,page:clean(body.page,1000),address:clean(body.address,300),timeframe:clean(body.timeframe,120),enquiry:clean(body.enquiry,200),message:clean(body.message,3000),introduction:clean(body.introduction,1000),property_context:clean(body.property_context,1500)};
  const payloadJson=JSON.stringify(lead);
  const requireDb=String(env.REQUIRE_LEAD_DB||'false').toLowerCase()==='true';
  let stored=false;
  if(env.LEADS_DB){
    try{
      await env.LEADS_DB.prepare('INSERT INTO leads (id, received_at, form_type, name, email, phone, payload_json, source_url, delivery_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)').bind(id,lead.receivedAt,form,name,email,phone,payloadJson,lead.page,'pending').run();
      stored=true;
    }catch(e){if(requireDb)return json({ok:false,error:'Enquiry storage is temporarily unavailable. Please call 0430 595 481.'},503)}
  }else if(requireDb){return json({ok:false,error:'Enquiry storage is not configured. Please call 0430 595 481.'},503)}

  const fields=Object.entries(lead).filter(([,v])=>v).map(([k,v])=>`<tr><th align="left" style="padding:6px 12px 6px 0">${esc(k)}</th><td style="padding:6px 0">${esc(v)}</td></tr>`).join('');
  const subject=`NorthEdge website enquiry — ${form}`;
  const html=`<h2>New NorthEdge website enquiry</h2><table>${fields}</table><p>Lead ID: ${esc(id)}</p>`;
  const deliveries=[];
  try{deliveries.push(await sendResend(env,lead,subject,html))}catch{deliveries.push({configured:true,ok:false})}
  try{deliveries.push(await sendWebhook(env,lead))}catch{deliveries.push({configured:true,ok:false})}
  const configured=deliveries.some(x=>x.configured), delivered=deliveries.some(x=>x.ok);
  const status=delivered?'delivered':(stored?'stored':'failed');
  if(env.LEADS_DB&&stored){try{await env.LEADS_DB.prepare('UPDATE leads SET delivery_status = ? WHERE id = ?').bind(status,id).run()}catch{}}
  if(!configured&&!stored)return json({ok:false,error:'Enquiry delivery is not configured. Please call 0430 595 481.'},503);
  if(!delivered&&stored)return json({ok:true,id,stored:true,delivered:false});
  if(!delivered)return json({ok:false,error:'We could not deliver the enquiry. Please call 0430 595 481.'},503);
  return json({ok:true,id,stored,delivered:true},201);
}

export async function onRequest(){return json({ok:false,error:'Method not allowed.'},405)}
