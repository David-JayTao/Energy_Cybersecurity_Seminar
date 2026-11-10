"""Generate Part 2 teaching diagrams, editable relations and data tables only."""
from pathlib import Path
from html import escape
import json, csv
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'图表素材'
PAGES=json.loads((ROOT/'page_data.json').read_text(encoding='utf8'))
INK='#173044'; BLUE='#246ca6'; ORANGE='#b95822'; GREEN='#16826c'; GRAY='#637383'
PALE='#eef4f8'; BG='#fafcfd'; RED='#b43a42'

class SVG:
    def __init__(self,n,subtitle):
        p=PAGES[n-11];self.n=n
        self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900"><title>P{n} {escape(p["title"])}</title><desc>{escape(p["figure"])}</desc>',
        '<defs>'+''.join(f'<marker id="{k}" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L8 4 L0 8Z" fill="{c}"/></marker>' for k,c in [('blue',BLUE),('orange',ORANGE),('green',GREEN),('gray',GRAY),('red',RED)])+'</defs>',
        f'<rect width="1600" height="900" fill="{BG}"/>',
        '<style>text{font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif} .body{font-size:26px}</style>']
        self.text(64,55,'能源 × 网络安全  /  刘酝潇  /  P'+str(n),20,GRAY)
        self.text(64,115,p['title'],38,INK,True)
        self.text(64,160,subtitle,24,GRAY)
        self.line(64,812,1536,812,GRAY,1)
        self.text(64,848,'来源：'+ ' / '.join(p['refs'])+'  ·  完整定位见逐页文案与本部分书目',20,GRAY)
        self.text(64,879,'2026-11-10  ·  本组重绘；图中比例不代表时间、概率或电气容量',18,GRAY)
    def text(self,x,y,text,size=26,color=INK,bold=False,anchor='start'):
        for i,t in enumerate(text.split('\n')):
            self.s.append(f'<text x="{x}" y="{y+i*size*1.45}" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{escape(t)}</text>')
    def rect(self,x,y,w,h,fill=PALE,stroke='#d3dfe6',dash=False):
        self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2"'+(' stroke-dasharray="10 7"' if dash else '')+'/>')
    def box(self,x,y,w,h,title,body='',color=BLUE,fill='white'):
        self.rect(x,y,w,h,fill,color)
        self.text(x+22,y+43,title,27,color,True)
        if body:self.text(x+22,y+86,body,24,INK)
    def line(self,x1,y1,x2,y2,color=BLUE,width=3,dash=False,arrow=False):
        k={BLUE:'blue',ORANGE:'orange',GREEN:'green',GRAY:'gray',RED:'red'}.get(color,'blue')
        self.s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="10 7"' if dash else '')+(f' marker-end="url(#{k})"' if arrow else '')+'/>')
    def path(self,d,color=BLUE,dash=False,arrow=True,width=3):
        k={BLUE:'blue',ORANGE:'orange',GREEN:'green',GRAY:'gray',RED:'red'}[color]
        self.s.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="10 7"' if dash else '')+(f' marker-end="url(#{k})"' if arrow else '')+'/>')
    def note(self,text,y=761,color=GRAY):self.text(64,y,text,23,color)
    def save(self):
        (OUT/f'P{self.n}.svg').write_text('\n'.join(self.s+['</svg>']),encoding='utf8')

