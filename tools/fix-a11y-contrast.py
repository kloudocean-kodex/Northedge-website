from pathlib import Path

root=Path(__file__).resolve().parents[1]
css=root/'public/assets/css/final-demo.css'
s=css.read_text(encoding='utf-8')
marker='/* Production QA: accessible brass on light editorial surfaces */'
block='''\n\n/* Production QA: accessible brass on light editorial surfaces */\n.split-copy .section-title em,\n.content-section.is-stone .section-title em{\n  color:#815B25;\n}\n'''
if marker not in s:
    css.write_text(s.rstrip()+block+'\n',encoding='utf-8')

qa=root/'docs/QA_REPORT.md'
q=qa.read_text(encoding='utf-8')
note='''\n## Preview accessibility correction — 9 August 2026\n\nAutomated Chromium + axe testing on the Cloudflare branch preview identified insufficient contrast for the large italic brass title accents on the About page. The affected text used `#D9B97A` against `#F7F4EE` / `#EEE8DE`, producing 1.71:1 / 1.54:1 where WCAG requires 3:1 for large text. Light-surface About title accents now use the established darker NorthEdge brass `#815B25`. The complete route-level accessibility gate must pass again on the replacement preview before merge.\n'''
if '## Preview accessibility correction — 9 August 2026' not in q:
    qa.write_text(q.rstrip()+'\n'+note,encoding='utf-8')
