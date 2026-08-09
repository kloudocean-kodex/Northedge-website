const QA_HOST='cutover-legacy-routing-previ.northedge-website.pages.dev';
const QA_HEADER='2026-08-09-cutover-r1';
const headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','X-Robots-Tag':'noindex, nofollow'};
const json=(body,status=200)=>Response.json(body,{status,headers});

export async function onRequestGet({request,env}){
  const url=new URL(request.url);
  if(url.hostname!==QA_HOST||request.headers.get('x-northedge-qa')!==QA_HEADER)return json({ok:false},404);
  if(!env.LEADS_DB)return json({ok:false,error:'LEADS_DB not bound'},503);
  try{
    await env.LEADS_DB.prepare(`CREATE TABLE IF NOT EXISTS lead_rate_limits (
      key TEXT NOT NULL,
      window_start INTEGER NOT NULL,
      count INTEGER NOT NULL DEFAULT 0,
      PRIMARY KEY (key, window_start)
    )`).run();
    await env.LEADS_DB.prepare('CREATE INDEX IF NOT EXISTS idx_lead_rate_limits_window_start ON lead_rate_limits(window_start)').run();
    const rows=await env.LEADS_DB.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('leads','lead_rate_limits') ORDER BY name").all();
    const names=(rows.results||[]).map(r=>r.name);
    return json({ok:names.includes('leads')&&names.includes('lead_rate_limits'),tables:names});
  }catch(e){
    return json({ok:false,errorClass:e?.name||'DatabaseError'},500);
  }
}

export function onRequest(){return json({ok:false},405)}
