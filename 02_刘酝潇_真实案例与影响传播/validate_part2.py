"""Validate Part 2 without writing shared materials. Exit nonzero on failure."""
from pathlib import Path
import json,re,subprocess,hashlib,xml.etree.ElementTree as ET
from PIL import Image
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
BASE='7124ac0bce4ffbc0b4cc3f2a25eb4e56442cd41c'
checks=[]
def check(name,ok,detail=''):
    checks.append(dict(name=name,passed=bool(ok),detail=detail))
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO,stderr=subprocess.PIPE)
def units(s):
    h=len(re.findall(r'[\u4e00-\u9fff]',s));u=h+len(re.findall(r'[A-Za-z]+(?:-[A-Za-z]+)*|\d+(?:[.,]\d+)*',s))
    return {'han':h,'characters':len(re.sub(r'\s','',s)),'units':u,'seconds':round(u/270*60+5)}
pages=json.loads((ROOT/'page_data.json').read_text(encoding='utf8'))
doc=(ROOT/'PPT逐页完整内容.md').read_text(encoding='utf8')
talk=(ROOT/'完整演讲逐字稿.md').read_text(encoding='utf8')
timing=(ROOT/'各页讲解时间表.md').read_text(encoding='utf8')
bib=(ROOT/'本部分参考文献.md').read_text(encoding='utf8')
check('P11-P20十页',len(pages)==10 and [p['n'] for p in pages]==list(range(11,21)))
for p in pages:
    n=p['n'];m=re.search(rf'(?ms)^## P{n}｜.*?(?=^## P|\Z)',doc);c=m[0] if m else ''
    check(f'P{n}完整页面模板',all(f'### {i}.' in c for i in range(1,8)))
    check(f'P{n}讲稿一致',p['script'] in c and p['script'] in talk)
    check(f'P{n}事实正文对应',all(b in c for b in p['bullets']) and p['title'] in c)
    st=units(p['script']);check(f'P{n}字数和计时',st==p['stats'] and f"|{st['han']}|{st['characters']}|{st['units']}|{st['seconds']}|" in timing)
    check(f'P{n}引用有完整书目',all(f'[{r}]' in bib for r in p['refs']))
    svg=ROOT/f'图表素材/P{n}.svg';png=svg.with_suffix('.png')
    try:
        tree=ET.parse(svg);ok=tree.getroot().attrib.get('viewBox')=='0 0 1600 900'
        with Image.open(png) as im:ok=ok and im.size==(1600,900);im.verify()
    except Exception as e:ok=False
    check(f'P{n}SVG与PNG有效',ok)
    check(f'P{n}图题与正文一致',p['title'] in svg.read_text(encoding='utf8'))
total={k:sum(units(p['script'])[k] for p in pages) for k in units(pages[0]['script'])}
check('合计统计一致',total==json.loads((ROOT/'统计结果.json').read_text(encoding='utf8')))
check('中央估时12至14分钟',720<=total['seconds']<=840,str(total))
check('口播包含开场和结尾','汪雨航' in pages[0]['script'] and '吴昀轩' in pages[-1]['script'])
required=['典型案例研究.md','本部分参考文献.md','制作交接与排练卡.md','第二部分_老师反馈与修订说明.md','第二部分_知识讲透与答辩准备.md','备用材料_2016乌克兰.md','事实核查与验收.md','恢复核验记录.json','README.md']
check('所需补充材料齐全',all((ROOT/x).is_file() for x in required))
knowledge=(ROOT/'第二部分_知识讲透与答辩准备.md').read_text(encoding='utf8')
check('13个知识点含六项解释',all(knowledge.count(t)>=13 for t in ['**通俗解释','**较严格的解释','**教学例子','**常见误解','**可能追问','**30秒回答']))
broken=[]
for f in ROOT.rglob('*.md'):
    text=f.read_text(encoding='utf8')
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if re.match(r'https?://|mailto:|#',target):continue
        if not (f.parent/target.split('#')[0]).exists():broken.append(str(f.relative_to(ROOT))+': '+target)
check('Markdown相对链接有效',not broken,'; '.join(broken))
check('无编码替换或占位符',all('\ufffd' not in f.read_text(encoding='utf8') and not re.search(r'TODO|TBD|待填写|占位文字',f.read_text(encoding='utf8')) for f in ROOT.rglob('*.md')))
check('10组图及4CSV齐全',all(len(list((ROOT/'图表素材').glob('*.'+ext)))==10 for ext in ['svg','png','mmd']) and len(list((ROOT/'图表素材').glob('*.csv')))==4)
v=json.loads((ROOT/'图表验证.json').read_text(encoding='utf8'))
check('Mermaid实际解析通过',len(v['mermaid'])==10 and all(x['ok'] for x in v['mermaid']))
check('SVG文本未超出画布',not v['text'])
render=json.loads((ROOT/'渲染记录.json').read_text(encoding='utf8'))
check('PNG对应最新SVG源文件',len(render)==10 and all(
    record.get('svg_sha256')==hashlib.sha256((ROOT/'图表素材'/record['svg']).read_bytes()).hexdigest()
    and record.get('png_sha256')==hashlib.sha256((ROOT/'图表素材'/record['png']).read_bytes()).hexdigest()
    for record in render))
check('无最终PPT文件',not list(ROOT.rglob('*.pptx')) and not list(ROOT.rglob('*.ppt')))
check('供电例子明确必要条件','唯一有效' in pages[4]['script'] and '备用' in pages[4]['script'])
check('图示不冒充现场拓扑','教学示意' in pages[2]['script'] and '取证拓扑' in pages[2]['script'])
check('Colonial保留运营方主语','运营方下达停运决定' in pages[7]['script'])
check('恢复事实与启示分开','报告支持的事实' in pages[5]['script'] and '工程要求' in pages[5]['script'])
changed=[x for x in git('diff','--name-only','-z',BASE).decode().split('\0') if x]
untracked=[x for x in git('ls-files','--others','--exclude-standard','-z').decode().split('\0') if x]
check('改动和新增只在第二部分',all(x.startswith(ROOT.name+'/') for x in changed+untracked))
check('远程已有提交保留',subprocess.run(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=REPO,capture_output=True).returncode==0)
check('Git差异无空白错误',subprocess.run(['git','diff','--check',BASE],cwd=REPO,capture_output=True).returncode==0)
tracked=git('ls-tree','-r','--name-only','-z',BASE).decode().split('\0')
manifest=[]
for f in sorted(ROOT.rglob('*')):
    if not f.is_file() or '__pycache__' in f.parts or f.name in ['交付文件清单.json','验收结果.json']:continue
    manifest.append({'file':f.relative_to(ROOT).as_posix(),'status':'updated_or_retained' if f.relative_to(REPO).as_posix() in tracked else 'new','bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(ROOT/'交付文件清单.json').write_text(json.dumps({'base':BASE,'excludes':['交付文件清单.json','验收结果.json'],'files':manifest},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
result={'passed':all(c['passed'] for c in checks),'check_count':len(checks),'stats':total,'checks':checks,'limitation':'自动检查不等于事实或视觉审查；人工阅读和图表目视检查另见事实核查与验收.md。'}
(ROOT/'验收结果.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'passed':result['passed'],'checks':len(checks),'stats':total,'errors':[c for c in checks if not c['passed']]},ensure_ascii=False))
raise SystemExit(0 if result['passed'] else 1)
