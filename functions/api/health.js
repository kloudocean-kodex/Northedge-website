export async function onRequestGet({ env }) {
  return Response.json({
    ok: true,
    service: 'northedge-website',
    leadDatabase: Boolean(env.LEADS_DB),
    emailDelivery: Boolean(env.RESEND_API_KEY && env.LEAD_FROM_EMAIL),
    webhookDelivery: Boolean(env.LEAD_WEBHOOK_URL)
  }, { headers: { 'Cache-Control': 'no-store' } });
}
