CREATE TABLE IF NOT EXISTS leads (
  id TEXT PRIMARY KEY,
  received_at TEXT NOT NULL,
  form_type TEXT NOT NULL,
  name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  payload_json TEXT NOT NULL,
  source_url TEXT,
  delivery_status TEXT NOT NULL DEFAULT 'pending'
);
CREATE INDEX IF NOT EXISTS idx_leads_received_at ON leads(received_at);
CREATE INDEX IF NOT EXISTS idx_leads_form_type ON leads(form_type);

CREATE TABLE IF NOT EXISTS lead_rate_limits (
  key TEXT NOT NULL,
  window_start INTEGER NOT NULL,
  count INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (key, window_start)
);
CREATE INDEX IF NOT EXISTS idx_lead_rate_limits_window_start ON lead_rate_limits(window_start);
