export type VisitCount={status:'ready';count:string}|{status:'local'|'unavailable'};
export const counterEndpoint='https://busuanzi.ibruce.info/busuanzi';

// Counters are scoped to a hostname by the provider. Send only that origin as
// Referer, never the application's station, city or search query parameters.
export function canCountVisits(location:Pick<Location,'hostname'|'protocol'>):boolean{
 const host=location.hostname.toLowerCase();
 return location.protocol==='https:'&&!!host&&host.includes('.')&&
  !/^(?:\d{1,3}\.){3}\d{1,3}$/.test(host)&&!host.includes(':')&&
  !host.endsWith('.localhost')&&!host.endsWith('.local')&&!host.endsWith('.test')&&!host.endsWith('.invalid');
}
export function parseVisitCount(payload:unknown):string|null{
 if(!payload||typeof payload!=='object')return null;
 const value=(payload as {site_uv?:unknown}).site_uv;
 if(typeof value==='number'&&!Number.isSafeInteger(value))return null;
 if(typeof value!=='number'&&typeof value!=='string')return null;
 const digits=String(value);
 return /^\d{1,24}$/.test(digits)?BigInt(digits).toLocaleString('zh-CN'):null;
}

let once:Promise<VisitCount>|undefined;
export function loadVisitCount():Promise<VisitCount>{
 // One request per loaded document, including React StrictMode effect replay.
 // A filter change, city change or component remount must not send another hit.
 // Across reloads, visitor deduplication belongs to the provider's UV metric.
 if(once)return once;
 if(!canCountVisits(window.location))return once=Promise.resolve({status:'local'});
 return once=new Promise(resolve=>{
  const callback=`BusuanziCallback_${Math.floor(1099511627776*Math.random())}`;
  const globals=window as unknown as Record<string,unknown>;
  const script=document.createElement('script');
  let settled=false;
  const finish=(result:VisitCount)=>{
   if(settled)return;
   settled=true;clearTimeout(timeout);script.remove();
   // A response already in flight may arrive after a timeout. Keep a harmless
   // callback for this document so it cannot throw or change the displayed state.
   globals[callback]=()=>{};
   resolve(result);
  };
  const timeout=setTimeout(()=>finish({status:'unavailable'}),8000);
  globals[callback]=(payload:unknown)=>{
   const count=parseVisitCount(payload);
   finish(count===null?{status:'unavailable'}:{status:'ready',count});
  };
  script.async=true;
  script.referrerPolicy='origin';
  script.src=`${counterEndpoint}?jsonpCallback=${callback}`;
  script.onerror=()=>finish({status:'unavailable'});
  document.head.appendChild(script);
 });
}
