# 接班说明 · 2026-10-08

用户已要求暂停扩展。此轮完成收尾，不继续后台采集；下次收到继续指令后从广州接起。项目根目录就是本文件所在目录，未初始化 Git，未发布线上网站。

## 必须保持的项目宗旨

首页以主要站点地图为主，先选城市，再选该城市的独立车站，之后展示可直达全国的目的地。不要提前展开路线与全部筛选。目的是理解“能到”，共用、合并相近线路以提升可读性，可以适当牺牲线形真实性；不能合并车站。完整同一客运服务的停站事实决定直达，绘图走廊不能制造直达关系。过夜、少停站服务沿共享通道绘制，不直接拉跨省长直线。

以正常公开售票的客运服务为范围；临客、旅游候选、异常时间与目录所在地矛盾需要独立证据。不能用城市中心假装车站坐标，不要将第三方时刻快照说成官方实时完整运行图。

## 本次可交付快照

- 开放 149 城市、1,249 个独立出发站；10,803 个完整客运服务；地图使用 1,962 个有来源坐标的车站。
- 已定位站点之间 104,732 个服务区间均有连续绘图路径，缺失0；每个出发站在缩放6/8均检查可见站点连通，另有旧徐州、南京南、苏州的筛选组合。
- 江苏13市、浙江10市、安徽16市、山东16市、河南18市、湖北17个目录城市/行政单位、江西11市、福建9市、河北11市、山西11市、湖南14个目录城市/行政单位、北京、天津、上海。具体开放站数以 docs/EXPANSION-PROGRESS.md 为准，不能说这些省的全部当前车站/车次已穷尽。
- 广州暂未开放入口，见下面续传说明；全国其他目的地仍可出现广州站等独立车站。
- 上海18个开放入口。黄渡独立登记仍保留，但仅有未核验普通售票的旅游服务候选，因此暂不开放。不存在合并站点。
- 源时刻更新2026-09-11，采集2026-10-08；轨道来源快照2026-05-10。所有离线构建输入均在源包中，不依赖临时采集文件或运行时在线查询。

## 广州断点：不要丢弃或重新从零抓取

`data/raw/city-guangdong-guangzhou-station-index.json` 保存43个目录站，目录候选总计4,027个车次。已有跨城市缓存1,973个候选事实，其中本市新增文件保存760条；还剩2,054个候选尚未抓取。本轮日志中的2,814表示开始时需要新增采集的数量，不是总候选数。

`data/raw/expansion-release.json` 的 `pausedCityIds` 含 `guangdong-guangzhou`，`originSources.indexes()` 会阻止该城市提前开放；其已完整取得的单条服务事实仍可支撑其他城市。`city-guangdong-guangzhou-acquisition.json` 尚未生成，这是中途暂停，不是采集完成。

下次先执行：

```sh
python3 scripts/acquireCity.py guangdong guangzhou 广东
```

采集结束后检查该市 acquisition 的 failedPages、stationIssues，再补查坐标。确认失败请求已补查或逐项记录排除依据后，只从 expansion-release.json 的 pausedCityIds 删除 `guangdong-guangzhou`，保留其他项；否则不得解锁入口。接着依次运行：

```sh
npm run data:build
python3 scripts/writeExpansionProgress.py
npm test
npm run build
```

确认 `data/audit.json` 的 missingDrawingIntervals 为空、remainingUnmappedIntervals 为0，以及新出发站均有合法服务和坐标，才更新交付包和统计。未定位车站要保持 pending，不做空入口。建议广州收尾后逐市继续广东，再重庆、四川、陕西、广西；原先这一批尚未进入这些后续省份。`expandProvinces.py` 会顺序遍历省内城市并复用缓存，但仍需每市验收，不要把抓完页面当成完成发布。

## 待核验项和已知边界

当前有96个未开放目录入口：64个坐标待核验、31个正常客运记录不足、1个身份归属冲突（高密北）。139个接受服务中的全国目的站尚无可信坐标，地图暂不显示。具体名字见扩展进度及 data/audit.json。不要为了让统计变成零而猜坐标或删除原始停站。

`data/raw/pause-city-issues.json` 汇总35份城市历史采集审计里的失败/站点问题；其中部分服务已由后续城市补齐，续查前对照全局缓存，避免重复抓取。当前生成审计保存23条失败页面记录。

牛车河的淄博目录、向阳的许昌目录、石城的赣州目录按所在地矛盾隔离；芦台更正为天津。证据在 origin-index-exclusions.json、origin-index-corrections.json。石城东是另一个江西车站，保留独立。原始目录记录不删除。

坐标工作脚本：resolveStationCoordinates.py、acquireWikidataCoordinates.py、verifyWikidataCandidates.py、verifyCoordinateCandidates.py。精确中文OSM车站对象/高精度铁路Wikidata可接受，英文表或粗略Wikidata只能提示候选区域，需独立中文身份核验。当前机器的辅助输入是 `/tmp/yanxian-coordinates/station.csv`、工作区 `work/admin1.geojson`；后续机器需重新准备来源，离线生成/部署不需要它们。不要同时运行多个坐标文件写入程序。

新增走廊审查在 passengerCorridors.py 和 corridor-review-evidence.json。最后修复邯长、哈佳区间；回归还覆盖牙克石—齐齐哈尔避免绕到哈尔滨、达万、干武、辛泰等。只补实际需要的经核验客运走廊，不能整体引入货运网。

## 验证与交付

5,045项Vitest、14项Python检查通过，TypeScript与正式构建通过。一次全量引用检查因数据增长超过原5秒限制，保留全部断言并仅将这一项超时调整为30秒，重跑全部检查通过。

实际生产页面核对首页地图/城市阶段、武汉10个独立入口和天河机场21个目的站、3个省级地区、29个服务；桌面1280、手机390宽均无横向溢出，控制台无error。证据在 docs/screenshots/，正式记录见 VERIFICATION.md。

网络数据共享完整服务路径索引，前端解码后恢复逐服务区间；约36.87 MB原始数据、gzip6.46 MB，按需加载。首次打开服务网络仍有下载与解析成本，后续可按区域拆分，但不能丢失跨省服务。页面首页只读取概览。

上一级目录的 yanxian-expanded-source.zip 与 yanxian-expanded-pages.zip 是本次源包和静态部署包；yanxian-source.zip 与 yanxian-pages.zip 同步为同一版本。源包不包含 node_modules、dist 与临时文件，Pages包包含dist根目录文件。运行 npm ci 后可离线生成快照、测试及构建；Pages工作流已经配置。

本轮采集与预览服务均在交付前停止，没有定时任务、后台继续扩展或自动发布。用户下一次说继续，先阅读本文件，核对当前审计和额度，再处理广州断点。
