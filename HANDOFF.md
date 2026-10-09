# 接班说明 · 2026-10-09

本轮扩展收在新疆，剩余额度留给全量检查与打包。下一批从内蒙古开始。未初始化 Git、未发布线上网站。

## 当前快照

开放 276 城市、2,446 个独立出发站；接受 17,365 个服务，使用 2,765 个有来源坐标的车站。146,031 个已定位停站区间都有连续绘图路径，缺失 0。尚有 12 个国内目的站待坐标核验、161 个目录入口待核验；完整事实保留，不猜坐标、不开放空入口。

本轮完成广西14、云南14、贵州9、甘肃12、宁夏5、青海4、新疆20个源目录城市/行政单位的采集，七份省级采集审计的 failedCities 均为空。相比上一交付新增75个城市、573个独立出发站。目录覆盖不等于官方全部现行车次已穷尽。

已定位区间的 missingDrawingIntervals 为空、remainingUnmappedIntervals 为0。坐标及目录入口待核验列表见 docs/EXPANSION-PROGRESS.md 与 data/audit.json。

庆盛与南沙北、新塘与广州新塘是官方更名的同一车站；新塘南及其他不同车站保持独立 ID。没有合并不同站点。遵义南使用本次旧源快照站名，通过官方更名后的乌江寨站核验坐标；不要做全局“遵义南→乌江寨”别名，新建高铁站可能复用“遵义南”名称，未来更新须区分独立身份。

## 必须保持

首页地图为主，先城市再独立车站，再展示可直达全国的目的地。目的为理解“能到”；相近线形共享、去回环，但不可合并不同车站。完整同一客运服务的停站决定直达，绘图走廊不能制造直达。过夜少停站服务沿共用走廊，不能跨省长直线。

坐标不得用城市中心代替。临客、旅游候选、时间矛盾及身份冲突隔离。第三方时刻快照不能称为官方实时运行图。源日期2026-09-11、采集2026-10-09、轨道来源2026-05-10。

## 继续步骤

```sh
npm ci
python3 scripts/expandProvinces.py neimenggu:内蒙古
python3 scripts/auditUnavailableServices.py
# 全部城市采集结束后，再同步独立站点城市归属（此处为本机输入路径）
python3 scripts/resolveStationCoordinates.py --csv /tmp/yanxian-coordinates/station.csv --admin ../../work/admin1.geojson --osm data/raw/verified-coordinate-objects.json
npm run data:build
python3 scripts/writeExpansionProgress.py
npm test
npm run build
```

逐市采集、复用缓存；城市索引必须有 acquisition 才开放，中途暂停保留每40条的完整服务检查点。省级文件仅记录已完成城市及失败，不单凭 failedCities 为空推断整个省已跑完；核对省目录和采集进程。缺坐标保持 pending。最终生成后核对区间缺失0，再更新包和统计。

本机坐标输入：/tmp/yanxian-coordinates/station.csv、工作区 work/admin1.geojson；精确中文对象文件 data/raw/verified-coordinate-objects.json。resolveStationCoordinates.py 的 --osm 必须是带 elements 的对象，不能用英文候选数组。acquireNamedStationObjects.py 获取 node/way/relation 原始对象及独立点/中心；英文粗略坐标只定位检索区域，中文身份必须在原始对象确认。Wikidata 消歧义页和粗略点不直接定位。不同程序不能同时写同一坐标证据文件；离线构建部署不需要临时输入。

## 本轮修补与核验边界

OSM 同名候选先过滤国家及已确认目录省份，再判断距离歧义，避免海外中文同名对象遮蔽国内真实车站。证据不足的同名地点保持待核验。原始对象与官方坐标覆盖登记均保留来源。

中老 D83—D88 的2026-09-11快照依据12306规则区分万象等5个海外停站；规则同时匹配车次、日期和磨憨/万象停站，不能全局禁用某个站名。完整序列保留，国内直达映射不误用海外同名站。serviceScope.py 与 service-geographic-scope.json 留规则及回归。

本轮补齐大瑞、内六（含OSM组合名称）、酒额、天平/天华、平汝等具名已建客运走廊；不纳入在建段、煤矿专用线和全量货运网。旧大河沿高普联络线逐项例外保留，其他未核验联络线仍排除。证据在 corridor-review-evidence.json，回归在 test_reviewed_corridors.py。

目录错误归属按 origin-index-exclusions.json 隔离；高密北、芦台修正归属且保留独立ID。牛车河、向阳、石城错误城市条目不开放，石城东独立。岔江等跨省目录身份冲突也保持待核验。

43份不完整源快照留哈希和原因，完整重取结果保存到 city-service-recovery-services.json。历史失败页面42条仍如实保留；失败审计与坏页源日期可能不同，先对照全局缓存及排除文件，不能为清零而删除事实。

## 交付

全量检查及生产页面证据见 VERIFICATION.md；源包含原始事实、生成快照、工具、测试和Pages工作流。上一级 yanxian-expanded-source.zip、yanxian-expanded-pages.zip，canonical两包同步；源包不含node_modules/dist/临时文件。

采集全部结束；交付时预览停止，没有定时任务或后台扩展。下一次先读本文件、核对实际额度与审计，再从内蒙古继续。
