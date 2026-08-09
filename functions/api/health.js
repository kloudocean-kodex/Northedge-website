const headersFor=(request)=>{
  const h={
    'Cache-Control':'no-store',
    'X-Content-Type-Options':'nosniff',
    'X-Frame-Options':'DENY',
    'Referrer-Policy':'strict-origin-when-cross-origin',
    'Permissions-Policy':'camera=(), microphone=(), geolocation=()',
    'Content-Security-Policy':"default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
  };
  try{if(new URL(request.url).hostname.endsWith('.pages.dev'))h['X-Robots-Tag']='noindex, nofollow'}catch{}
  return h;
};

export async function onRequestGet({request,env}){
  const requireDb=String(env.REQUIRE_LEAD_DB||'false').toLowerCase()==='true';
  let databaseConfigured=Boolean(env.LEADS_DB);
  let databaseHealthy=false;
  let schemaHealthy=false;
  let databaseError=null;

  if(env.LEADS_DB){
    try{
      await env.LEADS_DB.prepare('SELECT 1 AS ok').first();
      databaseHealthy=true;
      const rows=await env.LEADS_DB.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('leads','lead_rate_limits')").all();
      const names=new Set((rows.results||[]).map(r=>r.name));
      schemaHealthy=names.has('leads')&&names.has('lead_rate_limits');
    }catch(e){
      databaseError=e?.name||'DatabaseError';
    }
  }

  const emailDelivery=Boolean(env.RESEND_API_KEY&&env.LEAD_FROM_EMAIL);
  const webhookDelivery=Boolean(env.LEAD_WEBHOOK_URL);
  const ok=(!requireDb||(databaseConfigured&&databaseHealthy&&schemaHealthy));

  return Response.json({
    ok,
    service:'northedge-website',
    leadDatabase:databaseConfigured,
    leadDatabaseHealthy:databaseHealthy,
    leadSchemaHealthy:schemaHealthy,
    emailDelivery,
    webhookDelivery,
    downstreamDeliveryConfigured:emailDelivery||webhookDelivery,
    ...(databaseError?{databaseError}:{}),
  },{status:ok?200:503,headers:headersFor(request)});
}