def diagrams():
    s=SVG(11,'比较改变运行状态的环节，避免从“停电／停运”直接反推攻击方式')
    for y,label,c,items in [(265,'2015 乌克兰｜直接控制影响',BLUE,[('取得控制能力','来自入侵与远程访问'),('非授权控制操作','攻击者使用已有接口'),('断路器动作','现场电气连接改变'),('局部配电中断','影响范围受工况约束')]),(535,'2021 Colonial｜间接运行影响',ORANGE,[('IT业务系统勒索','攻击最先确认在IT侧'),('安全范围不确定','需要隔离、遏制攻击'),('运营方停运决定','由企业停止运行'),('燃料运输受限','供应恢复涉及物流')])]:
        s.text(64,y-35,label,28,c,True)
        for i,(t,b) in enumerate(items):
            x=64+i*380;s.box(x,y,332,142,t,b,c)
            if i<3:s.line(x+332,y+70,x+375,y+70,c,3,arrow=True)
    s.note('两条路径为所选案例的主要机制；并非所有能源安全事件的穷尽分类。');s.save()

    s=SVG(12,'事件规模与口径｜不把客户换成人数，不把区域配电中断扩大全国')
    for x,y,w,title,b in [(64,225,720,'2015年12月23日','事件发生日期；调查公开日期另算'),(816,225,720,'3家区域配电企业','配电服务区域受影响'),(64,405,720,'约225,000个客户','客户账户口径；不能换算居民人数'),(816,405,720,'约1–6小时','不同受影响区域的停电时长范围')]:s.box(x,y,w,150,title,b)
    s.box(64,606,1472,110,'供电恢复后，自动化运行仍受限制','停电时长与控制环境修复时长，是不同指标',ORANGE)
    s.note('数据据R02与R03；R03引用R02等资料，两者不是完全独立的取证来源。');s.save()

    s=SVG(13,'功能关系教学示意｜不是2015年某家企业的现场拓扑，也不是国内工程合规方案')
    s.rect(64,215,290,480,'#f2f5f7');s.text(86,255,'业务网络（IT）',27,INK,True)
    s.box(86,300,246,155,'办公与业务系统','邮件、文档、管理\n不直接等于设备控制')
    s.rect(405,215,520,480,'#edf5fc');s.text(427,255,'控制中心（OT）',27,INK,True)
    s.box(430,300,470,110,'HMI：人机界面','运行人员查看状态、提出操作')
    s.box(430,490,470,140,'SCADA控制与采集功能','组织控制请求与现场数据\nHMI是其交互部分')
    s.line(530,410,530,488,ORANGE,3,arrow=True);s.text(548,452,'操作',22,ORANGE)
    s.line(800,490,800,412,BLUE,3,arrow=True);s.text(816,452,'显示',22,BLUE)
    s.line(380,205,380,710,GRAY,2,True);s.text(70,654,'受控接入：身份、对象、权限',21,GRAY)
    s.line(332,375,428,375,GRAY,3,True,True)
    s.text(84,505,'边界不是随意互通',23,GRAY)
    s.rect(1000,215,536,480,'#edf7f3');s.text(1022,255,'站内与现场设备',27,INK,True)
    s.box(1050,310,430,115,'RTU等现场终端','连接设备信号与执行回路',GREEN)
    s.box(1130,515,270,100,'断路器','改变电路通断',GREEN)
    s.path('M 900 525 H 966 V 340 H 1048',ORANGE);s.text(915,310,'控制 →',20,ORANGE)
    s.path('M 1050 395 H 982 V 590 H 902',BLUE);s.text(925,632,'← 反馈',20,BLUE)
    s.line(1175,425,1175,513,ORANGE,3,arrow=True);s.text(1030,475,'执行',22,ORANGE)
    s.line(1350,515,1350,427,BLUE,3,arrow=True);s.text(1380,475,'状态',22,BLUE)
    s.line(1040,560,1130,560,GREEN,7);s.line(1400,560,1510,560,GREEN,7)
    s.text(1022,655,'电源侧 ━ 电气线路 ━ 下游负荷',23,GREEN)
    s.note('橙色箭头：控制／操作　蓝色箭头：状态／量测　绿色粗线：电气连接　灰色虚线：边界／受控接入');s.save()

    s=SVG(14,'按报告归纳共同机制｜访问方式存在差异，不把多家企业拼成同一取证链')
    s.rect(64,215,700,360,'#edf5fc',BLUE,True);s.text(86,255,'研究归纳：如何获得运行环境访问',27,BLUE,True)
    for x,t,b in [(86,'业务网络立足','钓鱼等入侵活动\n非每步均有公开日志'),(446,'凭据与远程访问','利用已有接入能力\n账号权限限制范围')]:s.box(x,310,292,180,t,b)
    s.line(378,397,444,397,BLUE,3,True,True)
    s.rect(816,215,720,360,'#fff4ed',ORANGE);s.text(838,255,'报告支持：实际控制行为与后果',27,ORANGE,True)
    s.box(838,310,300,180,'现有控制软件／HMI','攻击者执行\n非授权控制操作',ORANGE)
    s.box(1196,310,315,180,'开关动作与停电','现场状态发生改变\n供电路径受到影响',ORANGE)
    s.line(764,397,836,397,BLUE,3,True,True);s.line(1138,397,1194,397,ORANGE,3,arrow=True)
    s.box(64,625,1472,100,'能连通 ≠ 能操作；功能正常 ≠ 该次操作获得合法授权','逐项核实：网络可达范围、身份与会话、目标对象及操作能力',GRAY)
    s.note('虚线：研究重建与跨域关系；实线：报告支持的控制过程。未绘制具体漏洞、协议字段或设备型号。');s.save()

    s=SVG(15,'简化径向供电教学例子｜前提：下游负荷没有其他已投入的有效电源')
    def circuit(y,opened):
        s.text(64,y-90,'分闸后：该通路断开' if opened else '合闸时：该通路连续',28,ORANGE if opened else GREEN,True)
        s.box(64,y-52,230,110,'电源侧','上级供电',GREEN)
        s.box(1070,y-52,300,110,'下游负荷','失去该电源' if opened else '经该路径受电',ORANGE if opened else GREEN)
        c=GRAY if opened else GREEN
        s.line(294,y,600,y,c,7);s.line(720,y,1070,y,c,7)
        for x in [600,720]:s.s.append(f'<circle cx="{x}" cy="{y}" r="7" fill="white" stroke="{c}" stroke-width="3"/>')
        s.line(600,y,702 if opened else 720,y-44 if opened else y,ORANGE if opened else GREEN,6)
        s.text(575,y+65,'断路器',24,INK)
        s.text(790,y-24,'电气线路',22,c)
    circuit(330,False);circuit(590,True)
    s.text(480,205,'控制系统 → 现场终端 → 执行回路 → 分闸动作',24,ORANGE)
    s.line(650,410,650,495,ORANGE,3,arrow=True);s.text(680,460,'状态改变',23,ORANGE)
    s.path('M 1370 590 H 1495 V 440',GRAY,True,False);s.text(1285,410,'备用路径未投入',23,GRAY)
    s.note('能否转供取决于备用路径、容量与安全操作条件；保护和联锁不能默认识别所有非授权分闸。',746)
    s.note('绿色／灰色粗线是电气连接，不是通信流量；本图不推算2015年的停电规模。',783);s.save()

    s=SVG(16,'事件报告中的不同作用｜不同企业的破坏细节不合并为同一站点的完整经历')
    for x,t,b,c in [(64,'造成供电中断','控制操作 → 开关动作\n供电路径被切断',ORANGE),(566,'妨碍远程恢复','主机与部分通信设备受损\n远程工具难以继续使用',BLUE),(1068,'影响客户联系','电话服务受到干扰\n不是分闸的必要步骤',GRAY)]:s.box(x,220,468,155,t,b,c)
    s.text(64,430,'恢复进程：终点不同，不绘制未经证实的持续时间比例',26,INK,True)
    s.box(64,475,620,140,'供电服务恢复〔报告事实〕','人工等方式恢复送电\n依赖人员、现场操作及通信条件',GREEN)
    s.box(824,475,712,140,'控制能力恢复〔报告事实＋本组启示〕','供电恢复后，自动化仍受限制〔事实〕\n需重建账号、配置、通信并核验〔启示〕',BLUE)
    # Separate cause and recovery panels without crossing the section heading.
    s.rect(64,670,1472,58,'#fff4ed',ORANGE);s.text(88,708,'恢复送电不证明远程控制已经可信；人工恢复也必须满足现场安全条件。',25,ORANGE,True)
    s.note('固件破坏、主机擦除与电话干扰分开叙述，不把KillDisk写成所有破坏行为的统一名称。');s.save()

    s=SVG(17,'本组工程分析｜三个观察方向分别解释作用范围、供电后果和恢复速度')
    for y,t,a,b in [(235,'操作权限','只能查看／可操作单站／可操作多站','决定可能被改变的对象范围'),(410,'供电条件','负荷位置、备用路径、可转供容量','影响实际失电范围与持续时间'),(585,'恢复能力','可信通信、现场人员、可用操作工具','影响发现、处置与恢复速度')]:
        s.box(64,y,310,132,t,'需按具体系统核实')
        s.box(430,y,640,132,a,'不同条件可能改变同一异常操作的后果',GRAY)
        s.box(1130,y,406,132,'观察结果',b,GREEN)
        s.line(374,y+65,428,y+65,BLUE,3,arrow=True);s.line(1070,y+65,1128,y+65,GRAY,3,arrow=True)
    s.note('不提供虚构概率或评分；入侵范围、停电范围、停电时长不能相互替代。');s.save()

    s=SVG(18,'具名证词中的处置依据｜不画攻击者到泵阀的控制箭头')
    items=[('IT业务系统勒索','5月7日发现'),('起点与范围不确定','担心威胁扩展至OT'),('运营方隔离、停运','安全处置决定'),('燃料运输受限','实际能源业务影响')]
    for i,(t,b) in enumerate(items):
        x=64+i*380;s.box(x,265,332,155,t,b,ORANGE)
        if i<3:s.line(x+332,342,x+377,342,ORANGE,3,arrow=True)
    s.text(64,505,'运行重启与终端供应是不同进程',28,INK,True)
    for x,t,b in [(64,'5月7日','停运并开始处置'),(566,'5月12日晚','开始恢复管道服务'),(1068,'此后逐步恢复供应','依赖运输、库存和替代来源')]:s.box(x,555,468,145,t,b,BLUE)
    s.line(532,626,564,626,BLUE,3,arrow=True);s.line(1034,626,1066,626,BLUE,3,arrow=True)
    s.note('公开证据不支持攻击者直接操纵泵阀；这也不等于证明OT完全不受运行影响。');s.save()

    s=SVG(19,'按主要机制比较｜实际事件可兼有控制异常与主动停运，表格不是穷尽分类')
    rows=[('初始与进入','业务网络入侵、凭据与远程访问','业务IT系统受到勒索'),('改变运行的主体','攻击者实施非授权控制操作','运营方下达停运决定'),('关键连接环节','已有控制功能 → 现场开关动作','范围不确定 → 隔离、遏制攻击'),('已确认的结果','约225,000客户配电中断','管道停运、燃料运输受限'),('恢复需要区分','恢复送电／恢复可信远程控制','管道开始重启／终端供应恢复')]
    s.rect(64,215,1472,65,INK,INK);s.text(86,258,'比较维度',27,'white',True);s.text(390,258,'2015 乌克兰',27,'white',True);s.text(980,258,'2021 Colonial',27,'white',True)
    for i,(a,b,c) in enumerate(rows):
        y=280+i*85;s.rect(64,y,1472,85,'white' if i%2 else PALE,'#d3dfe6');s.text(86,y+50,a,25,INK,True);s.text(390,y+50,b,24,BLUE);s.text(980,y+50,c,24,ORANGE)
    s.note('取证重点：前者查操作和设备反馈，后者查决策依据与运行依赖。',765);s.save()

    s=SVG(20,'本组提出的问题｜第三部分据此选择可解释、可验证的技术')
    s.box(64,235,710,400,'怎样识别不当操作？','账号与会话：谁在用？\n对象与权限：能操作哪里？\n运行授权：这次操作该不该发生？\n设备反馈：现场结果是否符合预期？',BLUE)
    s.box(826,235,710,400,'怎样支撑可靠恢复？','受影响范围：哪些能力还可信？\n运行选择：继续、降级还是停运？\n恢复条件：账号、配置、通信、现场\n重启验证：先证明能够安全运行',ORANGE)
    s.rect(64,676,1472,66,'#edf7f3',GREEN);s.text(88,718,'验证方向：可追溯的异常证据　＋　可信的现场状态　＋　实际恢复演练',27,GREEN,True)
    s.note('建议来自案例分析；不作“某项技术当年部署就一定能阻止事件”的保证。',785);s.save()

