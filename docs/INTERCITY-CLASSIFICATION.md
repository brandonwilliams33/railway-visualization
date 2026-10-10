# 城际站点归类 · 2026-10-10

已核验36个城市、27条线路/运营分段、225个独立出发站。本轮在147个基础上增加78个站点的导航归类。65个共有枢纽或干线站保留外层快捷入口，160个站点收进城际子目录。深圳机场、深圳机场北、福海西、沙井西在深圳城际子目录中列出，深圳北与“城际铁路”并列。

归类数据在 `src/data/intercity-groups.json`，逐条保存线路名称、省份范围 `provinceIds`、独立站点ID、是否保留外层入口及公开来源。`src/lib/intercityIndex.ts`只引用现有开放站点，严格核对ID、名称与省份。跨省线路按每站实际所属城市显示，不把大兴机场改归北京。不同站点不合并，同站多线路只列一次并附线路标签。线路归类不产生车次、不改变直达或绘图；C字头、机场名、距离近均不自动归入。

|城市|已识别独立站点|
|---|---:|
|上海|5|
|东莞|21|
|中山|7|
|佛山|5|
|保定|1|
|北京|5|
|南京|3|
|咸宁|3|
|唐山|3|
|天津|9|
|威海|4|
|孝感|2|
|常州|4|
|广州|32|
|廊坊|9|
|开封|3|
|惠州|8|
|无锡|4|
|株洲|4|
|武汉|10|
|江门|2|
|深圳|4|
|清远|6|
|湘潭|4|
|烟台|4|
|焦作|3|
|珠海|11|
|肇庆|1|
|苏州|8|
|郑州|10|
|鄂州|4|
|镇江|4|
|长沙|13|
|青岛|5|
|黄冈|2|
|黄石|2|

## 线路与依据

