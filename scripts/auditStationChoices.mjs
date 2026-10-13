import {createServer} from 'vite';
import {writeFile} from 'node:fs/promises';

// Read the same TypeScript index and overview function used by the application.
const server=await createServer({server:{middlewareMode:true},appType:'custom'});
try {
 const {origins,departureCities,stationChoiceIndex,getOverview}=await server.ssrLoadModule('/src/lib/network.ts');
 const errors=[];
 const sortedIds=stations=>stations.map(s=>s.id).sort();
 const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 const rows=departureCities.map(city=>{
  const choice=stationChoiceIndex.city(city.id),view=getOverview(city.id);
  const expected=origins.filter(s=>s.cityId===city.id);
  const nested=choice.groups.flatMap(g=>g.stations);
  const accessible=new Set([...choice.primary,...nested].map(s=>s.id));
  const primaryIds=new Set(choice.primary.map(s=>s.id));
  const hidden=nested.filter(s=>!primaryIds.has(s.id));
  const check=(okay,message)=>{if(!okay)errors.push(`${city.id}: ${message}`)};
  check(equal(sortedIds(choice.all),sortedIds(expected)),'city index differs from independent origins');
  check(equal([...accessible].sort(),sortedIds(expected)),'missing or foreign station entry');
  check(new Set(nested.map(s=>s.id)).size===nested.length,'overlapping inner groups');
  check(new Set(choice.primary.map(s=>s.id)).size===choice.primary.length,'duplicate outer entry');
  check(choice.primary.length+choice.groups.length>0,'city has no selectable entry');
  check(equal(sortedIds(view.stations),sortedIds(choice.primary)),'outer map differs from main-station choices');
  check(expected.some(s=>s.id===view.hubStation.id),'overview anchor belongs to another city');
  check(view.overviewCity===city.name,'incorrect overview city');
  check(view.services.length===0&&view.segments.length===0,'premature network on city overview');
  for(const group of choice.groups){
   check(equal([...new Set(group.sections.flatMap(s=>s.stations.map(v=>v.id)))].sort(),sortedIds(group.stations)),`${group.id}: missing section entry`);
   check(equal(sortedIds(getOverview(city.id,group.id).stations),sortedIds(group.stations)),`${group.id}: incorrect map markers`);
   check(group.stations.every(s=>s.cityId===city.id),`${group.id}: foreign city station`);
  }
  check(hidden.every(s=>!view.stations.some(v=>v.id===s.id)),'grouped small station leaked onto outer map');
  const group=g=>choice.groups.find(v=>v.id===g)?.stations.length||0;
  return {cityId:city.id,city:city.name,province:expected[0]?.province,stations:expected.length,primary:choice.primary.length,intercity:group('intercity'),local:group('local'),hiddenOnCityMap:hidden.length,primaryIds:sortedIds(choice.primary),groups:choice.groups.map(g=>({id:g.id,stationIds:sortedIds(g.stations)}))};
 }).sort((a,b)=>a.province.localeCompare(b.province,'zh-CN')||a.city.localeCompare(b.city,'zh-CN'));
 const sum=key=>rows.reduce((n,r)=>n+r[key],0);
 const result={scope:'All accepted departure origins; navigation grouping, not official station grades',cities:rows.length,origins:origins.length,primaryStations:sum('primary'),intercityCities:rows.filter(r=>r.intercity).length,intercityStations:sum('intercity'),localCities:rows.filter(r=>r.local).length,localStations:sum('local'),hiddenOnCityMaps:sum('hiddenOnCityMap'),groupOnlyCities:rows.filter(r=>!r.primary).map(r=>r.cityId),errors,rows};
 await writeFile('docs/city-choice-audit.json',JSON.stringify(result,null,2)+'\n');
 await writeFile('docs/CITY-CHOICE-AUDIT.md',`# 全城市选站与地图审计\n\n通过实际应用的 stationChoiceIndex 与 getOverview 检查，覆盖 ${result.cities} 城、${result.origins} 个独立出发站。错误 ${errors.length} 项。\n\n外层保留 ${result.primaryStations} 个主要快捷入口；市内及周边小站 ${result.localCities} 城 / ${result.localStations} 站，城际 ${result.intercityCities} 城 / ${result.intercityStations} 站。两类组内不重叠；部分共有主站同时提供城际快捷入口，因此各列不能简单相加。共 ${result.hiddenOnCityMaps} 个仅在分类内的站点从城市外层地图隐藏。\n\n检查：全部站点入口覆盖、城市身份、组内唯一、各分段成员覆盖、外层地图与主站列表一致、子目录地图与对应成员一致、概览不提前显示线路。单站或缺少繁忙主站的城市仍保留可选入口。此审计不代表全国未开放站点已核验，也不认定官方站级。\n\n重新生成：\`npm run data:audit-choices\`。详细独立 ID 见 [city-choice-audit.json](city-choice-audit.json)。\n\n| 省份 | 城市 | 全部独立站 | 外层站 | 城际组 | 小站组 | 外层地图隐藏 |\n| --- | --- | ---: | ---: | ---: | ---: | ---: |\n${rows.map(r=>`| ${r.province} | ${r.city} | ${r.stations} | ${r.primary} | ${r.intercity} | ${r.local} | ${r.hiddenOnCityMap} |`).join('\n')}\n`);
 console.log(JSON.stringify({...result,rows:undefined},null,2));
 if(errors.length)process.exitCode=1;
}finally{await server.close()}
