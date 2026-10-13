import rules from '../data/slow-fuxing-rules.json';
import type {PassengerService,TrainType} from '../types';

export const trainTypeLabels:Record<TrainType,string>={all:'全部客运',highspeed:'高铁 / 动车',conventional:'普速', 'slow-fuxing':'普速复兴号'};
export const isHighspeed=(service:PassengerService)=>['G','D','C'].includes(service.category);

// A snapshot classification inferred from contemporary numbering bands. Do not
// apply historical D7xx assignments to present-day services with reused numbers.
export function isSlowFuxing(service:PassengerService):boolean{
 if(!service.passenger||!/^\d{4}-\d{2}-\d{2}$/.test(service.sourceUpdatedAt))return false;
 const match=/^([CD])([1-9]\d{0,2})$/.exec(service.trainNumber);
 if(!match||match[1]!==service.category)return false;
 const number=Number(match[2]);
 return rules.bands.some(b=>b.category===service.category&&number>=b.min&&number<=b.max&&service.sourceUpdatedAt>=b.effectiveFrom);
}

export function matchesTrainType(service:PassengerService,type:TrainType):boolean{
 switch(type){
  case 'all':return true;
  case 'highspeed':return isHighspeed(service);
  case 'conventional':return !isHighspeed(service);
  case 'slow-fuxing':return isSlowFuxing(service);
 }
}
export function parseTrainType(value:string|null):TrainType{
 return value&&Object.hasOwn(trainTypeLabels,value)?value as TrainType:'all';
}