MMD={
11:'A[2015：取得控制能力] --> B[攻击者非授权控制操作] --> C[开关动作] --> D[局部配电中断]\nE[2021：IT勒索] --> F[范围不确定] --> G[运营方停运决定] --> H[燃料运输受限]',
12:'A[2015年12月23日] --- B[3家区域配电企业]\nB --- C[约225000客户]\nC --- D[不同区域约1至6小时]\nD --- E[供电恢复后自动化仍受限制]\nN[并列事实：连接线不表示因果或时间比例]',
13:'subgraph IT[业务网络]\n A[办公与业务系统]\nend\nsubgraph OT[控制中心]\n B[HMI：运行人员交互界面]\n C[SCADA控制与数据采集功能]\n B -->|操作| C\n C -->|状态显示| B\nend\nsubgraph FIELD[现场]\n D[RTU等现场终端]\n E[断路器执行回路与状态信号]\n F[电源侧]\n G[下游负荷]\n D -->|控制| E\n E -->|反馈| D\n F ---|电气连接| E\n E ---|电气连接| G\nend\n A -.->|边界：受控接入，不等于可操作| B\n C -->|控制请求| D\n D -->|状态和量测| C\n N[教学示意：不是2015现场拓扑]',
14:'subgraph RESEARCH[研究归纳：具体访问方式有差异]\n A[业务网络立足] -.-> B[获取凭据]\n B -.-> C[远程接入运行环境]\nend\n C -.->|实际操作能力需核实| D[使用已有控制软件与HMI]\n D --> E[非授权开关操作]\n E --> F[现场设备状态变化]\n F -->|具体供电条件| G[局部配电中断]\n N[正常功能不等于该次操作获得合法授权]',
15:'A[控制请求] --> B[现场终端与执行回路]\n B --> C[断路器由合闸变分闸]\n C --> D[一条电气通路断开]\n D --> E{存在可投入的替代供电吗}\n E -->|没有| F[下游失去该电源]\n E -->|可能有| G[核验容量与安全操作条件]\n G --> H[满足条件后才可转供]\n N[教学例子：不推算2015各站实际影响]',
16:'A[非授权控制操作] --> B[开关动作与供电中断]\n C[主机与部分通信设备受损] --> D[远程恢复受阻]\n E[电话服务干扰] --> F[客户联系受阻]\n B --> G[人工等方式恢复供电：事实]\n D --> H[供电恢复后自动化仍受限：事实]\n H -.-> I[核验账号配置通信与现场：本组启示]\n N[不同企业细节不合并为单站完整过程]',
17:'A[实际操作权限] --> B[可影响对象范围]\n C[负荷与备用路径] --> D[实际失电范围]\n E[通信人员与工具] --> F[恢复速度]\n B -.-> G[共同分析具体后果]\n D -.-> G\n F -.-> G\n N[本组分析：不打虚构分数]',
18:'A[5月7日发现IT勒索] --> B[起点与范围不确定]\n B --> C[运营方决定隔离与停运]\n C --> D[燃料运输受限]\n C --> E[排查并确认运行安全]\n E --> F[5月12日晚开始恢复服务]\n F --> G[运输库存与替代来源影响供应恢复]\n N[没有证据支持攻击者直接操纵泵阀]',
19:'A[2015：非授权控制] --> B[开关动作] --> C[配电中断]\n D[核查操作与设备反馈] -.-> B\n E[2021：IT勒索] --> F[运营方停运] --> G[运输受限]\n H[核查决策依据与运行依赖] -.-> F\n N[两类主要机制；可能在复杂事件中并存]',
20:'A[不当操作识别] --> B[核对身份对象与授权]\n B --> C[核对现场反馈]\n C --> D[形成可追溯异常证据]\n E[可靠恢复] --> F[确认哪些能力可信]\n F --> G[选择降级停运或重启]\n G --> H[实际演练与运行验证]\n N[本组需求；具体技术与效果由第三部分论证]'
}
def tables():
    rows={11:[['案例','改变运行主体','主要路径','来源'],['2015乌克兰','攻击者','非授权控制操作—开关动作—停电','R02'],['2021Colonial','运营方','IT勒索—处置停运—运输受限','R07']],
    12:[['指标','值','单位或口径','来源'],['日期','2015-12-23','事件发生日期','R02/R03'],['企业','3','区域配电企业','R03'],['影响','225000','约，客户，非居民人数','R02/R03'],['持续时间','1–6','小时，不同区域范围','R03']],
    19:[['维度','2015乌克兰','2021Colonial','来源'],['主体','攻击者非授权操作','运营方停运决定','R02/R07'],['关键环节','控制功能到开关动作','IT事件到隔离停运','R02/R07'],['后果','局部配电中断','燃料运输受限','R02/R07/R08'],['恢复','供电与可信远控分别恢复','管道重启与终端供应有时间差','R02/R07/R08']],
    20:[['待解决问题','观察依据','验证方向','性质'],['识别不当操作','正常控制功能被滥用','身份授权与设备反馈可追溯','本组推论'],['支撑可靠恢复','远控受阻与安全停运','现场可信状态与恢复演练','本组推论']]}
    for n,rs in rows.items():
        with (OUT/f'P{n}_表格.csv').open('w',encoding='utf-8-sig',newline='') as f:csv.writer(f).writerows(rs)

if __name__=='__main__':
    diagrams();tables()
    for n,s in MMD.items(): (OUT/f'P{n}.mmd').write_text('flowchart LR\n'+s+'\n',encoding='utf8')
    print('Generated 10 SVG, 10 Mermaid, 4 CSV')
