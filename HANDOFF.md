# 接班说明 · 2026-10-10

本轮新增六个省区，收在西藏；全部采集、校验与打包完成。当前入口已覆盖大陆31个省级地区。下一步进入逐市补核小站与身份边界。未初始化 Git、未发布线上网站。

## 当前快照

开放 342 城市、3,095 个独立出发站；接受 19,019 个服务，使用 3,187 个有来源坐标的车站。156,287 个已定位停站区间都有连续绘图路径，缺失 0。尚有 6 个国内目的站待坐标或同名身份核验、275 个目录入口待核验；完整事实保留，不猜坐标、不开放空入口。

本轮完成内蒙古12、辽宁14、吉林9、黑龙江13、海南12、西藏5个源目录城市/行政单位的采集，六份省级采集审计的 failedCities 均为空。相比上一交付新增66个城市、649个独立出发站。目前入口覆盖大陆31个省级地区；目录覆盖不等于官方全部现行车次已穷尽。

已定位区间的 missingDrawingIntervals 为空、remainingUnmappedIntervals 为0。待定位的国内目的站为三家子、古城、桃山、盘古、艾家村、褚家湾。详细入口及原因见 docs/EXPANSION-PROGRESS.md、data/audit.json；275个 pending 不能直接理解为全部仍在运营的漏站，需分别验证坐标、身份与有效服务。

庆盛与南沙北、新塘与广州新塘是官方更名的同一车站；新塘南及其他不同车站保持独立 ID。没有合并不同站点。遵义南使用旧源快照站名，通过官方更名后的乌江寨站核验坐标；不要做全局“遵义南→乌江寨”别名，新建高铁站可能复用这个名称。

## 必须保持

首页地图为主，先城市再独立车站，再展示可直达全国的目的地。目的为理解“能到”；相近线形共享、去回环，但不可合并不同车站。完整同一客运服务的停站决定直达，绘图走廊不能制造直达。过夜少停站服务沿共用走廊，不能跨省长直线。

坐标不得用城市中心代替。临客、旅游候选、时间矛盾及身份冲突隔离。第三方时刻快照不能称为官方实时运行图。源日期2026-09-11、采集2026-10-10、轨道来源2026-05-10。

## 本轮修补

acquireCity.py 修复吉林市与吉林省代码同为 jilin 时误用省级直接目录的判断，重采全省九个城市完成；test_acquisition.py 保留嵌套目录回归。

acquireSnapshotStationObjects.py 从本地全量 HOTOSM 的独立站点节点获取候选 ID，再用 OSM 原始多节点 API 验证中文名称、station/halt、可见性及非地铁属性。每批保存完整原始证据；404批次分拆、网络失败有限重试。verified-coordinate-objects.json 保留原始对象，近似英文点不直接入库。不同程序不能同时写这个证据文件。

营盘水、长庆桥、阿拉山口按原始独立 OSM 点与铁路运营方/地方政府资料确认归属，补足粗略边界面的误判；证据见 coordinate-overrides.json。坐标没有用城市中心代替。

新增白阿、甘库、汤林、前抚、福前、鹤北、拉日等已建具名客运走廊；来源及完整服务例子见 corridor-review-evidence.json。省政府历史停运通知只用于证明线路办理客运，不作为当前停运规则。规划延伸、专用线及全量货运网不入库。test_reviewed_corridors.py 检查端点连续及绕路上限。

## 接下来优先做

1. 先查仍未开放的大站及特殊行政管理归属。加格达奇、劲松、古源等目录归属为黑龙江，而粗略省界面把独立点归为内蒙古；需要行政管理与站址的公开证据再处理，不能只为消除冲突改省份。
2. 三家子、桃山、四方台等同名原始对象分散在不同地点；逐项结合源车次、目录城市及铁路身份核验，不能按最近点合并。同省同名也必须核对独立身份。
3. 古城、盘古、艾家村、褚家湾等缺点继续补证；褚家沟与褚家湾是不同站，不能替代。完整停站保留。
4. 复核275个 pending 与44条失败页面审计，先查是否已在全局完整缓存或45份坏源排除登记；不能为清零删事实。无正常客运记录不自动等于永久停运。
5. 逐市更新源快照后，城市采集全部结束再同步坐标登记、生成和全量检查；只在最终稳定快照打包。

## 续传与验证

```sh
npm ci
# 针对实际需要补核的城市或省份运行采集器，复用缓存
python3 scripts/expandProvinces.py jilin:吉林
python3 scripts/auditUnavailableServices.py
python3 scripts/resolveStationCoordinates.py --csv /tmp/yanxian-coordinates/station.csv --admin ../../work/admin1.geojson --osm data/raw/verified-coordinate-objects.json
npm run data:build
python3 scripts/writeExpansionProgress.py
npm test
npm run build
```

本机可选快速找节点：

```sh
python3 scripts/acquireSnapshotStationObjects.py ../../work/hotosm/railways.geojson --names /absolute/path/station-names.json
```

输入名字为 JSON 字符串数组。全量轨道、本机 CSV 与 admin1.geojson 是更新时输入，不进入源码包；已提交快照的构建完全离线。resolveStationCoordinates.py 的 --osm 必须是带 elements 的原始对象，不能用英文候选数组。不同坐标证据写入程序顺序运行，生成必须等坐标同步完成。

逐市保存，每40份完整服务保留检查点；城市索引必须有 acquisition 才开放。省级文件只记录已完成城市及失败，不能单凭 failedCities 为空推断尚在运行的整省已经结束。中老 D83—D88 的海外站规则按车次、日期及磨憨/万象必要停站限定；国内同名站不误用海外坐标。

## 交付

12,430项Vitest与18项Python检查通过，生产构建通过。实际首页、沈阳10个独立入口、沈阳北603个直达站点、海口东28站及拉萨45站已检查。桌面1280、手机390无横向溢出，控制台无error。详见 VERIFICATION.md。

上一级 yanxian-expanded-source.zip、yanxian-expanded-pages.zip 及 canonical 两包同步；源码含原始事实、生成快照、工具、测试与 Pages 工作流，不含 node_modules、dist、缓存或临时输入。

交付时预览与采集进程均停止，没有自动续跑或定时任务。继续前先读本文件并核对实际额度，留足检查和打包余量。
