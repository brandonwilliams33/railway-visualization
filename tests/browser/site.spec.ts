import {origins,departureIndex,stationChoiceIndex} from '../../src/lib/network';
import {test,expect,type Page} from '@playwright/test';
async function chooseCity(page:Page,city:string){
 const selection=departureIndex.resolve({city});
 await page.getByLabel('出发区域',{exact:true}).selectOption(selection.region!);
 await page.getByLabel('出发省份',{exact:true}).selectOption(selection.province!);
 await page.getByLabel('出发城市',{exact:true}).selectOption(city);
}
test('selection, search, directory, details and persistent URL',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 await page.goto('/');await expect(page.locator('.leaflet-container')).toBeVisible();await expect(page.locator('.province-directory')).toHaveCount(0);await chooseCity(page,'xuzhou');await expect(page.locator('.province-directory')).toHaveCount(0);await page.getByRole('button',{name:'徐州东站',exact:true}).click();
 await expect(page.getByRole('heading',{name:'徐州东站，出发。'})).toBeVisible();await expect(page.locator('.leaflet-container')).toBeVisible();
 await page.getByRole('textbox',{name:'搜索可直达城市或车站'}).fill('西安');
 await page.locator('.province-group button').filter({hasText:'西安北'}).click();await expect(page.getByRole('complementary',{name:'地图详情'})).toContainText('西安北站');
 expect(page.url()).toContain('q=');await page.reload();await expect(page.getByRole('textbox',{name:'搜索可直达城市或车站'})).toHaveValue('西安');
 await page.getByRole('button',{name:'重置筛选'}).click();await page.getByLabel('目的地区域').selectOption('jiangsu');await expect(page.locator('.province-group')).toHaveCount(1);
 await page.getByRole('button',{name:'数据与方法'}).click();await expect(page.getByRole('dialog')).toBeVisible();await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).toHaveCount(0);
 await page.getByRole('button',{name:'阅读全文'}).click();await expect(page.getByText('晚上：地锅鸡，或者烧烤')).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);expect(errors).toEqual([]);
});
test('both hubs, type filtering and empty state',async({page})=>{
 await page.goto('/?station=xuzhou');await page.getByLabel('列车类型').selectOption('conventional');
 await expect(page.getByRole('heading',{name:'徐州站，出发。'})).toBeVisible();
 const n=await page.locator('.stat b').first().textContent();expect(Number(n)).toBeGreaterThan(100);
 await page.getByRole('textbox',{name:'搜索可直达城市或车站'}).fill('不存在');await expect(page.getByText('没有匹配的直达站点')).toBeVisible();await expect(page.locator('.stat b').first()).toHaveText('0');
 await page.getByRole('button',{name:'切换中心站'}).click();await expect(page.getByRole('heading',{name:'从这里，去远方。'})).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test('Jiangsu cities, separate stations and a small-station network',async({page})=>{
 await page.goto('/');await expect(page.getByLabel('出发城市')).toBeDisabled();
 await chooseCity(page,'suzhou');await expect(page.locator('.hub-options button')).toHaveCount(stationChoiceIndex.city('suzhou').primary.length+stationChoiceIndex.city('suzhou').groups.length);
 await expect(page.getByRole('button',{name:'苏州站',exact:true})).toBeVisible();await expect(page.getByRole('button',{name:'苏州北站',exact:true})).toBeVisible();
 await expect(page.locator('.province-directory')).toHaveCount(0);await page.getByRole('button',{name:'苏州站',exact:true}).click();
 await expect(page.getByRole('heading',{name:'苏州站，出发。'})).toBeVisible();await expect(page.locator('.fixed-city')).toContainText('苏州');
 await page.getByRole('button',{name:'切换中心站'}).click();await chooseCity(page,'nantong');await page.getByRole('button',{name:'市内及周边小站',exact:true}).click();await page.getByRole('button',{name:'栟茶站',exact:true}).click();
 await expect(page.getByRole('heading',{name:'栟茶站，出发。'})).toBeVisible();await expect(page.locator('.stat b').first()).toHaveText('7');
 await page.locator('.province-group button').filter({hasText:'如东'}).click();await page.getByRole('button',{name:'从如东站出发'}).click();
 await expect(page.getByRole('heading',{name:'如东站，出发。'})).toBeVisible();await page.reload();await expect(page.getByRole('heading',{name:'如东站，出发。'})).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});


test('cross-province cities keep the map-first selection flow',async({page})=>{
 await page.goto('/');await expect(page.getByLabel('出发区域').locator('option')).toHaveCount(1+departureIndex.regions.length);
 for(const name of ['上海虹桥','杭州西','合肥南']){
  const origin=origins.find(s=>s.name===name);if(!origin)continue;
  await chooseCity(page,origin.cityId);
  await expect(page.locator('.hub-options button')).toHaveCount(stationChoiceIndex.city(origin.cityId).primary.length+stationChoiceIndex.city(origin.cityId).groups.length);
  await expect(page.locator('.province-directory')).toHaveCount(0);
  await page.getByRole('button',{name:name+'站',exact:true}).click();
  await expect(page.getByRole('heading',{name:name+'站，出发。'})).toBeVisible();
  await expect(page.locator('.fixed-city')).toContainText(origin.city);
  await page.reload();await expect(page.getByRole('heading',{name:name+'站，出发。'})).toBeVisible();
  await page.getByRole('link',{name:'沿线 Railbound'}).click();
 }
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});


test('departure hierarchy restores links and clears children when changing parents',async({page})=>{
 await page.goto('/');
 await expect(page.getByLabel('出发省份')).toBeDisabled();await expect(page.getByLabel('出发城市')).toBeDisabled();
 await chooseCity(page,'suzhou');await expect(page.locator('.hub-options button')).toHaveCount(stationChoiceIndex.city('suzhou').primary.length+stationChoiceIndex.city('suzhou').groups.length);
 await page.getByLabel('出发省份').selectOption('anhui');
 await expect(page.getByLabel('出发城市')).toHaveValue('');await expect(page.locator('.hub-options button')).toHaveCount(0);
 await expect(page.locator('.province-directory')).toHaveCount(0);await page.reload();
 await expect(page.getByLabel('出发区域')).toHaveValue('east');await expect(page.getByLabel('出发省份')).toHaveValue('anhui');
 await page.getByLabel('出发区域').selectOption('south');
 await expect(page.getByLabel('出发省份')).toHaveValue('');await expect(page.getByLabel('出发城市')).toBeDisabled();
 await page.goto('/?city=anhui-suzhou');
 await expect(page.getByLabel('出发区域')).toHaveValue('east');await expect(page.getByLabel('出发省份')).toHaveValue('anhui');await expect(page.getByLabel('出发城市')).toHaveValue('anhui-suzhou');
 await expect(page.getByRole('button',{name:'宿州站',exact:true})).toBeVisible();
 await page.getByRole('link',{name:'沿线 Railbound'}).click();
 await expect(page.getByLabel('出发区域')).toHaveValue('');await expect(page.getByLabel('出发省份')).toBeDisabled();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test('intercity sits beside hubs and opens independent station choices',async({page})=>{
 await page.goto('/');await chooseCity(page,'guangdong-shenzhen');
 await expect(page.getByRole('button',{name:'深圳北站',exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'深圳机场站',exact:true})).toHaveCount(0);
 await page.getByRole('button',{name:'城际铁路',exact:true}).click();
 await expect(page.getByRole('region',{name:'城际车站'})).toBeVisible();
 await expect(page.locator('.intercity-stop button')).toHaveCount(4);
 await page.reload();await expect(page.getByRole('region',{name:'城际车站'})).toBeVisible();
 await page.getByRole('button',{name:'深圳机场站',exact:true}).click();
 await expect(page.getByRole('heading',{name:'深圳机场站，出发。'})).toBeVisible();
 await page.getByRole('button',{name:'切换中心站'}).click();
 await expect(page.getByRole('region',{name:'城际车站'})).toBeVisible();
 await page.getByRole('button',{name:'返回全部车站'}).click();
 await expect(page.getByRole('button',{name:'城际铁路',exact:true})).toBeFocused();
 await page.getByRole('button',{name:'城际铁路',exact:true}).click();
 await page.getByLabel('出发城市',{exact:true}).selectOption({label:'广州'});
 await expect(page.getByRole('region',{name:'城际车站'})).toHaveCount(0);
 await expect(page.getByRole('button',{name:'广州南站',exact:true})).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test('local small stops stay separate from intercity and retain their return group',async({page})=>{
 const s=origins.find(s=>s.name==='莘庄')!;await page.goto('/');await chooseCity(page,s.cityId);
 await expect(page.getByRole('button',{name:'上海虹桥站',exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'莘庄站',exact:true})).toHaveCount(0);
 await page.getByRole('button',{name:'市内及周边小站',exact:true}).click();
 await expect(page.getByRole('region',{name:'市内及周边小站',exact:true})).toContainText('金山铁路');
 await page.getByRole('button',{name:'莘庄站',exact:true}).click();
 await expect(page.getByRole('heading',{name:'莘庄站，出发。'})).toBeVisible();
 await page.reload();await page.getByRole('button',{name:'切换中心站'}).click();
 await expect(page.getByRole('region',{name:'市内及周边小站',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'返回全部车站'}).click();
 await expect(page.getByRole('button',{name:'市内及周边小站',exact:true})).toBeFocused();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
