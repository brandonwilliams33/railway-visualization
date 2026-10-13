import {createServer} from 'vite';
import {writeFile} from 'node:fs/promises';
const server=await createServer({server:{middlewareMode:true},appType:'custom'});
try{
 const network=await server.ssrLoadModule('/src/lib/network.ts');
 const {isSlowFuxing}=await server.ssrLoadModule('/src/lib/trainTypes.ts');
 await network.loadNetwork();
 const accepted=network.data.services.filter(isSlowFuxing);
 const byStation=new Map();
 for(const service of accepted)for(const id of service.stations){const codes=byStation.get(id)||[];codes.push(service.trainNumber);byStation.set(id,codes)}
 const origins=network.origins.filter(s=>byStation.has(s.id));
 const rows=origins.map(s=>({stationId:s.id,name:s.name,city:s.city,cityId:s.cityId,trainNumbers:byStation.get(s.id)}));
 const xuzhou=network.getNetwork('xuzhou',{type:'slow-fuxing',province:'',search:''});
 const result={basis:'number-band-inference',completeFleetVerification:false,classifiedServices:accepted.length,departureStations:origins.length,cities:new Set(origins.map(s=>s.cityId)).size,xuzhou:{destinations:xuzhou.destinations.length,provinces:xuzhou.provinces.length,serviceRecords:xuzhou.services.length,trainNumbers:xuzhou.services.map(s=>s.trainNumber)},rows};
 await writeFile('docs/slow-fuxing-audit.json',JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({...result,rows:undefined},null,2));
}finally{await server.close()}
