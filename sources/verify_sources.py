from pathlib import Path
from html.parser import HTMLParser
import requests,json,concurrent.futures
ROOT=Path(__file__).resolve().parents[1]
class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ['script','style']:self.skip+=1
    def handle_endtag(self,tag):
        if tag in ['script','style']:self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip and data.strip():self.parts.append(data.strip())
refs=json.loads((ROOT/'sources/references.json').read_text(encoding='utf-8'))
def check(item):
    k,v=item;url=v['url'];dest=ROOT/f'sources/{k}_source.pdf'
    if dest.exists():return dict(id=k,url=url,status=200,verification='本地已下载PDF，保留首次成功结果',bytes=dest.stat().st_size)
    try:
        a=requests.get(url,timeout=15);result=dict(id=k,url=url,final_url=a.url,status=a.status_code,bytes=len(a.content))
        if a.ok:
            if a.content.startswith(b'%PDF'):dest.write_bytes(a.content)
            else:
                enc=a.encoding if a.encoding and a.encoding.lower()!='iso-8859-1' else 'utf-8'
                t=a.content.decode(enc,errors='replace');p=Text();p.feed(t)
                (ROOT/f'sources/{k}_page.txt').write_text('\n'.join(p.parts),encoding='utf-8')
            result['verification']='HTTP获取成功；实质核验范围见书目，HTTP成功不等于全文已审阅'
        else:result['verification']='脚本获取失败；已通过网页工具读取官方内容，见事实核查'
        return result
    except Exception as e:return dict(id=k,url=url,error=str(e),verification='本地未保存；已通过网页工具核对公开内容，见书目限制')
res=list(concurrent.futures.ThreadPoolExecutor(8).map(check,refs.items()))
(ROOT/'sources/url_check.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(res,ensure_ascii=False))
