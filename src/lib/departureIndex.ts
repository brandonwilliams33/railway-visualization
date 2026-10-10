import type {DepartureOrigin} from '../types';

// Presentation regions only. Station identity and reachability stay in the data.
export const geographicRegions = [
 {id:'north',name:'华北',provinces:['beijing','tianjin','hebei','shanxi','neimenggu']},
 {id:'northeast',name:'东北',provinces:['liaoning','jilin','heilongjiang']},
 {id:'east',name:'华东',provinces:['shanghai','jiangsu','zhejiang','anhui','fujian','jiangxi','shandong']},
 {id:'central',name:'华中',provinces:['henan','hubei','hunan']},
 {id:'south',name:'华南',provinces:['guangdong','guangxi','hainan']},
 {id:'southwest',name:'西南',provinces:['chongqing','sichuan','guizhou','yunnan','xizang']},
 {id:'northwest',name:'西北',provinces:['shaanxi','gansu','qinghai','ningxia','xinjiang']},
 {id:'hongkong-macao-taiwan',name:'港澳台',provinces:['hongkong','macao','taiwan']},
] as const;
export interface DepartureSelection {region:string|null;province:string|null;city:string|null}

export function buildDepartureIndex(origins:DepartureOrigin[]){
 const provinces=new Map<string,{id:string;name:string;regionId:string}>();
 const cities=new Map<string,{id:string;name:string;provinceId:string;regionId:string}>();
 for(const origin of origins){
  const region=geographicRegions.find(r=>(r.provinces as readonly string[]).includes(origin.provinceId));
  if(!region)throw new Error('未配置出发区域：'+origin.provinceId);
  const previous=cities.get(origin.cityId);
  if(previous&&previous.provinceId!==origin.provinceId)throw new Error('出发城市跨省重名 ID：'+origin.cityId);
  provinces.set(origin.provinceId,{id:origin.provinceId,name:origin.province,regionId:region.id});
  cities.set(origin.cityId,{id:origin.cityId,name:origin.city,provinceId:origin.provinceId,regionId:region.id});
 }
 const regions=geographicRegions.filter(r=>[...provinces.values()].some(p=>p.regionId===r.id));
 const provincesIn=(region:string|null)=>geographicRegions.find(r=>r.id===region)?.provinces.flatMap(id=>{const province=provinces.get(id);return province?[province]:[]})||[];
 const citiesIn=(province:string|null)=>[...cities.values()].filter(c=>c.provinceId===province).sort((a,b)=>a.name.localeCompare(b.name,'zh-CN'));
 function resolve(selection:Partial<DepartureSelection>):DepartureSelection{
  // A known city (including old shared URLs) supplies its complete ancestry.
  const city=selection.city?cities.get(selection.city):undefined;
  if(city)return {region:city.regionId,province:city.provinceId,city:city.id};
  const region=regions.find(r=>r.id===selection.region)?.id||null;
  const province=selection.province?provinces.get(selection.province):undefined;
  return {region,province:province?.regionId===region?province.id:null,city:null};
 }
 return {regions,provinces,cities,provincesIn,citiesIn,resolve};
}
