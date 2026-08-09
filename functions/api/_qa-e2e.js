const HOST='cutover-legacy-routing-previ.northedge-website.pages.dev';
const KEY='northedge-e2e-20260809-v2';
const headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','X-Robots-Tag':'noindex, nofollow'};
const json=(body,status=200)=>Response.json(body,{status,headers});
const allowed=request=>{const u=new URL(request.url);return u.hostname===HOST&&u.searchParams.get('key')===KEY};

export async function onRequestGet({request,env}){
  if(!allowed(request))return json({ok:false},404);
  if(!env.LEADS_DB)return json({ok:false,error:'LEADS_DB not bound'},503);
  try{
    const u=new URL(request.url);const batch=(u.searchParams.get('batch')||'').trim();
    const total=await env.LEADS_DB.prepare('SELECT COUNT(*) AS n FROM leads').first();
    let rows=[];
    if(batch){
      const r=await env.LEADS_DB.prepare("SELECT id,form_type,name,email,phone,payload_json,source_url,delivery_status FROM leads WHERE name LIKE ? ORDER BY received_at").bind(`QA NorthEdge E2E ${batch}%`).all();
      rows=r.results||[];
    }
    return json({ok:true,total:Number(total?.n||0),batch,rows});
  }catch(e){return json({ok:false,errorClass:e?.name||'DatabaseError'},500)}
}

export async function onRequestDelete({request,env}){
  if(!allowed(request))return json({ok:false},404);
  if(!env.LEADS_DB)return json({ok:false,error:'LEADS_DB not bound'},503);
  try{
    const u=new URL(request.url);const batch=(u.searchParams.get('batch')||'').trim();
    if(!/^B[0-9]{8,20}$/.test(batch))return json({ok:false,error:'Invalid batch'},400);
    const before=await env.LEADS_DB.prepare("SELECT COUNT(*) AS n FROM leads WHERE name LIKE ?").bind(`QA NorthEdge E2E ${batch}%`).first();
    await env.LEADS_DB.prepare("DELETE FROM leads WHERE name LIKE ?").bind(`QA NorthEdge E2E ${batch}%`).run();
    const total=await env.LEADS_DB.prepare('SELECT COUNT(*) AS n FROM leads').first();
    return json({ok:true,deleted:Number(before?.n||0),total:Number(total?.n||0)});
  }catch(e){return json({ok:false,errorClass:e?.name||'DatabaseError'},500)}
}

export function onRequest(){return json({ok:false},405)}
