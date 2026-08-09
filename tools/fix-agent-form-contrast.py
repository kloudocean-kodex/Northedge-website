from pathlib import Path
root=Path(__file__).resolve().parents[1]
css=root/'public/assets/css/final-demo.css'
s=css.read_text(encoding='utf-8')
marker='/* Production QA: accessible labels on light appraisal forms */'
block='''\n\n/* Production QA: accessible labels on light appraisal forms */\n.content-section.is-stone .light-form .form-field label{\n  color:#3F4742!important;\n}\n'''
if marker not in s:
    css.write_text(s.rstrip()+block+'\n',encoding='utf-8')
qa=root/'docs/QA_REPORT.md'
q=qa.read_text(encoding='utf-8')
note='''\n## Agent appraisal label contrast correction — 9 August 2026\n\nThe full Cloudflare preview axe pass identified insufficient contrast on five labels in the Gurinder appraisal form. Labels on light appraisal surfaces now use `#3F4742`, preserving the restrained visual system while exceeding WCAG AA text contrast requirements. The complete preview gate must pass again before merge.\n'''
if '## Agent appraisal label contrast correction — 9 August 2026' not in q:
    qa.write_text(q.rstrip()+'\n'+note,encoding='utf-8')
