"""Render only Part 2 SVGs. Requires Windows Chrome and Pillow.
Browser profiles and HTML diagnostics live in the OS temporary directory.
"""
from pathlib import Path
import concurrent.futures, subprocess, tempfile, json, html, re, os, hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parent
FIG=ROOT/'图表素材'
CHROME=Path(os.environ.get('PART2_CHROME',r'C:\Program Files\Google\Chrome\Application\chrome.exe'))
TMP=Path(tempfile.mkdtemp(prefix='energy_part2_'))
FLAGS=[str(CHROME),'--headless','--disable-gpu','--hide-scrollbars','--no-first-run','--no-default-browser-check','--allow-file-access-from-files','--force-device-scale-factor=1']
def render(p):
    png=p.with_suffix('.png')
    cmd=FLAGS+['--window-size=1600,900','--screenshot='+str(png),'--user-data-dir='+str(TMP/p.stem),p.as_uri()]
    run=subprocess.run(cmd,capture_output=True,timeout=60,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if run.returncode or not png.exists():raise RuntimeError(p.name+run.stderr.decode('utf8','replace')[-500:])
    with Image.open(png) as im: assert im.size==(1600,900);im.verify()
    return {'svg':p.name,'png':png.name,'size':[1600,900],
            'svg_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
            'png_sha256':hashlib.sha256(png.read_bytes()).hexdigest()}
def browser_checks():
    # Use the already-vendored Mermaid runtime without editing shared files.
    library=ROOT.parent/'05_质量验收/mermaid.min.js'
    diagrams=[{'name':p.name,'source':p.read_text(encoding='utf8')} for p in sorted(FIG.glob('P*.mmd'))]
    svgs=''.join('<div class="diagram" data-name="'+p.name+'">'+p.read_text(encoding='utf8')+'</div>' for p in sorted(FIG.glob('P*.svg')))
    script='''<script>
    const inputs=INPUTS;
    async function run(){
      await document.fonts.ready;
      const result={mermaid:[],text:[]};
      mermaid.initialize({startOnLoad:false,securityLevel:'strict'});
      for(const d of inputs){try{await mermaid.parse(d.source);result.mermaid.push({file:d.name,ok:true})}catch(e){result.mermaid.push({file:d.name,ok:false,error:String(e)})}}
      for(const d of document.querySelectorAll('.diagram')){
        for(const t of d.querySelectorAll('text')){
          const b=t.getBBox();if(b.x<0||b.y<0||b.x+b.width>1600||b.y+b.height>900)result.text.push({file:d.dataset.name,text:t.textContent,box:[b.x,b.y,b.width,b.height]});
        }
      }
      document.getElementById('result').textContent=JSON.stringify(result);
    }run();</script>'''.replace('INPUTS',json.dumps(diagrams,ensure_ascii=False).replace('</','<\\/'))
    f=TMP/'check.html';f.write_text('<meta charset="UTF-8"><script src="'+library.as_uri()+'"></script>'+svgs+'<pre id="result">pending</pre>'+script,encoding='utf8')
    run=subprocess.run(FLAGS+['--user-data-dir='+str(TMP/'check_profile'),'--virtual-time-budget=15000','--dump-dom',f.as_uri()],capture_output=True,timeout=60,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    raw=run.stdout.decode('utf8','replace');match=re.search(r'<pre id="result">(.*?)</pre>',raw,re.S)
    if not match or match[1]=='pending':raise RuntimeError('Browser validation not completed')
    data=json.loads(html.unescape(match[1]));(ROOT/'图表验证.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    assert all(x['ok'] for x in data['mermaid']),data
    assert not data['text'],data
def main():
    files=sorted(FIG.glob('P*.svg'))
    with concurrent.futures.ThreadPoolExecutor(3) as pool: records=list(pool.map(render,files))
    for group in range(2):
        canvas=Image.new('RGB',(1600,1350),'#dce5eb')
        for j,p in enumerate(files[group*5:group*5+5]):
            with Image.open(p.with_suffix('.png')) as im:
                im=im.convert('RGB');im.thumbnail((790,444));canvas.paste(im,((j%2)*800+5,(j//2)*450+3))
        canvas.save(ROOT/f'图表联系表_{group+1}.jpg',quality=92)
    (ROOT/'渲染记录.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
    browser_checks();print('Rendered 10 PNG; Mermaid parse and SVG viewport checks passed. Temp:',TMP)
if __name__=='__main__':main()
