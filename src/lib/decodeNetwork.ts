import type {PassengerService,RailData} from '../types';

type CompactNetwork = Omit<RailData,'services'> & {
 schemaVersion:2;
 segmentPaths:number[][];
 services:(Omit<PassengerService,'segmentIds'> & {segmentPathIndexes:number[]})[];
};

export function decodeNetwork(raw:unknown):RailData{
 const {schemaVersion,segmentPaths,services:packedServices,...metadata}=raw as CompactNetwork;
 if(schemaVersion!==2)return raw as RailData;
 const paths=segmentPaths.map(path=>path.map(index=>{
  const segment=metadata.segments[index];
  if(!segment)throw new Error('线路数据包含无效区段');
  return segment.id;
 }));
 const services=packedServices.map(({segmentPathIndexes,...service})=>({
  ...service,segmentIds:segmentPathIndexes.map(index=>{
   const path=paths[index];
   if(!path)throw new Error('线路数据包含无效路径');
   return path;
  })
 }));
 return {...metadata,services};
}