- 穗深城际：新塘南、中堂、望牛墩、东莞西、洪梅、东莞港、厚街、虎门北、虎门东、长安西、长安、沙井西、福海西、深圳机场北、深圳机场。 [来源 1](https://news.southcn.com/node_28e97ffc67/b1fa309343.shtml) / [来源 2](https://jtys.sz.gov.cn/ydmh/jtcx/hccx/hczfb/content/post_9979838.html) / [来源 3](https://www.sznews.com/news/content/2019-12/14/content_22703785.htm)
- 穗深城际 · 新白广段：竹料、钟落潭东、九佛、佛塱、新龙、镇龙、永宁北、永宁南、新塘南。 [来源 1](https://www.huadu.gov.cn/zfxxgkml/gzshdqjtysj/content/mpost_10955866.html)
- 广州东环城际：花都、花城街、花山镇、白云机场北、白云机场南、白云机场东、竹料、帽峰山、大源、龙洞、岑村、科韵路、琶洲、番禺。 [来源 1](https://www.gz.gov.cn/zt/qltjygadwqjsxsdzgzlfzdf/gzzxd/content/post_10450408.html) / [来源 2](https://www.gz.gov.cn/zwfw/zxfw/content/post_6941799.html)
- 琶莲城际：琶洲、深井、化龙南、广州莲花山。 [来源 1](https://www.gz.gov.cn/zt/qltjygadwqjsxsdzgzlfzdf/gzzxd/content/post_10450408.html)
- 广清城际：花都、乐同、狮岭、银盏、龙塘镇、清城、燕湖、洲心、飞霞、广州白云。 [来源 1](https://www.gz.gov.cn/zwfw/zxfw/content/post_6941799.html) / [来源 2](https://td.gd.gov.cn/dtxw_n/tpxw/content/post_4642563.html) / [来源 3](https://www.huadu.gov.cn/zfxxgkml/gzshdqjtysj/content/post_10663601.html)
- 广惠城际 · 佛莞段：番禺、广州长隆、东环、官桥北、广州莲花山、麻涌、东莞西。 [来源 1](https://crec.joyhua.cn/ZTB/20240531/html/content_20240531001003.htm) / [来源 2](https://www.gz.gov.cn/zwfw/zxfw/jtfw/content/mpost_9674465.html)
- 广惠城际 · 莞惠及北延段：东莞西、道滘、西平西、东城南、寮步、松山湖北、大朗镇、常平南、常平东、樟木头东、银瓶、沥林北、陈江南、惠环、龙丰、西湖东、云山、小金口、惠州北。 [来源 1](https://dgsx.dg.gov.cn/sxgk/sxfq/zzsx/content/post_4160351.html) / [来源 2](https://www.gdszx.gov.cn/attachment/0/0/141/27076.pdf) / [来源 3](https://www.huadu.gov.cn/zfxxgkml/gzshdqjtysj/content/mpost_10523946.html)
- 珠机城际：珠海、湾仔北、十字门、横琴、珠海长隆、三灶东、珠海机场。 [来源 1](https://td.gd.gov.cn/gkmlpt/content/4/4804/post_4804412.html)
- 广珠城际：广州南、北滘、顺德、顺德学院、容桂、南头、小榄、中山北、中山、南朗、翠亨、珠海北、唐家湾、明珠、前山、珠海、古镇、江门东、新会。 [来源 1](https://www.chinanews.com/sh/2019/11-14/9006790.shtml) / [来源 2](https://zsrbapp.zsnews.cn/home/content/newsContent/ass%3D/629431) / [来源 3](https://gdee.gd.gov.cn/attachment/0/361/361695/2958531.pdf)
- 长株潭城际：长沙、麓谷、尖山、谷山、八方山、观沙岭、开福寺、树木岭、香樟路、湘府路、洞井、芙蓉南、暮云、田心东、大丰、株洲、株洲南、昭山、荷塘、板塘、湘潭。 [来源 1](https://www.hunan.gov.cn/hnszf/hnyw/szdt/202306/t20230620_29379786.html)
- 郑开城际：郑州东、贾鲁河、绿博园、运粮河、宋城路、开封。 [来源 1](https://source.nra.gov.cn/tlfc/tpsy/202503/t20250317_348258.shtml)
- 郑机城际：郑州东、南曹、孟庄、新郑机场、郑州航空港。 [来源 1](https://public.zhongmu.gov.cn/D2601X/9772604.jhtml)
- 武咸城际：武昌、武汉东、南湖东、汤逊湖、庙山、纸坊东、山坡东、贺胜桥东、横沟桥东、咸宁南。 [来源 1](https://www.hb-railway.cn/businessArea/railwayOperation/202409/t20240902_131671.shtml)
- 武黄城际：武汉、武汉东、葛店南、鄂州、花湖、黄石北、大冶北。 [来源 1](https://www.hb-railway.cn/businessArea/railwayOperation/202409/t20240902_131671.shtml)
- 武冈城际：葛店南、华容东、黄冈西、黄冈东。 [来源 1](https://www.hb-railway.cn/businessArea/railwayOperation/202409/t20240902_131671.shtml)
- 武孝城际：汉口、天河机场、闵集、孝感东。 [来源 1](https://www.hb-railway.cn/businessArea/railwayOperation/202409/t20240902_131671.shtml)
- 沪宁城际：南京、仙林、镇江、丹徒、丹阳、常州、戚墅堰、惠山、无锡、无锡新区、苏州新区、苏州、苏州园区、阳澄湖、昆山南、安亭北、南翔北、上海西、上海、上海虹桥。 [来源 1](https://www.suzhou.gov.cn/szsrmzf/szyw/202408/aaa61cd59f6a4f4bb8b524b6fc7312c5.shtml) / [来源 2](https://kyfw.12306.cn/mormhweb/zxdt/202304/t20230415_39211.html)
- 沪宁沿江城际：南京南、句容、金坛、武进、江阴、张家港、常熟、太仓、上海。 [来源 1](https://www.suzhou.gov.cn/szsrmzf/szyw/202408/aaa61cd59f6a4f4bb8b524b6fc7312c5.shtml)
- 广肇城际 · 广佛南环段：佛山西、番禺。 [来源 1](https://td.gd.gov.cn/dtxw_n/tpxw/content/post_3932031.html) / [来源 2](https://www.gz.gov.cn/zwfw/zxfw/jtfw/content/post_9669108.html)
- 广肇城际 · 佛肇段：佛山西、肇庆。 [来源 1](https://www.gz.gov.cn/zwfw/zxfw/jtfw/content/post_9669108.html)
- 郑焦城际：郑州、南阳寨、黄河景区、武陟、修武西、焦作。 [来源 1](https://www.12306.cn/mormhweb/zxdt_news/202308/t20230804_39767.html) / [来源 2](https://xcxfy.hncourt.gov.cn/public/detail.php?id=1943) / [来源 3](https://www.wuzhi.gov.cn/zwxxgk/zfld/ysy/)
- 京津城际：北京南、亦庄、武清、天津、军粮城北、塘沽、滨海。 [来源 1](https://www.beijing.gov.cn/ywdt/gzdt/202412/t20241222_3970796.html)
- 京雄城际：北京西、北京大兴、大兴机场、固安东、霸州北、雄安。 [来源 1](https://zdzqgw.beijing.gov.cn/zqfw/bjdxgjjc/bjdxgjjcjb/202410/t20241012_3917918.html)
- 津兴城际：大兴机场、固安东、永清东、安次、胜芳、天津西。 [来源 1](https://zdzqgw.beijing.gov.cn/zqfw/bjdxgjjc/bjdxgjjcjb/202410/t20241012_3917918.html)
- 京唐城际：北京通州、燕郊、大厂、香河、宝坻、玉田南、唐山西、唐山。 [来源 1](https://www.beijing.gov.cn/ywdt/gzdt/202212/t20221229_2886544.html) / [来源 2](https://www.tsgxq.gov.cn/uploads/files/460bb6e797b5f775d01a16f4ab4876f1.pdf) / [来源 3](https://www.beijing.gov.cn/ywdt/gzdt/202512/t20251226_4366443.html)
- 京滨城际 · 宝坻至北辰段：宝坻、宝坻南、北辰。 [来源 1](https://www.beijing.gov.cn/ywdt/gzdt/202212/t20221229_2886544.html) / [来源 2](https://www.tj.gov.cn/sy/xwfbh/xwfbh_210907/202509/t20250916_7133866.html)
- 青荣城际：青岛北、城阳、即墨北、莱西、莱阳、海阳北、桃村北、牟平、威海北、威海、文登东、荣成、夏格庄。 [来源 1](https://www.12306.cn/mormhweb/zxdt/202202/t20220225_36975.html) / [来源 2](https://fgw.weihai.gov.cn/art/2014/11/7/art_8989_396826.html)

## 归属纠正与边界

上一轮已把广州长隆旧目录误列珠海纠正为广州，保留 `st-wikidata-q113231610`、坐标、车次及原始来源。珠海长隆保持另一独立站点，未合并。本轮不修改车站身份、位置或原有服务。

本轮新增沪宁、沪宁沿江、广肇两个分段、郑焦、京津、京雄、津兴、京唐、京滨建成段和青荣；补充广清南延广州白云、广惠北延惠州北及青荣夏格庄。京唐北京通州使用正式命名/开通公告核对，未按旧工程站名创建重复站点。

这是已核验的导航覆盖，不是全国城际线路全量清单。未收录线路或站点仍保留原有选择入口；没有把规划站或缺少正常服务证据的站点开放，也没有通过本轮归类新增客运服务。广肇目前只有已有服务证据的共有枢纽进入分组，张槎、顺德北、狮山等未开放站仍待逐站补核。市域线路与仅开行C字头的长途线路不能直接当作城际；济莱、成灌等需保留名称与运营性质差异，后续再决定目录类别。成绵乐等其他线路仍需补充当前运营站点的逐项来源。不同来源发布日期不等同于本站快照车次日期。

入口状态 `?city=...&group=intercity` 可刷新恢复。专属城际站的老 `?station=...` 自动识别归类；共有枢纽老链接保留外层入口。从城际中选择共有枢纽时用 `?station=...&group=intercity` 保留返回组。更改区域、省份、城市清空旧组；切换中心站返回当前组，返回全部车站把键盘焦点交还“城际铁路”按钮。首页仍按需加载完整网络。

## 最新入口补充

现另有“市内及周边小站”目录。未属于城际的站点不再一律散列外层；统一选择索引负责主要站与两种子目录。城际数据仍为36城/27线路分段/225独立站点。上海莘庄等归市域小站，不是城际。参见[小站导航规则](SMALL-STATION-CLASSIFICATION.md)。
