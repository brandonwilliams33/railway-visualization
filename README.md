# 沿线 · Railbound

铁路客运直达网络的静态网站。React + TypeScript strict + Vite + Tailwind + Leaflet；可部署到 GitHub Pages，无后端、API key 或运行时列车查询。

从已开放城市的客运车站出发，探索有公开客运服务依据的直达车站与铁路走廊。

| 独立车站选择 | 天河机场出发网络 | 手机布局 |
| --- | --- | --- |
| ![武汉的独立客运车站](docs/screenshots/preview-expanded-city.png) | ![天河机场站直达网络](docs/screenshots/preview-expanded-network.png) | ![手机端客运网络](docs/screenshots/preview-expanded-mobile.png) |

## 本地运行

需要 Node.js 24+、Python 3.10+。

```sh
npm ci
npm run dev
```

打开终端输出的本地地址即可预览。也可以运行 `npm run preview` 查看生产构建。

## 使用与开发

```sh
npm run data:build
npm test
npm run build
npm run preview
```

`npm run data:build` 从提交的清洗快照离线生成前端数据、GeoJSON 与审计报告，不需要下载全量轨道。重新获取轨道时，从下方 HOTOSM 来源下载并解压 GeoJSON，然后运行：

```sh
python3 scripts/preparePhysicalRails.py /absolute/path/railways.geojson --snapshot YYYY-MM-DD
npm run data:build
```

完整停站信息在 `data/raw/passenger-services.json`；每条记录保留来源 URL、日期与页面哈希。更新这些快照时必须重新核验中心站停站、公开客运属性和临客候选，不能仅更新日期。

## 已实现

打开首页先看主要客运车站地图。选择出发城市后，才显示该城市独立车站的下一步选择；选择车站后展开客运网络、类型/地区/城市或站名搜索、同步统计、站点详情及直达目录。目录可定位地图，轨道可查看来源与客运服务例子。提供手机布局、键盘操作、减少动画、可分享的 URL 筛选、旅行笔记与数据说明。

首页先加载站点登记表，完整客运网络仅在选择车站或查看数据说明时按需加载。默认底图与数据全部本地读取；“街道底图”由用户主动启用后请求 OSM 公共瓦片服务。主要站点来自本次收录的站点登记表，并非全国所有车站。

## 线路画法

所有缩放级别都把相近的铁路轨道并为共用客运走廊；从中心站到可见站点只保留一套清晰的连接骨架，去掉平行替代线和回环。全国视图显示主要站点；放大后每个车站都有独立标记与点击入口，不合并不同车站。点选目的地时高亮共用走廊中的到达路径，表示“可以到”，不表示特定列车逐站经过这里。这个显示图不参与直达判定。长距离少停站区间沿已收录的铁路走廊绘制，不用两个停站直接拉长线。

## 扩展范围与数据边界

已开放 149 个城市、1,249 个独立出发站，涵盖江苏、上海、浙江、安徽、山东、河南、湖北、江西、福建、北京、天津、河北、山西、湖南。各站可展开其直达全国目的地的网络，站点保持独立 ID、名称和坐标。逐市清单见 [扩展进度](docs/EXPANSION-PROGRESS.md)，暂停位置和续传步骤见 [接班说明](HANDOFF.md)。目录采集完成不代表覆盖官方全部现行车次。

- 接受 10,803 个客运服务，使用 1,962 个有来源坐标的车站。
- 已定位站点之间的 104,732 个服务区间全部具有连续绘图路径，未留下断线区间。线路只表达可达联系，不声明列车实际运行径路。
- 139 个全国目的站仍待坐标核验；原始停站事实保留，地图暂不显示，不以城市中心替代。96 个目录入口未开放，原因与明细见扩展进度。
- 黄渡独立站点仍保留；本轮仅有未取得普通售票证据的旅游候选，因此暂停其出发入口。牛车河、向阳、石城的错误所在地目录条目隔离；芦台归属纠正至天津。不同站点没有合并。
- 广州的43站目录与760条新增服务事实已保存，但该城市采集尚未完成，因此暂不开放广州出发入口。其完整单条服务事实可作为其他已开放出发站的证据。
- 隔离 137 个时间倒退服务、38 个速度/时间矛盾服务和 98 个异常站序记录；排除 3,498 个临客候选。

