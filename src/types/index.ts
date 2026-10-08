import type { LineString } from 'geojson';
export type Category = 'G' | 'C' | 'D' | 'Z' | 'T' | 'K' | 'OTHER';
export type HubId = string;
export type CityId = string;
export interface DepartureOrigin {id:HubId;name:string;city:string;cityId:CityId;province:string;provinceId:string;tier:'major'|'local';sourceUrl:string;sourceUpdatedAt:string;candidateServiceCount:number;verifiedServiceCount:number}
export type TrainType = 'all' | 'highspeed' | 'conventional';
export interface Station {id:string;name:string;city:string;province:string;provinceId:string;latitude:number;longitude:number;isHub:boolean;major:boolean;coordinateSource:string}
export interface PassengerService {id:string;trainNumber:string;category:Category;stations:string[];passenger:boolean;sourceUrl:string;sourceUpdatedAt:string;segmentIds:string[][]}
export interface RailwaySegment {schematic?:boolean;id:string;coverageStationIds:string[];name?:string;railwayNames:string[];osmSourceId:string;geometrySource:string;routingConfidence:'inferred-corridor';family:'hs'|'ordinary'|'mixed';geometry:LineString;geometryAccuracy:'approximate'|'exact';passengerCategories:Category[];serviceIds:string[]}
export interface HubNetwork {hubStationId:string;destinationStationIds:string[];serviceIds:string[]}
export interface RailData {origins:DepartureOrigin[];physicalSources:Record<string,string[]>;updatedAt:string;retrievedAt:string;stations:Station[];services:PassengerService[];segments:RailwaySegment[];networks:Record<HubId,HubNetwork>;audit:{impossibleTimingServices?:string[];pendingOrigins:{name:string;reason:string}[];invalidTimingServices:string[];schematicRepairedIntervals:number;railCorridorRepairedIntervals:number;remainingUnmappedIntervals:number;schematicSegments:number;candidates:number;acceptedServices:number;rejectedNoHub:number;excludedTemporary:number;unlocatedStations:string[];failedPages:number;matchedPhysicalIntervals:number;unmatchedPhysicalIntervals:number;physicalSourceSnapshot:string;physicalGeometryBuild:string};sources:{name:string;url:string;description:string}[]}
export interface Filters {type:TrainType;province:string;search:string}
