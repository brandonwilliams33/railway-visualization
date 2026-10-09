# 接班说明 · 2026-10-09

本轮扩展收在陕西，额度剩余用于检查与打包。下一批从广西开始。未初始化 Git、未发布线上网站。

## 当前快照

开放 201 城市、1,873 个独立出发站；接受 15,492 个服务，使用 2,457 个有来源坐标的车站。135,799 个已定位停站区间都有连续绘图路径，缺失 0。尚有 54 个目的站待坐标核验、118 个目录入口待核验；完整事实保留，不猜坐标、不开放空入口。

在原149城市、1,249个入口基础上，本轮完成广东21个、重庆1个、四川20个、陕西10个源目录城市/行政单位。广州已解除历史暂停；四个 province-*-acquisition.json 的 failedCities 均为空。目录覆盖不等于官方全部现行车次已穷尽。

庆盛与南沙北、新塘与广州新塘是官方更名的同一车站，已统一曾用名检索；新塘南及其他不同车站均保留独立 ID，不合并站点。 证据：station-name-evidence.json，名称规范化：stationNames.py。原始服务来源站名保留，展示使用官方现名。

## 必须保持

首页地图为主，先城市再独立车站，再展示可直达全国的目的地。目的为理解“能到”；相近线形共享、去回环，但不可合并不同车站。完整同一客运服务的停站决定直达，绘图通道不能制造直达。过夜少停站服务沿共享走廊，不能跨省长直线。

坐标不得用城市中心代替。临客、旅游候选、时间矛盾及身份冲突隔离。第三方时刻快照不能称为官方实时运行图。源日期 2026-09-11、采集 2026-10-09，轨道来源2026-05-10。

## 继续步骤

```sh
npm ci
python3 scripts/expandProvinces.py guangxi:广西
python3 scripts/auditUnavailableServices.py
npm run data:build
python3 scripts/writeExpansionProgress.py
npm test
npm run build
```

逐市采集、复用缓存；城市索引必须有 acquisition 才开放，中途暂停保留每40条的完整服务检查点。原始文件原地续传，不从零重抓。新增坐标需核验后再生成，缺坐标保持 pending。生成审计 missingDrawingIntervals 必须为空，remainingUnmappedIntervals 必须为0，再更新包和统计。

本机坐标输入：/tmp/yanxian-coordinates/station.csv、工作区 work/admin1.geojson；精确中文对象文件 data/raw/verified-coordinate-objects.json。resolveStationCoordinates.py 的 --osm 必须是带 elements 的对象，不能用英文候选数组。acquireNamedStationObjects.py 精确中文节点；acquireWikidataCoordinates.py 保留旧证据；不要同时运行多个写同一坐标文件的程序。离线构建部署不需要这些临时输入。

## 核验边界

目录错误归属按 origin-index-exclusions.json 隔离；高密北更正山东潍坊、芦台更正天津，保留站点 ID。牛车河、向阳、石城错误城市条目不开放，石城东独立。

34 份不完整源快照在 service-source-exclusions.json 留哈希；完整重取结果在 city-service-recovery-services.json。审计保留 33 条历史失败页面记录，续查先对照全局缓存，避免重复下载。全部坐标、客运不足和身份问题详见 docs/EXPANSION-PROGRESS.md 与 data/audit.json。

本轮补齐广大/楚大/滇藏已建客运走廊与大河沿高普联络线。大河沿是逐项证据例外，其他联络线、货运网仍排除；不全量引入瓦日等货线。客运证据在 corridor-review-evidence.json，回归在 test_reviewed_corridors.py。

## 交付

全量检查及生产页面证据见 VERIFICATION.md；上下游工具与原始事实完整包含源包，Pages 工作流配置已有。交付在上一级 yanxian-expanded-source.zip、yanxian-expanded-pages.zip；canonical 两包同步。源包不含 node_modules/dist/临时文件。

采集全部停止，最终预览也在交付时停止；没有定时任务或后台扩展。下次先读本文件、核对实际额度与审计，再从广西继续。
