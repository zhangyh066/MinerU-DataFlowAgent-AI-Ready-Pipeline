# MinerU_json_算法交易的市场影响_稳定与信息效率的双重视角_岳崴_pdf_90f180da-b716-4e73

- 质量判定：YES
- 评分：93
- 理由：该论文采用多种计量方法研究算法交易对A股市场稳定性和信息效率的双重影响，变量定义清晰，样本明确，结果详细，学术贡献明确。

## 摘要

本文利用2015-2023年中国A股市场的高频交易数据和订单簿数据，构建算法交易强度指标，探讨了算法交易对股票市场稳定与信息效率的双重影响。研究发现，算法交易改善了市场流动性并抑制了价格波动，提升了市场稳定；然而，算法交易通过挤出知情交易者和卖空交易者，延缓了市场对新信息的吸收过程，降低了信息效率。上述双重影响在非国有、中小规模及信息披露质量较低的上市公司中更为显著。此外，算法交易在市场异动期间通过更强的流动性支持和波动抑制增强了市场稳定，但与此同时通过降低价格信息含量和信息反应速度导致了更显著的市场信息效率下降。本文研究对强化算法交易透明度管理、构建算法交易市场稳定性监管框架和加强市场信息效率保护具有一定启示。

## 正文

算法交易的市场影响:
稳定与信息效率的双重视角
岳崴屈建文李子潇刘悦
(湖南大学金融与统计学院,湖南长沙410006)
摘要:本文利用2015-2023年我国A股市场的高频交易数据和订单簿数据,构建算法交易
强度指标,探讨了算法交易对股票市场稳定与信息效率的双重影响。研究发现,算法交易改善了
市场流动性并抑制了价格波动,提升了市场稳定;然而,算法交易通过挤出知情交易者和卖空交易
者,延缓了市场对新信息的吸收过程,降低了信息效率。上述双重影响在非国有、中小规模及信息
披露质量较低的上市公司中更为显著。此外,算法交易对流动性共性风险影响有限;在市场异动
期间,算法交易通过更强的流动性支持和波动抑制增强了市场稳定,但与此同时通过降低价格信
息含量和信息反应速度导致了更显著的市场信息效率下降;算法交易显示出对股市“好波动”与
“坏波动"的非对称抑制效应。本文研究对强化算法交易透明度管理、构建算法交易市场稳定性监
管框架和加强市场信息效率保护具有一定后示。
关键词:算法交易;市场稳定;信息效率;流动性风险;价格波动
JEL分类号:G10,G12,G14 文献标识码:A 文章编号:1002-7246(2025)12-0133-18
一、引言
人工智能技术与资本市场的融合发展带来了金融资产交易方式的深刻变革,算法交
易(Algorithmic Trading,AT)正是这场变革的重要体现。算法交易是指利用计算机算法进
行自动交易决策、发送订单并管理订单的交易技术,包含组合选择、交易策略、执行策略等
内容(王宇超等,2014;Hendershott et al.,2011)。目前,算法交易已经成为全球资本市
场的重要交易方式,在一些成熟市场中,其交易占比已超过50 \%。尽管我国算法交易起
步相对较晚,但近年来发展迅速,当前A股市场仅程序化算法交易金额就占市场总成交
额的2 9 \%1。
2024年4月,国务院出台《关于加强监管防范风险推动资本市场高质量发展的若干
意见)“新国九条”),明确要求制定程序化交易监管规定,加强对高频量化交易监管。同
年5月,证监会印发《证券市场程序化交易管理规定(试行)》,从制度层面构建了算法交
易监管的总体框架。围绕金融工作的政治性、人民性,践行金融为民的理念,如何进一步
保护我国股市中广大中小散户的合法权益,坚持“趋利避害、突出公平、有效监管、规范发
展”的思路完善算法交易监管规则体系,需要结合我国资本市场的实际,对算法交易的市
场影响及作用机制进行深入的理论和实证研究。
然而,尽管理论上算法交易在提高交易效率、降低交易成本和减少人为错误和行为偏
差等方面具有潜在优势,但现有实证研究显示,算法交易的市场影响并不明确。一方面,
算法交易通过频繁报价和交易活动,不仅发挥了做市商功能,还促进了信息的快速传播,
降低了信息不对称导致的逆向选择成本,从而为市场参与者带来交易成本降低和风险缓
释的双重收益(Boehmer etal.,2021;Yuferova,2024)。另一方面,算法交易在宏观和微
观层面都可能带来潜在风险。从宏观视角来看,算法同质化和交易策略趋同可能加剧市
场波动,在极端条件下威胁市场稳定(Cartea et al.,2019;Leal and Napoletano,2019)。
此类趋同策略形成的“反馈循环”效应,可能降低市场流动性,扰乱价格发现机制。从微
观视角来看,算法交易投资者相对于散户投资者的技术、信息和速度优势可能影响资本市
场的“公开、公平、公正"秩序。研究还发现,算法交易投资者之间的“延迟套利竞赛”频繁
且激烈,导致显著的价格冲击、流动性损耗和高额交易成本(Aquilina et al.,2022)。
囿于A股市场高频交易数据和详细订单簿数据可得性有限,且算法交易在我国起步
相对较晚,目前我国关于算法交易市场影响的研究较少。在实证研究方面,多数文献或是
从单一维度关注算法交易的市场效应(韦立坚等,2022;张小日等,2024),或是通过模
拟仿真实验探讨算法交易的作用机制(王宇超等,2014),较少关注算法交易对市场稳定
和信息效率的双重影响。此外,现有研究多从公司特征与制度(张路等,2021;陈海强
等,2023)、市场制度(李松楠等,2023;赵家悦等,2024;陈海强等,2024)等视角考察上
述因素对资本市场稳定和信息效率的影响,而证券交易方式本身对市场的作用尚未得到
充分探讨。为此,本文拟考察算法交易对股票市场稳定与信息效率的双重影响,以期为相
关研究提供新的经验证据。
本文的主要发现如下:第一,算法交易能够缩小买卖价差,降低价格极差与已实现波
动率,通过提升流动性并抑制价格波动,增强市场稳定性。第二,算法交易降低了知情交
易强度和卖空强度,通过挤出传统知情交易者和卖空交易者,降低了市场信息效率。第
三,在市场异动期间,算法交易通过更强的流动性支持和价格波动抑制,提升了市场的稳
定性;但同时降低了市场的信息含量与信息反应速度,导致了更显著的信息效率下降。第
四,算法交易对于个股的流动性共性风险影响并不显著,表明其并未增加流动性共性风险。
第五,算法交易展现出对股市“好波动”与“坏波动"的非对称抑制效应,即相较于正面信息
引发的“好波动”,算法交易在应对负面信息引发的“坏波动"时表现出较弱的稳定作用。
此外,本文还从公司所有权性质、规模和信息披露质量等方面,分析了算法交易对市
场稳定和信息效率的差异性影响。研究发现,对于非国有、中小规模和信息披露质量较低
的上市公司,算法交易在提升市场稳定性的同时,对信息效率的抑制效应更为显著。这表
明,这些上市公司受益于算法交易带来的市场稳定提升,但也承受了信息效率下降的代
价。因此,对算法交易的评估需综合考虑其对市场稳定和信息效率的双重影响,在发挥其
市场稳定功能的同时,通过优化信息环境降低其对信息效率的负面冲击。据此,本文提出
强化算法交易透明度管理、构建算法交易市场稳定性监管框架和加强市场信息效率监测
与保护等政策建议。
本文的贡献主要有以下两点:(1)以往的研究显示,算法交易在欧美成熟资本市场提
升了市场信息效率(Brogaard etal.,2014;Yuferova,2024),但加剧了市场波动,在极端情
况下导致市场流动性迅速枯竭,从而威胁市场稳定(Lealand Napoletano,2019;Cartea et
al.,2019;Baldauf and Mollner,2020)。本文则发现,在中国资本市场中,算法交易在增
强流动性、抑制波动从而提升市场稳定性的同时,降低了信息效率。这一结论为理解算法
交易的市场影响提供了新的实证依据,也为构建更具针对性的监管规则提供了量化参考。
(2)本文拓展了证券交易模式影响资本市场的相关研究。现有文献多聚焦于公司特征、
制度环境或市场机制对资本市场的影响,本文则着眼于算法交易这一人工智能驱动的交
易方式,系统考察其对市场稳定与信息效率的双重作用,为理解人工智能技术在资本市场
中的实际效果提供了新的视角。
二、理论分析与研究假设
(一)算法交易与市场流动性
现有研究关于算法交易对市场流动性影响的实证结论尚未达成一致。一方面,从流
动性供给视角来看,算法交易的优势主要体现在其信息处理能力和交易执行速度上,通过
即时调整报价(Hasbrouck and Saar,2013)和履行做市职责(Brogaard et al.,2018),有效
提升市场流动性。具体而言,算法交易通过实时分析市场基本面、订单流以及跨市场价格
变动等信息,实现精准的报价优化,进而缩小买卖价差。当市场面临外部冲击时,算法交
易基于智能订单拆分策略和动态限价订单调整,将大额订单分解为多个小额订单,并在不
同价格水平上进行分散化执行,避免了订单过度集中对市场造成的冲击,通过增加订单簿
深度为市场提供了额外的流动性缓冲(Menkveld,2013),有效抑制了投资者非理性行为
导致的流动性枯竭风险。我国算法交易的流动性供给机制上与成熟市场有所差异。A股
市场散户虽仅持有约20 \%的市值,却贡献了81 \%的交易量(Jones etal.,2025),其情绪化
交易行为频繁产生冲击性订单。与欧美市场较广泛采用暗池交易不同,A股市场的算法
交易多采用被动执行策略,通过分拆大额订单、动态调整执行节奏,吸收散户冲击性订单,
降低价格滑点,从而提升交易执行效率。此外,A股市场ETF与股指期货之间的套利机
会为算法交易提供了重要交易场景(王良等,2018)。算法交易者通过持续监测基差,动
态调整报价和限价订单,促进ETF等大宗交易执行,同时在流动性撤回时提供限价订单,
补充市场深度(吴偎立和常峰源,2021)。综合以上分析,提出以下研究假设:
Hla:算法交易通过即时调整报价以及执行被动做市策略,提升了市场流动性。
然而,另一方面,算法交易对市场流动性的积极作用可能在市场波动性加剧时期被削
弱,在极端条件下甚至导致流动性急剧萎缩。这种不稳定性主要源于算法交易者在面临
信息不对称和逆向选择风险时的策略调整(Brogaard etal.,2018)。在我国股市中,散户
投资者信息处理与风险应对能力相对有限,客观上加剧了市场的信息不对称。当知情交
易者利用信息优势发起定向交易时,算法交易者通过订单流分析识别潜在风险,往往会迅
速从流动性提供者转变为流动性消耗者(Easley etal.,2011)。这一角色转换导致大量
同方向订单集中涌入,产生显著的信息溢出效应,即知情交易的信号通过订单流扩散,引
发其他交易者跟随行动。随着提供流动性的交易者集体撤单,市场买卖价差迅速扩大,交
易成本随之上升。散户投资者因缺乏信息优势,往往盲目跟风,进一步加剧订单簿失衡。
Carrion(2013)的研究指出,算法交易者的流动性供给行为具有显著的顺周期特征,这种
不确定性加剧了市场脆弱性。基于以上分析,提出以下竞争性假设:
H1b:算法交易通过切换流动性供需角色并放大流动性溢出风险,降低市场流动性。
(二)算法交易与市场价格稳定
算法交易主要通过下述两种渠道增强市场价格的稳定性:一是通过流动性供给抑制
短期价格波动,二是通过高效信息处理推动价格回归基本面价值。一方面,算法交易通过
持续提供流动性,降低由噪声交易引发的短期价格波动。通过实时监测和分析市场数据,
算法交易系统能够迅速识别由市场情绪、传闻等非基本面因素引发的异常价格波动。此
外,算法交易者通过被动做市策略和统计套利策略,在持续提供流动性的同时,抑制了市
场对临时信息的过度反应,进而降低了价格的短期波动性。另一方面,算法交易依托高频
数据处理与复杂决策算法,识别和提取市场中潜在的有效信息,及时纠正由信息不对称或
市场噪声引发的价格偏差,从而抑制由信息不对称或非理性行为引发的价格过度波动
(Hasbrouck and Saar,2013)。
然而,在极端市场条件下,尤其是在信息过度反应和羊群效应显著的情境下,算法交
易可能成为加剧市场短期波动,威胁市场稳定的催化剂。尽管算法交易者在信息获取和
处理能力方面较传统交易者具有明显优势,其往往基于相同的市场微观信号执行高度趋
同的交易策略,这种现象被称为“算法羊群效应”。Lealand Napoletano(2019)研究表明,
这种群体性行为会导致大量订单的集中撤回或减少,放大市场的短期情绪波动。当市场
情绪达到极端水平时,算法交易者迅速平仓,实现短期价格操纵。当市场出现持续下跌
时,算法交易者因无法在当日反向平仓,需等待下一交易日操作,容易引发连续多日的被
动抛压,加剧价格下行和市场波动。基于以上分析,提出以下竞争性假设:
\mathrm { H } 2 \mathrm { a }:算法交易通过流动性供给以及高效的信息处理,抑制了市场价格波动。
H2b:算法交易通过引发算法羊群效应以及操纵短期价格,加剧市场价格波动。
(三)算法交易与市场信息效率
市场信息效率是指市场中资产价格能够迅速且准确地反映所有相关信息的程度,是
衡量市场是否有效的核心标准之一。算法交易对市场信息效率产生了两方面影响:一方
面,算法交易显著提升市场对公开信息的反应速度,促进价格信息含量的提高;另一方面,
其对短期价格信号的过度关注可能延缓价格对长期基本面信息的反映,从而降低长期信
息效率。
算法交易者的信息监控和调整订单报价的边际成本极低,这种独特的信息处理优势
使算法交易者能够持续追踪市场信号,并在信息变化时即时调整交易策略,从而显著提升
市场价格的信息效率。算法交易者通过直接接入交易所数据流,能够同时处理多源异构
信息,并结合历史数据和实时市场状态进行综合评估,自动执行交易决策。该过程有效降
低了市场中的信息不对称和逆向选择成本,显著缩短了信息从产生到反映在市场价格上
的时间滞后,从而加速了新信息的市场融入过程(Yuferova,2024)。Brogaard et al.
(2014)研究发现,算法交易者能够根据信息的不同性质采取差异化策略,帮助市场价格
快速恢复正常。综合以上分析,提出以下研究假设:
H3a:算法交易通过处理异构信息,缩短信息处理滞后时间,从而提升市场信息效率。
然而,尽管算法交易策略在提供市场流动性和平滑短期波动方面具有优势,但其对短
期价格变化的关注往往超过了对公司基本面信息的考量,提高传统基本面交易者面临的
信息不对称和逆向选择成本,干扰信息的真实反映(Hasbrouck and Saar,2013)。这种机
制可能导致市场对长期价值的反应滞后,降低信息传递的效率和质量(Weller,2018)。
具体而言,基本面交易者在获取和解读信息时面临时间和资金的约束,需要在“不拆单的
后续收益风险"和“拆单的交易延迟风险”之间进行权衡(李松楠等,2023)。相比之下,算
法交易者通过智能算法筛选订单流,能够将不利选择成本转移给反应较慢的基本面交易
者,削弱了后者通过信息获取利润的能力。此外,信息价值的侵蚀导致基本面交易者获取
信息的动力减弱,从而削减市场对基本面信息的需求。这种变化压缩了基本面交易者的
交易空间,并可能挤出传统的知情交易者和卖空交易者,进一步损害市场的信息效率
(Baldauf and Mollner,2020;Thomas et al.,2024;陈海强和倪博,2024)。基于以上分析,
提出以下竞争性假设:
H3b:算法交易通过挤出传统基本面交易者,降低市场信息效率。
三、研究设计
(一)数据来源
本文数据来源于CSMAR和RESSET数据库,其中高频交易与订单簿数据来自
CSMAR高频库,通过SQL Server获取处理。样本区间为2015年1月5日至2023年12月
31日,覆盖上交所主板各行业公司。经剔除新上市企业、ST股票、变量缺失样本,并对连
续变量进行1 \%缩尾处理后,最终得到583家上证主板上市公司共计1254920个公司-日
度观测值。
(二)变量定义
1.核心解释变量:算法交易强度
目前学术界对算法交易强度的度量尚未达成统一意见。得益于交易所提供的精确到
算法交易账户层面的详细订单流数据,针对欧美成熟资本市场的少数研究能够深入分析
算法交易者的订单提交、修改、撤销和执行情况,为研究其行为模式和市场影响提供了重
要支持(Brogaardetal.,2018)。然而,由于隐私保护、监管限制以及数据访问权限的差
异,大多数研究(Hasbrouck and Saar,2013;Chakrabarty and Pascual,2023)难以获取详细
账户级数据。鉴于算法交易策略通常涉及频繁的订单修改与撤销操作,电子信息流量能
够有效反映市场订单操作频率,因而其与交易额的比率常被用作衡量算法交易活跃程度
的代理变量。
因此,本文参考 Hendershott et al.(2011)基于电子信息流量的方法,构建了算法交易
强度指标作为算法交易活跃度的代理变量。具体而言,该变量通过捕捉与算法交易策略
相关的高频订单提交与取消行为来反映算法交易的活跃程度,其定义如下:
A T _ { i , d } = - \frac { T A _ { i , d } } { M T _ { i , d } }
其中,T \boldsymbol { A } _ { i , d }表示公司i在第d个交易日的成交总额,单位为每百元;M T _ { i , d }表示公司i
在第d个交易日的信息流量,定义为订单成交数、订单提交数或订单取消数的总和,单位
为笔数,本文基于限价订单簿前十层(Level2级别)的委托买卖笔数变化计算得出
M T _ { i , d } = \sum \mid \Delta B i d _ { 1 , k } + \cdots + \Delta B i d _ { 1 0 , k } + \Delta A s k _ { 1 , k } + \cdots + \Delta A s k _ { 1 0 , k } )。该指标值的增加意味着
算法交易活动强度的增加。
2.被解释变量1
(1)市场流动性。度量市场流动性的常用指标包括买卖价差、市场深度、换手率和
Amihud比率等。这些指标从交易成本、市场深度和交易活跃度等维度刻画了市场流动
性。鉴于本文采用订单流数据,且算法交易主要作用于执行层面,参考孙广宇等(2021)
和ChakrabartyandPascual(2023),采用成交额加权相对有效价差(RES)作为流动性衡量
指标。(2)市场价格稳定。市场价格稳定的刻画通常基于历史波动率和标准差、隐含波
动率以及极值波动性等指标。鉴于算法交易主要集中于日内交易活动,本文参考
Hasbrouck and Saar(2013)和Boehmer etal.(2021),采用价格极差(PR)作为市场价格稳
定的衡量指标。该指标能够有效捕捉公司在交易日内的股票价格波动范围。(3)市场信
息效率。本文从信息含量和信息反应速度两个维度衡量市场信息效率。在信息含量方
面,若股票价格偏离随机游走过程,则当前价格与历史价格之间必然存在自相关性,且自
相关性越强,信息效率越低(Chordia et al.,2005)。参考孙广宇等(2021)和Yuferova
(2024),本文采用5分钟间隔的报价中点自相关系数(QMAR)的绝对值衡量信息含量。
在信息反应速度方面,若滞后收益能显著预测个股收益,则说明市场吸收信息存在延迟。
参考Chakrabartyand Pascual(2O23),本文采用价格延迟指标(Delay)衡量该维度,取值0
至100,数值越高表示反应越滞后、信息效率越低。
3.控制变量
为控制市场活跃度、规模效应、价格水平及自相关性等因素对市场稳定和信息效率的
潜在影响,本文参考李金甜和毛新述(2023)、李松楠等(2023)的方法,选取以下控制变
量:个股换手率(Turnover),以上市公司当日成交量与流通股数的比值衡量;个股市值
(Value),以上市公司当日总市值的自然对数衡量;股价的倒数(Inverse_prc),以上市公司
当日收盘价的倒数衡量;价格极差(PR)作为波动率代理变量。除此之外,控制变量还包
含滞后一期的被解释变量。为缓解反向因果等内生性问题,所有控制变量均取滞后一期
的值1。
(三)模型设定
为检验算法交易强度对市场流动性、波动性和信息效率的影响,参考Boehmer et al.
(2021)与Chang and Chou(2022)的研究,本文设置以下基准回归模型:
\begin{array} { r } { R E S _ { i , d } \ = \ \alpha + \beta A T _ { i , d } \ + \gamma C o n t r o l _ { i , d - 1 } \ + \chi R E S _ { i , d - 1 } \ + \delta _ { i } \ + \mu _ { d } \ + \varepsilon _ { i , d } } \end{array}
P R _ { i , d } = \alpha + \beta A T _ { i , d } + \gamma C o n t r o l _ { i , d - 1 } + \lambda R E S _ { i , d - 1 } + \chi Q M A R _ { i , d - 1 } + \varphi D e l a y _ { i , d - 1 } + \delta _ { i } + \mu _ { d }
Q M A R _ { i , d } ~ = ~ \alpha + \beta A T _ { i , d } ~ + ~ \gamma C o n t r o l _ { i , d - 1 } ~ + \chi Q M A R _ { i , d - 1 } ~ + ~ \delta _ { i } ~ + \mu _ { d } ~ + \varepsilon _ { i , d } ~
D e l a y _ { i , d } = \alpha + \beta A T _ { i , d } + \gamma C o n t r o l _ { i , d - 1 } + \varphi D e l a y _ { i , d - 1 } + \delta _ { i } + \mu _ { d } + \varepsilon _ { i , d }
其中,\delta _ { i }为公司个体固定效应,\mu _ { d }为时间日度固定效应,C o n t r o l _ { i , d - 1 }表示滞后一期的
控制变量。此外,在模型(3)中,加入滞后一期的流动性指标(R E S _ { i , d - 1 })和信息效率指标
\textit { ( ) } Q M A R _ { \textit { i , d - 1 } }与D e l a y _ { i , d - 1 }),以控制流动性和信息效率对波动性的影响。在上述模型中,
所有回归均采用公司层面聚类的稳健标准误估计。
四、实证结果分析
(一)基准回归结果
表1第(1)列汇报了算法交易强度对市场流动性的基准回归结果。在控制日度固定
效应和公司固定效应的情况下,核心解释变量AT系数显著为负,意味着算法交易强度的
提升降低了相对有效价差,表明算法交易强度的增加能够改善市场流动性,支持了假设
Hla。这一发现与Menkveld(2013)基于成熟市场的研究结论一致,即算法交易通过高频
报价和动态订单调整,为市场提供了持续的流动性支持,降低了交易成本。上述结果背后
的原因与成熟市场有所差异。与欧美市场常借助暗池减少市场冲击不同,A股市场的算
法交易者更倾向于采用被动执行策略,一方面主动吸收散户订单冲击,缓解瞬时流动性缺
口,另一方面通过分散执行降低交易成本,从而在高噪声环境中更有效地发挥流动性提供
者角色。
表1第(2)列汇报了算法交易强度对于市场波动性的影响。核心解释变量AT系数
值显著为负,意味着算法交易强度的提升降低了价格极差,表明算法交易对市场波动具有
明显的抑制作用,支持了假设\mathrm { H } 2 \mathrm { a }。由于此回归方程还同时控制了流动性指标RES和信
息效率指标QMAR及Delay,说明算法交易对市场波动的抑制作用不能简单地归因为新信
息吸收速度的放缓或是买卖价差的缩小。对此结果可能的解释是,算法交易通过提供流
动性(Brogaard etal.,2018)、执行市场中性策略(Menkveld,2013)以及进行短期套利
(Hasbrouck and Saar,2013;Carrion,2013)等方式,使市场对冲击的反应更加平稳,从而抑
制了剧烈的价格波动。
表1第(3)和第(4)列汇报了算法交易强度对于市场信息效率的影响。结果显示,核
心解释变量AT系数值均显著为正,意味着算法交易强度的提升不仅降低了市场价格的
信息含量,还减缓了市场价格对信息的反应速度,表明算法交易活动的增加显著抑制了市
场信息效率的提高,支持了假设\mathrm { H } 3 \mathrm { b }。这一结果说明,尽管算法交易在稳定市场价格方面
具有积极作用,但其交易策略的短期性、复杂性(Carrion,2013;Baldauf and Mollner,
2020)以及高频撤单行为(Hasbrouck and Saar,2013)干扰了市场对信息的反应,延缓了价
格吸收信息过程。
(二)稳健性检验结果1
第一,替换核心解释变量。尽管电子信息流量作为衡量算法交易活动的有效代理变
量,但其可能受到市场结构变化等其他因素的干扰,从而导致估计偏差。为此,本文借鉴
Weller(2018)和Yuferova(2024)的方法,计算了算法交易强度的替代变量——平均每笔
成交规模ATS,并将其作为解释变量进行回归分析,结论依然稳健。
第二,替换被解释变量。为考察不同市场稳定与信息效率的度量方式对实证结果的
影响,本文分别替换了流动性、波动性、信息含量和信息反应速度的代理变量。首先,在流
动性指标方面,采用成交额加权相对报价价差RQS作为新的替代变量。其次,在波动性
指标方面,参考Changand Chou(2022)的做法,使用基于5分钟频率的数据计算的已实现
波动率R V作为新的替代变量。再次,在信息含量方面,本文将QMAR指标的采样频率由
5分钟变更为10分钟,作为新的替代指标。最后,在信息反应速度方面,本文将Delay指
标的采样频率由5分钟变更为1分钟,作为新的替代指标。按上述方式替换被解释变量
之后,估计结果依然稳健。
第三,增加新的控制变量。为更全面地控制市场特征对研究结果的影响,本文在回归
分析中引入了对数化后的成交量(Volume)和剩余股票的市场质量指标平均值(\widetilde { M I })两
个新的控制变量。成交量是市场的重要特征变量,通常与流动性、波动性等因素密切相
关。原始成交量数据通常呈现右偏分布,容易受到极端大额交易的影响,从而对回归结果
产生不成比例的权重效应。因此,使用对数化后的成交量能够有效平滑数据,减弱极端值
的影响,并提升不同规模样本间的可比性。此外,考虑到市场稳定性和信息效率的影响因
素不仅限于单个证券层面,还可能受到跨市场共同因素的影响(Malceniece etal.,2019)。
因此,本文引入了所有其他股票的市场质量指标平均值作为控制变量,重新估计基准模
型,主要结论保持不变。
第四,调整聚类层级。为控制潜在的聚类相关性,本文对聚类层级进行了调整。首
先,将聚类层级调整至时间层面,以有效考虑同一时间段内的市场活动和事件对算法交易
影响结果的相关性。其次,进一步将聚类层级调整至公司交互时间的层面,以捕捉算法交
易在不同公司和时间背景下对市场影响的差异性。尽管聚类层次的调整更加细化,回归
结果仍保持稳健。
第五,扩展样本数量。为进一步确保实证结论的稳健性,本文将样本扩展至所有A
股上市公司,具体样本选择标准如下:(1)去除了样本期内上市交易时间少于1年的公
司,以避免新股上市初期可能出现的价格波动和交易异常对结果的干扰,确保样本公司具
有相对稳定的市场表现;(2)剔除了金融行业上市公司、ST和*ST上市公司、重要变量缺
失10 \%以上的上市公司;(3)对所有连续变量数据进行1 \%水平的双向缩尾处理。经过
上述数据处理后,新的研究样本包含2532家A股上市公司,共计3603135个公司一日度
观测值,覆盖上证主板、深证主板、创业板和科创板四大板块。回归结果表明,样本的扩展
并未改变核心结论。
(三)内生性问题处理1
1.工具变量法
由于现有的相关研究数据无法识别单个交易者,使用电子信息流量作为算法交易活
动的代理变量可能引入噪声。此外,流动性的改善或波动率的下降可能创造一个更吸引
算法交易者的市场环境,造成算法交易活动的增加,从而导致潜在的内生性问题。因此,
本文参考 Hasbrouck and Saar(2013)和Cartea et al.(2019)的做法,使用以下工具变量:
(1)滞后一期算法交易强度指标(I V 1)。(2)剔除公司本身以及其所在行业(基于2012年
版证监会行业分类代码)的其他公司,使用市场剩余公司的同期算法交易强度平均值作
为公司的工具变量(I V 2 )。工具变量回归结果显示,核心变量系数符号与基准回归结果
仍保持一致。无论是采用上述哪一种指标作为工具变量,算法交易对市场稳定和信息效
率的影响均显著和稳健。
2.双重差分法
自2014年11月起,上交所与港交所正式后动沪港通机制,允许境外投资者通过“沪
股通"渠道直接参与A股交易。随着沪股通标的范围不断扩展,逐步涵盖大盘蓝筹股及
部分中小盘成长股,并伴随交易机制与市场基础设施的持续优化,该制度性安排为研究市
场结构和投资者行为提供了一个良好的准自然实验环境。
沪港通机制的引入为A股市场带来了更多算法交易需求。一方面,推动了A股市场
交易平台和市场基础设施的智能化建设。降低了订单执行延迟,提高了交易系统容量,为
算法交易的发展提供了更强的技术支持和制度便利;另一方面,引入沪港通机制后,A股
市场在投资者结构、投资理念和交易策略等方面均发生了变化。沪股通吸引了来自成熟
市场的机构投资者,包括对冲基金、投行自营部门以及高频量化投资机构等,他们依赖算
法交易策略获取信息优势、速度优势以及跨市场套利机会2。本文据此将纳入沪股通的
公司作为处理组,未纳入的公司作为对照组,借鉴 Stephan(2024)、陈海强和倪博(2024)
的方法,构建双重差分模型识别沪港通对算法交易及其市场效应的影响。平行趋势检验
显示,被纳入沪股通前处理组与对照组无系统性差异,满足识别假设。为缓解潜在异质性
偏差,还基于政策实施前(2013年)两类公司在换手率、市值、价格、波动性、盈利能力、杠
杆率、账面市值比及行业分布等特征,采用最近邻和半径匹配方法进行倾向得分匹配。匹
配后结果与基准回归一致,进一步支持核心结论。
(四)分组回归
1.区分所有权与公司规模
研究表明,在规模较大、收益水平较好、经营稳定性较强的上市公司中,算法交易带来
的改善效应更为明显(Brogaard et al.,2014; Boehmer et al.,2021)。我国国有上市公司
通常具备规模大、交易活跃、业绩较优以及受严格监管等特点,因而被视为较高质量的上
市公司。本文基于所有权性质和市值规模分组回归发现,算法交易在非国有和中小公司
中对流动性、波动性和信息含量的影响更明显。与成熟市场相比,此差异可能源于A股
独特的投资者结构。在A股市场以散户为主、机构集中于大市值股票的背景下(Jones et
al.,2025),算法交易更有效地捕捉市场情绪,从而对中小盘股产生更显著的影响。
2.区分上市公司信息披露质量
有研究发现,信息披露质量与算法交易活跃度密切相关(Thomas etal.,2024)。高透
明度公司中,基本面投资者有效获取信息并提升定价准确性,抑制了算法交易的套利空间
(Carrion,2013);而在低信息披露质量的公司中,严重的信息不对称与低效的价格发现使
市场更依赖短期信号,为算法交易创造了更多获利机会。本文基于CSMAR《上市公司信
息考评表》进行分组回归发现,在低信息披露质量组中,算法交易虽通过改善流动性及降
低波动提升了短期市场稳定性,但也显著抑制了价格的信息含量与反应速度。这表明,在
信息透明度不足的环境中,算法交易更倾向于依赖短期技术指标进行交易,反而削弱了市
场对长期基本面信息的反映能力。
3.区分不同市场周期
过往研究表明,算法交易的市场影响在不同的市场周期可能存在差异(Brogaard et
al.,2018;Chakrabarty and Pascual,2023)。本文考察算法交易在我国不同市场周期的差
异性影响。样本期内我国股票市场存在以下异动周期:\textcircled{1} 2 0 1 5年1月5日至2016年1月
27日;\textcircled { 2 } 2 0 1 8年1月29日至2019年1月4日;\textcircled{3} 2 0 2 1年9月13日至2022年4月27日;
\textcircled {4 } 2 0 2 3年5月9日至2023年12月31日。将上述四段市场异动周期与剩余样本区间划
分开来,考察不同市场周期中算法交易对市场稳定和信息效率的影响。回归结果表明,算
法交易在不同市场周期中对市场稳定和信息效率的影响存在显著差异。市场稳定方面,
算法交易在市场异动期间对流动性和波动性的改善作用更为显著;信息效率方面,随着算
法交易强度的提高,其对市场异动周期中股票价格信息含量和信息反应速度的抑制作用
不断增强。
五、进一步讨论
(一)可能的流动性共性风险
个股流动性与市场其他股票之间的共性运动,被认为是引发系统性流动性风险的重
要来源(李金甜和毛新述,2023)。算法交易基于预设策略的执行特性可能导致不同股票
流动性变动的共性增强,进而提升个股流动性对市场流动性的相关性,放大系统性流动性
风险(Malceniece etal.,2019)。为探究算法交易是否加剧了流动性共性效应,本文借鉴
李金甜和毛新述(2023)的做法,构建流动性共性指标(Liquidity Commonality,CiL)」,并
分析算法交易对其影响。表2中列(1)至列(3)的回归结果显示,核心解释变量AT的系
数值均不显著,表明其并未对流动性共性产生明显影响。尽管理论上算法交易可能通过
提高市场流动性和减少冲击成本来影响个股的流动性共性,但实证结果未能支持这一假
设。这可能源于算法交易策略的多样性导致个股流动性影响不均。此外,市场的微观结
构和流动性特征也可能使得算法交易的效果在高流动性时期被掩盖。
(二‘好’‘坏"消息的影响
考虑到股市中“好消息”与“坏消息”对市场波动可能具有非对称效应——即负面信
息通常能比正面信息引发更剧烈的价格波动,本文进一步探讨在不同类型信息冲击下,算
法交易对市场波动性的影响。借鉴陈国进等(2019a)的研究方法,将收益率符号纳入价
格极差PR的计算之中,以评估算法交易在正面信息“好消息")和负面信息“坏消息”)
冲击下对市场稳定性的影响效应。表2中列(4)至列(6)的实证结果表明,算法交易对市
场波动性具有显著的抑制作用。然而,算法交易对不同类型波动的影响存在差异:对“好
波动”而言,算法交易对价格极差的抑制作用更为显著,表明算法交易能够有效抑制过度
乐观情绪引发的波动;对“坏波动”算法交易的抑制作用相对较弱,这表明算法交易在面
对负面信息冲击时,其稳定市场的作用相对有限。
(三)算法交易影响市场信息效率的潜在渠道
本部分检验算法交易降低市场信息效率的两种潜在渠道。第一,算法交易可能通过
挤出知情交易者降低市场信息效率。知情交易的存在提高市场价格对基本面信息的敏感
度(Easleyetal.,2011)。当算法交易者与知情交易者成为交易对手时,其较低的交易成
本和强大的信息筛选能力减少了知情交易者获取信息租金的机会,抑制了知情交易者的
活动强度(Weller,2018)。为验证上述渠道,使用知情交易强度变量VPIN(陈国进等,
2019b)进行分析。表3中的前3列展示了这一实证结果,列(1)中A T的系数显著为负,
说明算法交易强度的增加降低了知情交易强度;列(2)和列(3)显示知情交易强度可以提
高市场价格信息含量和信息反应速度。上述结果说明算法交易通过抑制知情交易者活
动,削弱了市场对基本面信息的反映能力,降低了市场信息效率。
第二,算法交易可能通过压缩卖空者的套利空间,降低其参与度,从而降低市场信息
效率。算法交易者利用其算法和数据分析能力,能够更快地识别并抢占套利机会,挤压卖
空者的交易空间和获利能力(陈海强和倪博,2024),导致卖空者的交易意愿下降。为验
证上述渠道,采用卖空强度变量 Shortper(定义为当日融券余额除以收盘流通市值)衡量
信息型卖空行为,考察其变动特征及对市场信息效率的影响。表3列(4)至列(6)的结果
支持这一渠道。列(4)中核心解释变量AT的系数显著为负,表明算法交易强度上升显著
抑制卖空行为;尽管列(5)中卖空强度系数不显著,但其系数仍是负值,且列(6)显示卖空
强度系数显著为负,依然可以表明其提高了信息反应速度。上述结果说明算法交易通过
抑制卖空交易者活动,削弱了市场对基本面信息的反映能力,降低了市场信息效率。
为进一步验证上述渠道,本文首先参考Liet al.(2023)提出的投资者类型识别方法,
基于CSMAR高频数据库的逐笔订单成交数据,分别构建了机构投资者、大散户投资者和
小散户投资者的订单不平衡(OIB)指标」。表4中列(1)回归结果显示,算法交易对机构
投资者的订单不平衡OIB产生显著负向影响,说明算法交易通过挤出机构投资者降低市
场信息效率。
其次,参考陆蓉等(2025),进一步考察算法交易强度与订单流不平衡OIB之间的动
态关系。表4中列(4)至列(6)的回归结果显示,算法交易强度与前一期各类投资者的订
单流不平衡L.OIB 显著正相关,表明算法交易具有趋势跟随特征。结合表4列(1)的结
果,算法交易强度与机构投资者当期订单不平衡OIB显著负相关,说明算法交易者会利
用执行速度优势挤压机构投资者的交易空间,削弱其定价作用,验证了算法交易降低市场
信息效率的渠道。
六、结论与政策建议
本文利用2015-2023年我国A股市场的高频交易数据和订单簿数据,构建算法交易
强度指标,揭示算法交易提升股票市场稳定与降低信息效率的双重影响。研究发现,算法
交易改善了市场流动性并抑制了价格波动,提升了市场稳定;但与此同时,算法交易通过
挤出传统的知情交易者和卖空交易者,延缓了市场对新信息的吸收过程,降低了信息效
率。分组回归结果表明,上述双重影响在非国有、中小规模及信息披露质量较低的上市公
司中更为显著。此外,算法交易在市场异动期间通过更强的流动性支持和波动性抑制,增
强了市场稳定;但也因削弱价格信息含量与信息反应速度而加剧了信息效率的损失。进一
步分析显示:(1)算法交易对于个股的流动性共性风险影响并不显著,表明其并未引发潜在
的系统性流动性风险;(2)相较于正面信息引发的股市“好波动”,算法交易在应对负面信息
引发的“坏波动"时,表现出较弱的稳定作用,表明其在提升市场稳定方面具有一定局限性;
(3)算法交易通过挤出传统的知情交易者和卖空交易者,降低了市场信息效率。
基于本文的研究发现,提出以下政策建议:第一,提升算法交易的信息透明度。应推
动建立算法交易策略与风险管理的定期披露机制,要求算法交易者公开核心策略框架、关
键参数及风控措施,增强市场对其交易行为的理解与预期,缓解因信息不对称引发的市场
疑虑。第二,构建稳定性导向的算法交易监管框架。建议引入基于波动率与市场阈值的
交易限制机制,在极端行情中自动触发算法交易调节措施。可探索设置流动性缓冲要求,
引导算法交易商在市场异常时发挥流动性供给功能,抑制过度交易对市场稳定的冲击。
第三,加强对市场信息效率的监测与保护。应进一步压实上市公司信息披露责任,提升信
息披露质量与违规成本,从源头上改善信息环境。同时,可借助监管科技手段,建立市场
信息效率实时监测体系,对可能引致价格扭曲的异常交易行为进行识别与干预,保障价格
对信息的有效反映。
参考文献
[]陈国进、丁杰和赵向琴,{ 2 0 1 9 } \mathrm { a }《“好"的不确定性“坏"的不确定性与股票市场定价——基于中国股市高频数据分
析》,《金融研究》第7期,第174~190页。
[]陈国进、张润泽、谢沛霖和赵向琴\mathbf { \nabla } _ { \mathbf { \mu } } 2 0 1 9 \mathrm { b }《知情交易、信息不确定性与股票风险溢价》,《管理科学学报》第4期,第
53~74页。
B]陈海强和倪博,2024,\mathrm { \ } ( \mathrm { T } + 0量化交易与转融券市场化费率居高不下之谜——从交易制度套利论协同改革的必要
性》,《管理世界》第6期,第60~76页。
陈海强、倪博、宋沐青和廖培森,2024,《信息披露的同伴效应促进了金融市场稳定——基于创业板注册制信息披
露改革的实证研究》,《经济学(季刊)》第5期,第1 6 7 2 \sim 1 6 8 7页。
陈海强、赵潇洋和李东旭,2023,《股权质押渠道与金融市场稳定——基于股价崩盘风险的视角》,《管理科学学报》
第6期,第81~95页。
李金甜和毛新述\bullet 2 0 2 3 ,《资本市场制度型开放与流动性共性效应一兼论气候风险的影响》,《金融研究》第5期,
第1 7 0 \sim 1 8 8页。
李松楠、刘玉珍和胡聪慧,2023,《价格笼子、流动性与价格发现效率—基于创业板注册制改革的证据》,《管理世
界》第3期,第49~62页。
陆蓉、张瑞瑞和闵思凯,2025,《量化交易的市场价值效应—信息优势的作用》,《管理世界》第6期,第5 5 \sim 7 6 +
1 5 7 + 7 7 \sim 9 7页。
孙广宇、李志辉、杜阳和王近,2021,《市场操纵降低了中国股票市场的信息效率吗——来自沪市\mathrm { A }股高频交易数
据的经验证据》,《金融研究》第9期,第1 5 1 \sim 1 6 9页。
[0]王良、秦隆皓、刘潇和陈婕,2018,《高频数据条件下基于ETF基金的股指期货套利研究》,《中国管理科学》第5
期,第9~20页。
[1]王宇超、李心丹和刘海飞\bullet 2 0 1 4《算法交易的市场影响研究》,《管理科学学报》第1期,第57~71页。
[2]韦立坚、张大卫、骆兴国和张洋锋,2022,《股指期货市场的高频交易与价格发现》,《管理科学学报》第1期,第
95~106页。
[13]吴偎立和常峰源,2021,《ETF、股票流动性与流动性同步性》,《经济学(季刊)》第2期,第6 4 5 \sim 6 7 0页。
[4]赵家悦、卢锐、柳建华和Jerry\mathrm { C a o } , 2 0 2 4 ,《涨跌停制度变革、股票流动性与资本市场表\Iup,《金融研究》第3期,第
113~131页。
[5]张路、李金彩、袁振超和岳衡,2021,《管理者能力与资本市场稳定》,《金融研究》第9期,第188~206页。
[6]张小日、孙芳芳和叶强,2024,《A股程序化交易与盈余公告前股价信息含量》,《计量经济学报》第6期,第1441~
1466页。
[17] Aquilina,M.,E.Budish and P.O'neill,2022,“Quantifying the High -Frequency Trading‘Arms Race’”,The
Quarterly Journal of Economics,137(1),pp.493~564.
[18]Baldauf,M.andJ.Moller,202O,“High-Frequency Tradingand Market Performance”,The JournalofFinance,75
(3),pp. 1495~1526.
[i9]Boehmer,E.,K.Fong and J.J.Wu,2O2l,“Algorithmic Tradingand Market Quality:International Evidence”,
Journal ofFinancial & Quantitative Analysis,56(8),pp.2659~2688.
20 Brogaard,J.,A.Carron,T.Moyaert,R.Riordan,A.Shkilko and K.Sokolov,2O018,“High-Frequency Trading
and Extreme Price Movements ”,Journal of Financial Economics,128(2),pp.253~265.
[1] Brogard,J,T.HendershottandR.Riordan,2O14,“High-Frequency Trading andPrice Discovery”,TheReviewof
Financial Studies,27(8),pp.2267 ~2306.
[2] Carrion,A.,2O13,“VeryFast Money:High-Frequency Trading on the NASDAQ”,Journal ofFinancial Markets,16
(4),pp.680 ~711.
[23] Cartea,A.,R.Payne,J.Penalva,andM.Tapia,2019,“Ultra-Fast ActivityandIntraday Market Quality”,Journal
of Banking& Finance,99,pp.157 ~181.
[4l Chakrabarty,B.andR.Pascual,2023,“Stock Liquidity and Algorithmic Market Making During the COVID-19
Crisis”,Journal of Banking & Finance,147,pp.106415.
[5] Chang,Y.K.andR.K.Chou,2022“Algorithmic Trading and Market Quality:Evidence from the Taiwan Index
Futures Market”,Journal of Futures Markets,42(10),pp.1837~1855.
[6 Chordia,T.,R.Rolland A.Subrahmanyam,2005,“Evidence on the Speed of Convergence to Market Efficiency”,
Journal of Financial Economics,76(2),pp.271~292.
[7]Easley,D.,M.M.LDe Prado and M. OHara,2O1l,“The Microstructure of the‘Flash Crash’:Flow Toxicity,
Liquidity Crashes,and theProbabilityof Informed Trading”,JournalofPortfolio Management,37(2),pp.118~128.
[8] Hasbrouck,J.and G.Saar,2013,“Low-Latency Trading”,Journal of Financial Markets,16(4),pp.646~679.
[9]Hendershott,T.,C.M.Jones and A.J.Menkveld,201,“Does Algorithmic Trading Improve Liquidity?”,The
Journal of Finance,66(1),pp.1~33.
Bol Jones,C.M.,D.Shi,X.Zhang and X.Zhang.,2O25,“Retail Trading andReturn Predictability in China”,Journal
ofFinancial & Quantitative Analysis,60(1),pp.68~104.
B1]Leal,S.J.and M.Napoletano,2O19,“Market Stabilityvs.Market Resilience:Regulatory Policies Experiments inan
Agent-Based Model withLow-and High-Frequency Trading”,Journal of Economic Behavior & Organization,157,
pp.15~41.
b2] Li,S.,J.Wu,X.Zhangand X.Zhang,2023,“Tracking Retail andInstitutional Investors Activityin China”,PBCSF
- NIFR Research Paper,SSRN:https://ssn.com/abstract=4630162.
B3] Malceniece,L,K.Malcenieksand T.J.Putnin,2019,“High-Frequency Trading and Comovement inFinancial
Markets”,Journal of Financial Economics,134(2),pp.381~399.
B4 Menkveld,A.J.,2O13,“High-Frequency Trading and the New-Market Makers”,Journal ofFinancial Markets,16
(4),pp.712~740.
b5] Stephan,A.,2O24,“The Efect of Algorithmic Trading on Management Guidance”,The Accounting Review,99(6),
pp.421~449.
b6 Thomas,W.B.,Y.Wang and L. Zhang,2O24,“Algorithmic Trading and Forward - Looking MD&A Disclosures”,
Journal of Accounting Research,62(4),pp.1533~1569.
b7] Weler,B.M.,2018,“Does Algorithmic Trading Reduce Information Acquisition?”,The Review of Financial Studies,
31(6) ,pp.2184 ~ 2226.
B8]Yuferova,D.,2O24,“Algorithmic Trading and Market Effciency Around the Introductionof theNYSE Hybrid Market”,
Journal of Financial Markets,69,pp.100909.
The Market Impact of Algorithmic Trading:
Dual Perspectives of Stability and Information Efficiency
YUE WeiQU Jianwen LI ZixiaoLIU Yue
( College of Finance and Statistics,Hunan University)
Summary:Algorithmic trading refers to trading technology that uses computer algorithms to automate trading
decisions,submit orders,and manage order execution.It includesportfolio selection,trading strategies,
execution strategies,and other elements,and has become a significant trading method in the securities market.
Currently,program trading in the securities market often adopts algorithmic trading approaches.
In April 2O24,the State Council issued the“Guidelines on Strengthening Regulation,Forestalling Risks
and Promoting the High - Quality Development of the Capital Market”,which explicitly called for the
formulation of regulations on program trading supervision and strengthened oversight of high- frequency
algorithmic trading.In May,the China Securities Regulatory Commission(CSRC) introduced the“Provisions
onthe Administration of Program Trading in the Securities Market(Trial)”to provide institutional foundation
foralgorithmic trading regulation.In line with the political and people-centered nature of financial work and
thephilosophyof serving the people through finance,further efortsare needed to protect the legitimate rights
and interests of the vast number of small and medium - sized retail investors in China's stock market.Improving
theregulatory framework for algorithmic trading requires comprehensive theoretical and empirical research on its
market impact and mechanisms,tailored to the realities of Chinas capital market.
This paper uses high -frequency trading data and order book data from China's A-share market between
2015 and 2023 to develop an algorithmic trading intensity indicator.It empiricall examines the dual impact of
algorithmic trading on stock market stabilityand information eficiency.The main findings are as follows:First,
algorithmic trading reduces bid -ask spreads in the stock market while also decreasing price ranges and realized
volatility,thereby enhancing market stability by improving market liquidity and suppressing market volatility.
Second,algorithmic trading reduces the intensity of informed tradingand short seling,thereby lowering market
information eficiency by crowding out traditional informed traders and short selers.Third,during periods of
market turbulence,algorithmic trading enhances market stability through stronger liquidity support and
suppression of price volatility;however,it simultaneously reduces the information content and speed of
information reaction in the market,leading toamore significant decline in information efficiency.Fourth,
algorithmic trading does not significantly impact the commonality risk of individual stock liquidity,indicating
that itdoes not increase liquidity commonality risk.Fifth,algorithmic trading exhibitsanasymmetric
suppression effct on“good volatility”and“bad volatility”in the stock market.Specifically,compared to
"good volatility”triggered by positive information,algorithmic trading shows aweaker stabilizing effect in
response to“bad volatility”caused by negative information.Additionaly,this paper analyzes the heterogeneous
impactof algorithmic trading on market stabilityand information eficiency from perspectives such as companys
ownership,size,and quality of information disclosure.The study finds that for non-state-owned listed
companies,smalland medium-sized listed companies,and listed companies with lower-quality information
disclosure,the efect of algorithmic trading in enhancing market stabilityis accompanied by a more pronounced
reduction in information efficiency.
The possible contributions of this paper are mainly in the following two aspects:(1)Previous studies have
shown that algorithmic trading enhances market information eficiency in mature capital markets but exacerbates
market volatility and,in extreme cases,leads to rapid depletion of market liquidity,thereby threatening market
stability.This paper,however,reveals the dual impact of algorithmic trading on Chinas capital market,that is,
enhancing market liquidity,reducing volatility,and thereby improving market stability,while simultaneously
reducing market information eficiency.Thus,in terms of theoretical implications,the findings provide new
empirical evidenceon the market impactof algorithmic trading.In terms of practical implications,the empirical
results ofer a quantitative basis for improving algorithmic trading regulatory rules.(2)This paper enriches the
academic discusion on the impact of securities trading models on capital markets.While existing literature has
largely focused on the efects of listed company characteristics,institutional mechanisms,and market systems
on capital markets,this study reveals the dual impact of algorithmic trading,an artificial intellgence-driven
securites trading method,on both market stability and informational eficiency.These findings provide a new
perspective for understanding the role of artificial intelligence technology in capital markets.
Based on the findings of this paper,the following policy recommendations are proposed to fully leverage the
positive role of algorithmic trading in supporting market stability while optimizing the market information
environment to mitigate its negative impact oninformation eficiency:First,regulatory authorities should
strengthen the management of algorithmic trading transparency to enhance market comprehensibility and
predictability of algorithmic trading behaviors.Second,given the significant diferences in the impact of
algorithmic trading onstability under diferent market conditions,policymakersneed toestablisha market
stabilityregulatory framework specificaly tailored to algorithmic trading.Third,sincealgorithmic trading may
delay price convergence to intrinsic value,regulatory agencies should strengthen the protection and monitoring
of market information efficiency.
Keywords:Algorithmic Trading,Market Stability,Information Efciency,Liquidity Risk,Price Volatility
JEL Classification: G1O,G12,G14
(责任编辑:李文华)(校对:LH)
