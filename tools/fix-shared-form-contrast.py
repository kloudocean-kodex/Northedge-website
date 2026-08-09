from pathlib import Path
root=Path(__file__).resolve().parents[1]
css=root/'public/assets/css/final-demo.css'
s=css.read_text(encoding='utf-8')
marker='/* Production QA: shared accessible light-form tokens */'
block='''\n\n/* Production QA: shared accessible light-form tokens */\n.light-form .form-field label,\n.enquiry-card .form-field label{\n  color:#3F4742!important;\n}\n.page-rent .content-section .section-title em{\n  color:#815B25;\n}\n'''
if marker not in s:
    css.write_text(s.rstrip()+block+'\n',encoding='utf-8')
qa=root/'docs/QA_REPORT.md'
q=qa.read_text(encoding='utf-8')
note='''\n## Shared form contrast correction — 9 August 2026\n\nA full-route Cloudflare preview sweep showed the same low-contrast label token on light forms and property enquiry cards, plus one Rent section title accent. The shared light-form/enquiry-card label colour is now `#3F4742` and the affected Rent light-surface accent uses `#815B25`. These are shared design-token corrections rather than page-by-page exceptions. A deployment-synchronised 28-route accessibility sweep is required after this change.\n'''
if '## Shared form contrast correction — 9 August 2026' not in q:
    qa.write_text(q.rstrip()+'\n'+note,encoding='utf-8')
