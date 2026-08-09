const QA_HOST='cutover-legacy-routing-previ.northedge-website.pages.dev';
const QA_KEY='2026-08-09-cutover-r1';
const QA_EMAIL_PREFIX='qa-northedge-preview-';
const headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','X-Robots-Tag':'noindex, nofollow'};
const json=(body,status=200)=>Response.json(body,{status,headers});
const allowed=(url)=>url.hostname===QA_HOST&&url.searchParams.get('qa')===QA_KEY;

async function ensureSchema(env){
  await env.LEADS_DB.prepare(`CREATE TABLE IF NOT EXISTS lead_rate_limits (
    key TEXT NOT NULL,
    window_start INTEGER NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (key, window_start)
  )`).run();
  await env.LEADS_DB.prepare('CREATE INDEX IF NOT EXISTS idx_lead_rate_limits_window_start ON lead_rate_limits(window_start)').run();
}

async function schemaState(env){
  const rows=await env.LEADS_DB.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('leads','lead_rate_limits') ORDER BY name").all();
  const names=(rows.results||[]).map(r=>r.name);
  const count=await env.LEADS_DB.prepare('SELECT COUNT(*) AS n FROM leads').first();
  return {tables:names,leadCount:Number(count?.n||0),schemaHealthy:names.includes('leads')&&names.includes('lead_rate_limits')};
}

export async function onRequestGet({request,env}){
  const url=new URL(request.url);
  if(!allowed(url))return json({ok:false},404);
  if(!env.LEADS_DB)return json({ok:false,error:'LEADS_DB not bound'},503);
  try{
    const action=url.searchParams.get('action')||'migrate';
    if(action==='migrate'){
      await ensureSchema(env);
      const state=await schemaState(env);
      return json({ok:state.schemaHealthy,...state});
    }
    if(action==='batch'){
      const batch=(url.searchParams.get('batch')||'').replace(/[^a-zA-Z0-9_-]/g,'').slice(0,80);
      if(!batch)return json({ok:false,error:'batch required'},400);
      const pattern=`${QA_EMAIL_PREFIX}${batch}-%@example.com`;
      const rows=await env.LEADS_DB.prepare('SELECT form_type, COUNT(*) AS n FROM leads WHERE email LIKE ? GROUP BY form_type ORDER BY form_type').bind(pattern).all();
      const total=await env.LEADS_DB.prepare('SELECT COUNT(*) AS n FROM leads WHERE email LIKE ?').bind(pattern).first();
      return json({ok:true,batch,total:Number(total?.n||0),forms:(rows.results||[]).map(r=>({form:r.form_type,count:Number(r.n||0)}))});
    }
    return json({ok:false,error:'unknown action'},400);
  }catch(e){
    return json({ok:false,errorClass:e?.name||'DatabaseError'},500);
  }
}

export async function onRequestPost({request,env}){
  const url=new URL(request.url);
  if(!allowed(url))return json({ok:false},404);
  if(!env.LEADS_DB)return json({ok:false,error:'LEADS_DB not bound'},503);
  try{
    if(url.searchParams.get('action')!=='cleanup')return json({ok:false,error:'unknown action'},400);
    const batch=(url.searchParams.get('batch')||'').replace(/[^a-zA-Z0-9_-]/g,'').slice(0,80);
    if(!batch)return json({ok:false,error:'batch required'},400);
    const pattern=`${QA_EMAIL_PREFIX}${batch}-%@example.com`;
    const before=await env.LEADS_DB.prepare('SELECT COUNT(*) AS n FROM leads WHERE email LIKE ?').bind(pattern).first();
    await env.LEADS_DB.prepare('DELETE FROM leads WHERE email LIKE ?').bind(pattern).run();
    const after=await env.LEADS_DB.prepare('SELECT COUNT(*) AS n FROM leads WHERE email LIKE ?').bind(pattern).first();
    return json({ok:Number(after?.n||0)===0,batch,deleted:Number(before?.n||0),remaining:Number(after?.n||0)});
  }catch(e){
    return json({ok:false,errorClass:e?.name||'DatabaseError'},500);
  }
}

export function onRequest(){return json({ok:false},405)}
