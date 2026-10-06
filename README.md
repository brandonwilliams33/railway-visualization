# 沿线 · Railbound

铁路客运直达网络的静态网站。React + TypeScript strict + Vite + Tailwind + Leaflet；可部署到 GitHub Pages，无后端、API key 或运行时列车查询。

从徐州站或徐州东站出发，探索有公开客运服务依据的直达车站与铁路走廊。

| 全国概览 | 徐州东站客运网络 | 手机布局 |
| --- | --- | --- |
| ![全国铁路站点概览](docs/screenshots/preview-home.jpg) | ![徐州东站客运网络地图](docs/screenshots/preview-network.jpg) | ![手机端客运网络](docs/screenshots/preview-mobile-network.jpg) |

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

打开首页先看主要客运车站地图。选择出发城市徐州后，才显示徐州站、徐州东站的下一步选择；选择车站后展开客运网络、类型/地区/城市或站名搜索、同步统计、站点详情及直达目录。目录可定位地图，轨道可查看来源与客运服务例子。提供手机布局、键盘操作、减少动画、可分享的 URL 筛选、旅行笔记与数据说明。

首页先加载站点登记表，完整客运网络仅在选择车站或查看数据说明时按需加载。默认底图与数据全部本地读取；“街道底图”由用户主动启用后请求 OSM 公共瓦片服务。主要站点来自本次收录的站点登记表，并非全国所有车站。

## 线路画法

全国概览合并邻近的线路走廊、柔化转折并只显示主要站点；区域放大逐步展开小站与细节。这个显示图只负责画法，不参与直达判定。点选目的地时高亮一条代表性客运路径，其余线路淡化，避免不同车次的绕行同时挤在地图上。长距离少停站区间不直接连接两个停站；保持已有路径或留空。几何仍可作为画法依据，无需在概览逐轨道还原。

## 数据与边界

- 接受 1,019 个公开客运服务；徐州站 505 个直达站，徐州东站 521 个直达站。
- 去重物理轨道区段 4,656 个；几何来自 OSM 原始轨道，约 30 米简化。
- 直达目的地只能来自**同一趟**经过中心站的完整停站记录，不通过图寻路创造换乘直达。
- 轨道匹配只使用审查过的具名客运干线、高铁及城际走廊，排除货运专线、车辆段、专用线等；不是把全国物理铁路直接加入网络。
- 原始轨道线形是真实地理数据，但站点投影和受约束寻路是推断匹配，**尚非逐车次已核验运行径路**。9,955 条客运区间记录匹配成功，5,851 条未匹配（按服务计数，含重复区间），不画直线补齐。线路覆盖不完整；仍可显示有公开服务依据的直达站点。
- 临客候选排除 201 条，非客运 5 条，异常重复停站序列 3 条；8 个站点无法可靠定位，1 个服务页面获取失败，详见 `data/audit.json`。
- 时刻表源日期 2026-09-11；轨道快照 2026-05-10。非实时完整运行图，无余票与开行保证。购票以 12306 为准。

## 来源与许可

[铁路网徐州站](https://www.crecc.com/jiangsu/xuzhou/xuzhou.html)、[徐州东站](https://www.crecc.com/jiangsu/xuzhou/xuzhoudong.html)：第三方公开时刻与完整停站页面，保存事实摘要，不复制页面全文。

[HOTOSM 中国铁路 / HDX](https://data.humdata.org/dataset/hotosm_chn_railways)：OSM/Geofabrik 轨道及站点快照，© OpenStreetMap contributors，[ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/)。`physical-rails.json`、轨道 GeoJSON 及关联衍生数据库按 ODbL 提供，来源引用通过 `physicalSources` 共享登记表完整保留，避免每个区段重复存储长列表。该登记表引用覆盖来源走廊，不代表每个 OSM way 都是当前区段的精确范围。

[railroutes 中国包](https://github.com/mayurrawte/railroutes/tree/main/packages/china)、[车站坐标补充](https://github.com/listenzcc/China-rail-way-stations-data)：辅助坐标；每站 `coordinateSource` 可追溯，中文 OSM 精确匹配优先。部分城市字段待核验，不用猜测填充。

[Natural Earth](https://www.naturalearthdata.com/)：公共领域行政区底图。软件代码许可见 `LICENSE`，第三方数据不适用软件许可。

## GitHub Pages

1. 将项目目录内容（包含 `.github`）推送到仓库的 `main` 分支。
2. 在仓库 Settings → Pages → Source 选择 **GitHub Actions**。
3. 推送 `main`，或手动运行 Deploy to GitHub Pages 工作流。
4. 部署成功后访问 `https://brandonwilliams33.github.io/railway-visualization/`。

构建使用相对资源路径 `base: './'`，支持仓库子目录和自定义域名。页面状态使用查询参数，无额外路由重写要求。工作流自动重新生成数据、运行单元测试、构建并部署 `dist`。

## 验证

`npm test` 验证去重、客运过滤、来源引用、同服务直达、两个中心站及筛选一致性。`npm run test:e2e` 提供桌面/手机 Playwright 测试（首次需 `npx playwright install chromium`）。本次另用真实浏览器检查首页选择阶段、地图线形、搜索、详情、移动端和控制台；记录见 `VERIFICATION.md`。

## 文件

`src/components` 页面控件；`src/map` 地图；`src/travel` 笔记；`src/lib/network.ts` 可达关系与筛选；`scripts` 离线 ETL；`data/raw` 清洗快照；`data/railway-segments.geojson` 物理轨道；`data/audit.json` 审计；`.github/workflows/deploy.yml` 发布。
