# 接班说明 · 2026-10-10 · 城际扩展与苹果式主题

此前完成“区域 → 省份 → 城市 → 独立车站”入口与黑龙江、宁夏补核。本轮继续城际归类并完成苹果式视觉主题，原有客运数据保持不变。开放342个城市、3,105个独立出发站，接受19,019个服务，使用3,193个有来源坐标的车站。156,306个已定位停站区间都有连续绘图路径，缺失0。已接受服务的国内停站坐标全部补齐；265个源目录入口仍待身份或正常客运记录核验。没有初始化Git、没有发布线上网站。

## 本轮城际归类

城际导航扩至36城、27条线路/运营分段、225个独立站点，本轮新增78个归类。选择城市后，“城际铁路”和主要站点并列，点击后按线路选择独立站点。仅导航归类，不合并站点，不修改同一服务直达规则。主要枢纽保留外层快捷入口，同站多线仅列一次附标签。详见docs/INTERCITY-CLASSIFICATION.md及src/data/intercity-groups.json。

src/lib/intercityIndex.ts严格校验ID、名称、省份；provinceIds数组支持跨省线路，按每站实际城市归类。group参数与原city/station参数兼容。共有枢纽老链接留在外层；从城际列表选枢纽时显式保存group，返回相应列表。更换父级清组；返回选站、刷新、旧分享链接均恢复适当入口。上一轮广州长隆旧目录从珠海纠正为广州，原ID/坐标/服务保留，珠海长隆独立。

本轮补入沪宁、沪宁沿江、郑焦、京津、京雄、津兴、京唐、京滨建成段、青荣和广肇分段，补充广州白云、惠州北与夏格庄。广东广肇专属小站仍需正常客运服务与坐标验证；其他城际线路可继续逐条核验。市域线路不能仅凭C字头归为城际。不添加缺乏正常服务验证的站点。全量12,487项Vitest和20项Python通过，严格类型与生产构建通过。

视觉主题已统一重写src/styles.css，采用冷白、系统字体、蓝色选中态；RailMap只换配色和阅读提示，不改变共用走廊逻辑。index.html主题色和站点图标同步。桌面城际导航与列表并列，手机长列表限制140px高度，地图44px控件保持可点。设计方案见docs/DESIGN.md；最终截图preview-apple-*，具体实测见VERIFICATION.md。

## 入口与站点原则

首页保持地图为主，先选择华北、东北、华东、华中、华南、西南、西北，再选省份、城市，最后选独立车站。只有车站选定后才显示直达全国的网络。更改父级清空下级；原有city/station分享链接自动推导所属区域和省份，未选完的region/departureProvince也可刷新恢复。departureProvince与目的地筛选province分开。

src/lib/departureIndex.ts维护大区与省级代码，开放城市动态来自验证后的origins。仅显示有开放入口的地区，港澳台分类预留但当前不显示空组。新增省级代码需明确归组，不能悄悄丢失。不同城市ID、站点ID保持独立；苏州与宿州仍分省，古城与古城镇、褚家湾与褚家沟不混同。

本项目目的为理解“能到”：相近线形共用、去回环，不能合并不同站点。完整同一服务停站决定直达，绘图走廊不能制造直达。少停站及过夜服务沿共用走廊，不跨省拉长直线；坐标不能用城市中心或区间插值代替。

第三方时刻快照不是官方实时运行图。源日期2026-09-11、采集2026-10-10、轨道来源2026-05-10。临客、旅游候选、时间矛盾、坏源及身份冲突继续隔离；无正常记录不自动等于永久停运。

## 此前站点补核

新增10个独立入口：加格达奇、劲松、古源、小扬气、新天、桃山、古城、盘古、艾家村、褚家湾。相比上一版国内待定位目的站6个减少为0。四方台的绥化独立对象已核验，但候选记录未形成已接受正常客运服务，仍保留pending入口。

- station-identity-reviews.json：加格达奇等5站按政府资料确认的黑龙江大兴安岭行政管理归属分类，保留地理省界内蒙古、原ID、坐标与坐标来源。resolveStationCoordinates.py应用校正前锁定ID、坐标及坐标来源，防止改成另一个同名对象。
- homonym-coordinate-reviews.json：桃山选国铁绥化车务段60239，四方台选59879，三家子选国铁通辽车务段53373。结合目录城市、运营方、完整服务邻站序列与公开身份资料，保留其他矿业或外省同名原始对象，没有合并。三家子的城市判断明确记为证据推断。
- origin-index-corrections.json：古城的北京条目纠正为齐齐哈尔、盘古的重庆条目纠正为大兴安岭、褚家湾的固原条目纠正为中卫；原始目录记录仍保留。前两站已有独立坐标，却因源目录错误被省份过滤挡住，不能误判成没有坐标。
- ningxia-coordinate-review.json：宁夏小范围精确中文OSM查询取得艾家村node/2662698002、褚家湾node/11938234794，两者为独立railway=halt对象，与12306站址及政府公布现状站序核验。2024扩能工程的计划关站不直接当成当前停运证据。

