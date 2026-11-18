import {describe,it,expect} from 'vitest';
import {number,rate,format,Metric,isDataset} from './model';
const v=(value:number|null,status:Metric['status']='verified'):Metric=>({value,status});
describe('公開数値と欠損値',()=>{
 it('欠損を0へ変換しない',()=>{expect(number(v(null,'unavailable'))).toBeNull();expect(format(v(null,'not_collected'))).toBe('入手不可');expect(rate({average:v(null,'pending'),full:v(1000)})).toBeNull()});
 it('未確認・取得失敗の数値は表示も描画もしない',()=>{for(const s of ['pending','failed','investigating','not_applicable'] as const){expect(number(v(50,s))).toBeNull();expect(format(v(50,s))).toBe('入手不可')}});
 it('実測0と欠損を区別する',()=>{expect(number(v(0))).toBe(0);expect(format(v(0),'点')).toBe('0点')});
 it('各年度自身の満点で得点率を計算する',()=>{expect(rate({average:v(600),full:v(1200)})).toBe(50);expect(rate({average:v(600),full:v(1000)})).toBe(60)});
 it('満点不明・0の得点率は推定しない',()=>{expect(rate({average:v(500),full:v(null,'unavailable')})).toBeNull();expect(rate({average:v(0),full:v(0)})).toBeNull()});
 it('壊れたJSONの構造を拒否する',()=>{expect(isDataset({version:1,records:[],sources:[]})).toBe(false);expect(isDataset(null)).toBe(false)});
 it('NaNを表示しない',()=>expect(number(v(NaN))).toBeNull());
});