## 逐城市继续扩展

`data/raw/jiangsu-station-index.json` 保留江苏底稿；新增城市使用 `city-*-station-index.json` 和 `city-*-services.json`，并保存 URL、源日期及页面哈希。完整服务事实在城市间复用，出发站登记自动生成城市与站点入口。坐标只接受已核验的独立车站，不能用城市中心代替。

```sh
python3 scripts/acquireCity.py guangdong guangzhou 广东
npm run data:build
npm test
npm run build
```

当前广州还有发布隔离，先遵循 HANDOFF.md 的核验与解锁步骤，再构建。若有未定位站点，先用 `resolveStationCoordinates.py` 补坐标；`verifyCoordinateCandidates.py` 仅把英文坐标表当候选区域，再通过原始 OSM 对象上的中文站名验证；`acquireWikidataCoordinates.py` 配合明确的同名消歧义登记补充高精度铁路车站坐标。采集与坐标步骤需要联网，已提交快照的构建完全离线。

## 来源与许可

[Wikidata](https://www.wikidata.org/) 的结构化车站坐标使用 CC0；拒绝海外同名对象、消歧义页和粗略坐标。每个站点保留实际来源链接。

[铁路网江苏车站目录](https://www.crecc.com/jiangsu/)、[铁路网徐州站](https://www.crecc.com/jiangsu/xuzhou/xuzhou.html)、[徐州东站](https://www.crecc.com/jiangsu/xuzhou/xuzhoudong.html)：第三方公开时刻与完整停站页面，保存事实摘要，不复制页面全文。

[HOTOSM 中国铁路 / HDX](https://data.humdata.org/dataset/hotosm_chn_railways)：OSM/Geofabrik 轨道及站点快照，© OpenStreetMap contributors，[ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/)。`physical-rails.json`、轨道 GeoJSON 及关联衍生数据库按 ODbL 提供，来源引用通过 `physicalSources` 共享登记表完整保留，避免每个区段重复存储长列表。该登记表引用覆盖来源走廊，不代表每个 OSM way 都是当前区段的精确范围。

[railroutes 中国包](https://github.com/mayurrawte/railroutes/tree/main/packages/china)、[车站坐标补充](https://github.com/listenzcc/China-rail-way-stations-data)：辅助坐标；每站 `coordinateSource` 可追溯，中文 OSM 精确匹配优先。部分城市字段待核验，不用猜测填充。

[Natural Earth](https://www.naturalearthdata.com/)：公共领域行政区底图。软件代码许可见 `LICENSE`，第三方数据不适用软件许可。

## GitHub Pages

1. 将项目目录内容（包含 `.github`）推送到仓库的 `main` 分支。
2. 在仓库 Settings → Pages → Source 选择 **GitHub Actions**。
3. 推送 `main`，或手动运行 Deploy to GitHub Pages 工作流。
4. 部署成功后，在仓库 Pages 页面打开实际生成的网站链接。

构建使用相对资源路径 `base: './'`，支持仓库子目录和自定义域名。页面状态使用查询参数，无额外路由重写要求。工作流自动重新生成数据、运行单元测试、构建并部署 `dist`。

## 验证

`npm test` 验证去重、客运过滤、来源引用、同服务直达、全部已开放出发站及筛选一致性。`npm run test:e2e` 提供桌面/手机 Playwright 测试（首次需 `npx playwright install chromium`）。本次另用真实浏览器检查首页选择阶段、地图线形、搜索、详情、移动端和控制台；记录见 `VERIFICATION.md`。

## 文件

`src/components` 页面控件；`src/map` 地图；`src/travel` 笔记；`src/lib/network.ts` 可达关系与筛选；`scripts` 离线 ETL；`data/raw` 清洗快照；`data/railway-segments.geojson` 物理轨道；`data/audit.json` 审计；`.github/workflows/deploy.yml` 发布。
