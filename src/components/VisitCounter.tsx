import {useEffect,useState} from 'react';
import {loadVisitCount,type VisitCount} from '../lib/visitCounter';

export function VisitCounter(){
 const [result,setResult]=useState<VisitCount|null>(null);
 useEffect(()=>{let active=true;loadVisitCount().then(value=>{if(active)setResult(value)});return()=>{active=false}},[]);
 return <span className="visit-counter" aria-live="polite" title="独立访客数（UV），重复访问按不蒜子规则去重；不等于严格的设备数量，同一域名下的页面共用统计。">累计访客数 <b>{!result?'加载中…':result.status==='ready'?`${result.count} 人次`:result.status==='local'?'上线后开始统计':'暂不可用'}</b></span>;
}
