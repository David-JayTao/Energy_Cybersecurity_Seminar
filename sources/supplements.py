import runpy,csv,json
from pathlib import Path
D=runpy.run_path(str(Path(__file__).with_name('build_materials.py')))
R=D['ROOT'];write=D['write'];box=D['box'];text=D['svgtext'];arrow=D['arrow'];lines=D['lines']
for i,(heads,rows) in D['TABLES'].items():
    folder=D['MEMBERS'][(i-1)//10][1]
    p=R/f'{folder}/图表素材/P{i:02d}_表格.csv'
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(heads+['来源']);w.writerows(row+[' '.join(D['PAGES'][i-1]['refs'])] for row in rows)
folder=D['MEMBERS'][2][1]
mmd='''flowchart TB
  subgraph PC["生产控制区"]
    I["安全I区：实时监控一次设备的业务"]
    II["安全II区：与I区紧密交互、影响较大但不直接控制的业务"]
  end
  subgraph MI["管理信息区"]
    III["安全III区：运行指挥、分析决策相关业务"]
    IV["安全IV区：其他业务"]
  end
  A["特定终端或非专用网络接入：按第6条设安全接入区"]
  A -.->|"适用条件判断，非连接许可"| PC
  NOTE["示意仅说明业务分类；通信与隔离按规定另行设计"]
'''
s='<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900"><rect width="1600" height="900" fill="white"/><g font-family="Microsoft YaHei, sans-serif">'
s+=text(60,70,'P29补充：中国电力监控系统安全分区（概念图）',34)
s+=text(60,125,'依据第27号令第4–6条；按业务功能与要求部署，不按设备名称机械归类。',25)
for x,title,labels in [(70,'生产控制区',['安全I区：实时监控一次设备','安全II区：紧密交互、影响较大但不直接控制']), (820,'管理信息区',['安全III区：运行指挥、分析决策','安全IV区：其他业务'])]:
    s+=text(x,220,title,30)
    for j,lab in enumerate(labels):s+=box(x,260+j*160,690,115,lab,size=26)
s+=box(70,650,1440,90,'特定终端或非专用网络接入：按第6条设安全接入区；并非允许任意公网直连。','#fff1df',25)
s+=text(70,805,'来源：R15。仅说明分区概念，不提供通信互联许可，不作为工程施工或合规认证依据。',23)
s+='</g></svg>'
write(folder+'/图表素材/P29_中国分区.svg',s);write(folder+'/图表素材/P29_中国分区.mmd',mmd)
for name,folder,topic in D['MEMBERS']:
    write(folder+'/图表素材/使用说明.md','''# 图表素材使用说明

SVG为可缩放矢量图，PNG为1600×900预览/插图，Mermaid为可编辑逻辑源码；同编号是同一主题的不同载体，不是新增PPT页面。表格CSV保留数值和来源编号，可导入表格或重新排版。P29另有中国分区补充图。

SVG与Mermaid允许布局详略不同，但不得改变事实和箭头含义。表格页的Mermaid只列概念节点，直接插入请使用SVG/PNG或CSV重排。建议只插入图主体，把来源和必要限定保留在页脚；不要把制作说明放到上屏页面。

图表均为本组依据所列资料重新组织的教学示意，不复制设备厂商真实网络拓扑。实线为本图解释的流程/关系，虚线为条件、研究重建或旁路监测。能源流单独标注，不是互联网流量。
''')
# 课程报告自包含书目，避免提交时丢失外链文件。
p=R/'04_全组资料/课程报告正文.md';s=p.read_text(encoding='utf-8')
if '\n## 完整书目\n' not in s:
    s+='\n## 完整书目\n\n'+'\n\n'.join(D['reftext'](i) for i in sorted(D['REFS']))
    p.write_text(s,encoding='utf-8')
# 每份独立包在正文前提供首次使用缩写的英文全称。
intro='''本包缩写首读：人工智能（Artificial Intelligence，AI）；信息技术（Information Technology，IT）；运行技术（Operational Technology，OT）；工业控制系统（Industrial Control Systems，ICS）；监控与数据采集（Supervisory Control and Data Acquisition，SCADA）；人机界面（Human–Machine Interface，HMI）；可编程逻辑控制器（Programmable Logic Controller，PLC）；远程终端单元（Remote Terminal Unit，RTU）；虚拟专用网络（Virtual Private Network，VPN）；多因素认证（Multi-Factor Authentication，MFA）；能源管理系统（Energy Management System，EMS）；电池管理系统（Battery Management System，BMS）；分布式能源资源（Distributed Energy Resources，DER）；机器学习（Machine Learning，ML）；深度神经网络（Deep Neural Network，DNN）；支持向量机（Support Vector Machine，SVM）；安全水处理试验台（Secure Water Treatment，SWaT）。此段是阅读准备，不计入演讲稿。\n\n'''
for name,folder,topic in D['MEMBERS']:
    for filename in ['PPT逐页完整内容.md','完整演讲逐字稿.md']:
        p=R/folder/filename;s=p.read_text(encoding='utf-8')
        if '本包缩写首读' not in s:
            pos=s.index('\n\n')+2;s=s[:pos]+intro+s[pos:];p.write_text(s,encoding='utf-8')
print('supplements complete')
