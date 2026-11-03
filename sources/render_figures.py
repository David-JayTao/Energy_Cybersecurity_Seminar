from pathlib import Path
import subprocess,concurrent.futures,json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
CHROME=Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
TMP=ROOT/'05_质量验收'/'render_profiles';TMP.mkdir(exist_ok=True)
def render(p):
    target=p.with_suffix('.png')
    cmd=[str(CHROME),'--headless','--disable-gpu','--hide-scrollbars','--no-first-run','--no-default-browser-check','--allow-file-access-from-files','--force-device-scale-factor=1','--window-size=1600,900','--screenshot='+str(target),'--user-data-dir='+str(TMP/p.stem),p.as_uri()]
    a=subprocess.run(cmd,capture_output=True,timeout=45,creationflags=subprocess.CREATE_NO_WINDOW)
    if not target.exists():return {'file':str(p),'error':a.stderr.decode('utf-8','replace')[-500:]}
    im=Image.open(target)
    return {'file':str(p.relative_to(ROOT)),'png':str(target.relative_to(ROOT)),'size':im.size}
files=sorted(ROOT.glob('0[123]_*/图表素材/*.svg'))
res=list(concurrent.futures.ThreadPoolExecutor(4).map(render,files))
(ROOT/'05_质量验收'/'render_log.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
for group in range((len(files)+9)//10):
    sheet=Image.new('RGB',(1600,1800),'#cbd5df')
    for j,p in enumerate(files[group*10:group*10+10]):
        png=p.with_suffix('.png')
        if png.exists():
            im=Image.open(png).convert('RGB');im.thumbnail((790,350));sheet.paste(im,((j%2)*800+5,(j//2)*360+5))
    sheet.save(ROOT/'05_质量验收'/f'图表联系表_{group+1}.jpg',quality=90)
print(json.dumps(res,ensure_ascii=False))
