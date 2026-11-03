from pathlib import Path
import json,re,hashlib,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
pages=json.loads((ROOT/'sources/page_data.json').read_text(encoding='utf-8'))
refs=json.loads((ROOT/'sources/references.json').read_text(encoding='utf-8'))
stats=json.loads((ROOT/'05_质量验收/统计结果.json').read_text(encoding='utf-8'))
errors=[];checks=[]
def check(name,ok,detail=''):
    checks.append(dict(name=name,passed=bool(ok),detail=detail))
    if not ok:errors.append(name+': '+detail)
check('正式页30页',len(pages)==30)
packages=sorted(ROOT.glob('0[123]_*/PPT逐页完整内容.md'))
check('三份独立内容包',len(packages)==3)
for block,p in enumerate(packages):
    s=p.read_text(encoding='utf-8');chunks=re.split(r'(?m)^## P\d{2}｜',s)[1:]
    check(p.parent.name+'页面数量',len(chunks)==10)
    for j,c in enumerate(chunks):
        check(f'P{block*10+j+1:02d}八项模板',all(f'### {i}.' in c for i in range(1,9)))
        script=pages[block*10+j]['script']
        check(f'P{block*10+j+1:02d}讲稿一致',script in c and script in (p.parent/'完整演讲逐字稿.md').read_text(encoding='utf-8'))
        check(f'P{block*10+j+1:02d}来源存在',all(x in refs for x in pages[block*10+j]['refs']))
check('至少20项有使用的核心文献',len(refs)>=20 and set(refs)==set(x for p in pages for x in p['refs']))
check('每人中央时长12–15分钟',all(12<=x['minutes']<=15 for x in stats))
check('全组中央时长36–42分钟',36<=sum(x['seconds'] for x in stats)/60<=42)
check('每人讲稿超过3000汉字',all(x['han']>=3000 for x in stats))
qa=(ROOT/'04_全组资料/高质量答辩问题与答案.md').read_text(encoding='utf-8')
check('至少15个答辩题且包含主答简答详答证据',len(re.findall(r'^## Q\d+',qa,re.M))>=15 and all(qa.count(x)>=30 for x in ['主答：','30秒内回答','进一步解释','证据：']))
svgs=list(ROOT.glob('0[123]_*/图表素材/*.svg'));pngs=list(ROOT.glob('0[123]_*/图表素材/*.png'));mmd=list(ROOT.glob('0[123]_*/图表素材/*.mmd'));csvs=list(ROOT.glob('0[123]_*/图表素材/*.csv'))
check('31组图表载体齐全',len(svgs)==len(pngs)==len(mmd)==31)
for p in svgs:
    try:E.parse(p)
    except Exception as e:errors.append(str(p)+str(e))
check('9份表格CSV',len(csvs)==9)
mer=json.loads((ROOT/'05_质量验收/mermaid_validation.json').read_text(encoding='utf-8'))
check('Mermaid实际解析',len(mer)==31 and all(x['ok'] for x in mer))
check('没有生成PPT或PPTX',not list(ROOT.rglob('*.pptx')) and not list(ROOT.rglob('*.ppt')))
broken=[]
for p in ROOT.rglob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if re.match(r'https?://|mailto:|#',target):continue
        if not (p.parent/target.split('#')[0]).exists():broken.append(str(p.relative_to(ROOT))+': '+target)
check('Markdown本地链接',not broken,'；'.join(broken))
check('无编码替换符',all('\ufffd' not in p.read_text(encoding='utf-8') for p in ROOT.rglob('*.md')))
check('讨论提纲与课程报告存在',all((ROOT/x).exists() for x in ['01_老师讨论提纲.md','04_全组资料/课程报告正文.md']))
inputs=[]
for p in ROOT.parent.iterdir():
    if p.suffix.lower() in ['.pptx','.xlsx']:inputs.append(dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size))
result=dict(passed=not errors,checks=checks,errors=errors,input_files=inputs,counts=dict(pages=30,refs=len(refs),svg=len(svgs),png=len(pngs),mermaid=len(mmd),csv=len(csvs)))
(ROOT/'05_质量验收/自动检查结果.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(passed=not errors,errors=errors,checks=len(checks),counts=result['counts']),ensure_ascii=False))
if errors:raise SystemExit(1)