上一轮已完成内蒙古12、辽宁14、吉林9、黑龙江13、海南12、西藏5个源目录城市的采集，现覆盖大陆31个省级地区。吉林市/吉林省同代码的嵌套目录修复仍保留回归。白阿、甘库、汤林、前抚、福前、鹤北、拉日具名客运走廊及证据保留。

## 接下来优先做

1. 逐市复核265个pending：分清无正常服务、身份矛盾及剩余未接受候选的缺点。大扬气、松树林、白桦排、翠峰的特殊行政管理归属仍需逐站补证，不能扩大本轮5站校正名单。
2. 检查其他同省错市目录条目，先取得独立站址依据，再用针对具体sourceCityId的校正。12306旧地址是身份资料，不是实时车次依据。
3. 44条失败页面审计和45份坏源隔离保留；优先查全局完整缓存，不能为了清零删除源事实。四方台只解决了身份与坐标，未取得正常服务时不开放。
4. 完整网络按需块约53.7MB、gzip约9.15MB。后续可按出发站拆分以改善首次网络下载与解析；首页继续仅载概览。不要用删除跨省直达事实来缩小文件。

## 续传与验证

```sh
npm ci
# 按实际要更新的城市或省份复用缓存采集
python3 scripts/expandProvinces.py jilin:吉林
python3 scripts/auditUnavailableServices.py
python3 scripts/resolveStationCoordinates.py --csv /tmp/yanxian-coordinates/station.csv --admin ../../work/admin1.geojson --osm data/raw/verified-coordinate-objects.json
npm run data:build
python3 scripts/writeExpansionProgress.py
npm test
npm run build
```

每市独立保存索引、服务与acquisition，服务每40份保留检查点；城市采集全部结束后再同步坐标并生成。省级failedCities为空不表示尚在运行的采集已结束。

本机全量HOTOSM ../../work/hotosm/railways.geojson、admin1.geojson及CSV是更新输入，不进入源码包；已保存快照可以离线构建。acquireSnapshotStationObjects.py按本地独立节点ID分批获取原始OSM中文站点；acquireNamedStationObjects.py支持小范围精确中文node/way/relation查询。resolveStationCoordinates.py的--osm必须是带elements的原始对象，不能传英文候选数组。不要让两个程序同时写verified-coordinate-objects.json；生成和测试等写入结束后再做。

中老D83—D88海外5站按车次、日期和必要停站限定，完整源序列保留；本轮国内停站补齐不表示海外站入图。营盘水、长庆桥、阿拉山口等已有证据校正继续保留。庆盛/南沙北、新塘/广州新塘是官方更名同一车站，新塘南独立；遵义南旧源通过乌江寨核验，不能做全局更名别名，未来高铁站可能复用旧名。

## 交付与检查

精确检查结果见VERIFICATION.md。本轮截图使用docs/screenshots/preview-apple-{landing,city,intercity,network,mobile}.jpg；此前城际截图preview-intercity-*保留；上轮区域索引截图docs/screenshots/preview-index-{landing,city,network,mobile}.png保留；preview-expanded等旧截图留作历史证据。区域/省份清空、旧链接恢复、全部出发站缩放6/8连通、完整同一服务直达、类型分区及来源引用均检查。

上一级yanxian-expanded-source.zip与yanxian-expanded-pages.zip为本轮快照，canonical的yanxian-source.zip与yanxian-pages.zip同步。源码包含原始事实、生成快照、校正证据、工具、测试和Pages工作流，不含node_modules、dist、缓存或临时输入；Pages包以dist内容为根。

交付时停止预览和采集，无定时任务。下一轮先读本文件并查看实际额度，留足验证、说明和打包余量。

## 最新修正：小站归纳

用户明确城际只是小站归纳的一种。新增stationChoiceIndex统一两种组，group类型为intercity/local。303城、2,225个小站自动收进local；上海11小站，其中8站按有来源的金山铁路市域线路列出，其他3站不猜线路。主站依据旧major、已核验保留入口及服务数>=100；缺少主站的城市保留一个直接入口。此规则不是官方站级或市内服务限制。全部3,105站仍可选。资料见docs/SMALL-STATION-CLASSIFICATION.md。后续优先精化主站白名单和市域线路依据，不能把local都叫城际。原城际目录225站不变；参考最新preview-local-*截图，preview-apple-*保留为上一轮主题证据。
