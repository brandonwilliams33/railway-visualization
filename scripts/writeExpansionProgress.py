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
    if audit.get('outOfScopeStations'):
        lines.extend(['完整国际车次事实中保留以下海外站，本轮地图暂不收录：'+'、'.join(audit['outOfScopeStations'])+'。它们与国内坐标待核验分开记录。',''])
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
    lines.extend(['上海松江、莘庄等独立车站保持自己的身份；目录记录与本站直达关系分别核验。','',
        '客运服务来自第三方公开时刻快照，源日期不保证当天开行。线路只用于阅读，不作为逐车次实际径路。','',
        '## 已完成源目录采集','',
        '| 省份代码 | 已完成目录城市数 | 失败城市数 |','| --- | --- | --- |'])
    for path in sorted((ROOT/'data/raw').glob('province-*-acquisition.json')):
        record=json.loads(path.read_text())
        lines.append(f"| {path.name.removeprefix('province-').removesuffix('-acquisition.json')} | {len(record['completedCities'])} | {len(record['failedCities'])} |")
    lines.extend(['','## 后续续传','',
        '每市独立保存目录、完整服务事实及采集审计。只有已生成城市采集审计的入口才参与生成；中途暂停从已保存的事实续传，不重新从零抓取。具体下一批及验收步骤见 HANDOFF.md。','',
        '完整停站区间以共用路径索引保存，加载时还原各服务自己的区间，不改变不同站点身份及直达判定。官方更名的同一车站可搜索曾用名；新塘南与广州新塘仍独立。',''])
    (ROOT/'docs/EXPANSION-PROGRESS.md').write_text('\n'.join(lines))

if __name__=='__main__':
    write_progress()
