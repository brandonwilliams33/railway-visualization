import {test,expect} from '@playwright/test';
test('selection, search, directory, details and persistent URL',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 await page.goto('/');await expect(page.locator('.leaflet-container')).toBeVisible();await expect(page.locator('.province-directory')).toHaveCount(0);await page.getByLabel('出发城市').selectOption('xuzhou');await expect(page.locator('.province-directory')).toHaveCount(0);await page.getByRole('button',{name:'徐州东站',exact:true}).click();
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
