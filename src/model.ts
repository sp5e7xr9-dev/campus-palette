export type Status = 'verified'|'unavailable'|'not_collected'|'investigating'|'failed'|'not_applicable'|'pending';
export type Metric = {value:number|null;status:Status;source?:string;kind?:'official'|'calculated';reason?:string;note?:string;basis?:'unweighted';contextSource?:string};
export type Group = Record<string,Metric>;
export type RecordData = {id:string;university:string;faculty:string;department:string;selection:string;year:number;common:Group;individual:Group;total:Group;admissions:Group;note?:string;subjects?:{common:string[];individual:string[]}};
export type Source = {id:string;university:string;title:string;url:string;page:number;retrievedAt:string;sha256:string;status:string;verifiedAt?:string;reviewer?:string;format?:'pdf'|'html'};
export type University = {id:string;name:string;kana:string;short:string;region:string;officialUrl:string;resultUrl:string;note:string;type?:string;defaultTab?:'common'|'total'|'individual'};
export type Dataset = {version:number;updatedAt:string;universities:University[];sources:Source[];records:RecordData[];coverageNote:string};
export const years = [2024,2025,2026];
export const missing:Metric = {value:null,status:'not_collected',reason:'公式資料との照合が完了していません。'};
export function number(m?:Metric):number|null {return m?.status==='verified' && typeof m.value==='number' && Number.isFinite(m.value) ? m.value:null;}
export function rate(group:Group):number|null {const a=number(group.average),b=number(group.full);return a!==null&&b!==null&&b>0?a/b*100:null;}
export function format(m?:Metric,unit=''):string {const n=number(m);return n===null?'入手不可':`${n.toLocaleString('ja-JP',{maximumFractionDigits:2})}${unit}`;}
export function safeRead<T>(key:string,fallback:T):T {try {const v=JSON.parse(localStorage.getItem(key)||'null');return Array.isArray(fallback)?(Array.isArray(v)?v:fallback):v??fallback;}catch{return fallback;}}
export function safeWrite(key:string,value:unknown){try{localStorage.setItem(key,JSON.stringify(value));return true;}catch{return false;}}
export function isDataset(value:unknown):value is Dataset {
 if(!value||typeof value!=='object')return false;
 const d=value as Dataset;
 if(d.version!==1||typeof d.updatedAt!=='string'||!Array.isArray(d.universities)||!d.universities.length||!Array.isArray(d.sources)||!Array.isArray(d.records)||typeof d.coverageNote!=='string')return false;
 const ids=new Set(d.universities.map(u=>u?.id));
 if(!d.universities.every(u=>u&&['id','name','kana','short','region','officialUrl','resultUrl','note'].every(k=>typeof u[k as keyof University]==='string')))return false;
 const sources=new Map(d.sources.map(s=>[s?.id,s]));
 if(!d.sources.every(s=>s&&typeof s.id==='string'&&typeof s.url==='string'&&s.url.startsWith('https://')&&typeof s.page==='number'&&s.page>=1&&typeof s.title==='string'&&typeof s.retrievedAt==='string'))return false;
 return d.records.every(r=>r&&ids.has(r.university)&&years.includes(r.year)&&['id','faculty','department','selection'].every(k=>typeof r[k as keyof RecordData]==='string')&&['common','individual','total','admissions'].every(k=>{const g=r[k as keyof RecordData] as Group;if(!g||typeof g!=='object')return false;return Object.values(g).every(m=>m&&['verified','pending','unavailable','not_collected','investigating','failed','not_applicable'].includes(m.status)&&(m.value===null||(typeof m.value==='number'&&Number.isFinite(m.value)))&&(m.status!=='verified'||(m.value!==null&&!!m.source&&sources.get(m.source)?.university===r.university)));}));
}
