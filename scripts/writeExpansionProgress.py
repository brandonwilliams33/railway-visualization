"""Write the expansion ledger from the exact generated, deployable snapshot."""
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def write_progress():
    data=json.loads((ROOT/'src/data/overview.json').read_text())
    audit=data['audit'];origins=data['origins']
    cities=Counter((o['province'],o['city']) for o in origins)
    lines=[f"# 扩展进度 · {data['retrievedAt']}",'',f"已开放 {len(cities)} 个城市、{len(origins)} 个独立出发站，可查看它们可直达的全国目的地。",'',
           '| 省份 | 城市 | 独立出发站 |','| --- | --- | --- |']
    lines.extend(f'| {province} | {city} | {count} |' for (province,city),count in sorted(cities.items()))
    intervals=audit['matchedPhysicalIntervals']+audit['unmatchedPhysicalIntervals']
    lines.extend(['','## 核验边界','',f"接受 {audit['acceptedServices']:,} 个客运服务，使用 {len(data['stations']):,} 个有来源坐标的车站。{intervals:,} 个服务区间；尚未补齐绘图路径 {audit['remainingUnmappedIntervals']} 个。",''])
    if audit['unlocatedStations']:
        lines.extend(['尚未定位的全国目的站：'+'、'.join(audit['unlocatedStations'])+'。保留原始停站事实；地图暂不显示这些站。',''])
    else:
        lines.extend(['已接受服务中的全部停站均已定位。',''])
    if audit['pendingOrigins']:
        lines.extend(['尚未开放的目录站点：','', '| 车站 | 待核验原因 |','| --- | --- |'])
        reasons={'station identity conflicts with catalogue':'目录归属与独立车站身份矛盾，待核验','coordinate missing':'独立车站坐标待核验','no validated regular passenger service':'本轮未取得可核验的正常客运记录'}
        lines.extend(f"| {entry['name']} | {reasons.get(entry['reason'],entry['reason'])} |" for entry in audit['pendingOrigins'])
        lines.append('')
    exclusion_path=ROOT/'data/raw/origin-index-exclusions.json'
    if exclusion_path.exists():
        lines.extend(['存在所在地矛盾的目录条目另行隔离：',''])
        for item in json.loads(exclusion_path.read_text()):
            lines.append(f"- {item['name']}：暂不开放 {item['cityId']} 的目录入口。{item['reason']} [身份核验]({item['identityUrl']})；原始目录记录保留。")
        lines.append('')
    correction_path=ROOT/'data/raw/origin-index-corrections.json'
    if correction_path.exists():
        for item in json.loads(correction_path.read_text()):
            lines.extend([f"{item['name']}：依据[所在地证据]({item['identitySource']})纠正为 {item['province']} {item['city']}，保留独立站点身份。",''])
    lines.extend(['上海目录的16站之外，依据完整服务停站表补充上海松江、莘庄2个独立入口。黄渡独立登记保留；仅有未核验普通售票的旅游候选，本轮暂不开放出发入口。未将车站合并。','',
        '客运服务来自第三方公开时刻快照，源日期不代表保证当天开行。线路只用于阅读，不作为逐车次实际径路。','',
        '## 后续续传','',
        '广东、重庆、四川、陕西目录采集已完成；下一批从广西继续，先阅读 `HANDOFF.md`。未完成 acquisition 的城市不会开放入口。每市独立保存 `city-*-station-index.json`、`city-*-services.json` 与采集审计；已完成城市复用服务事实。城市间顺序采集，失败站点可续传补查。完整停站区间以共用路径索引保存，加载时还原服务自己的区间，不改变站点身份或直达判定。','',
        '```sh','python3 scripts/expandProvinces.py guangxi:广西','python3 scripts/writeExpansionProgress.py','```',''])
    (ROOT/'docs/EXPANSION-PROGRESS.md').write_text('\n'.join(lines))

if __name__=='__main__':
    write_progress()
