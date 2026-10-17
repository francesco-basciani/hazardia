const {chromium}=require(process.env.HAZARDIA_PLAYWRIGHT_PATH),fs=require('fs'),path=require('path');
(async()=>{
const root=process.cwd(),out=process.argv[2],ids=JSON.parse(fs.readFileSync(process.argv[3])).jobs;fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.HAZARDIA_BROWSER_EXECUTABLE,headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],checks=[];page.on('pageerror',e=>errors.push(e.message));
function check(name,value){checks.push({name,pass:!!value});if(!value)throw Error(name);}
try{
await page.route('**/qa-axe.js',route=>route.fulfill({contentType:'application/javascript',body:fs.readFileSync(process.env.HAZARDIA_AXE_PATH,'utf8')}));
await page.goto('http://127.0.0.1:8080/fire-studio.html?a='+ids.A+'&b='+ids.B);
await page.waitForSelector('#fire-workbench-frame');await page.waitForFunction(()=>document.body.dataset.view==='results');
const frame=page.frameLocator('#fire-workbench-frame');await frame.locator('#units>div').first().waitFor();
check('legacy link redirects to main simulations',page.url().includes('/?')&&page.url().includes('view=results'));
check('no separate studio navigation',await page.locator('.studio-nav').count()===0);
check('old pair restored',await frame.locator('#area-a').innerText()!=='Nessun risultato');
check('legacy sidebar hidden for fire',!(await page.locator('#control-sidebar').isVisible()));
await frame.locator('#units button').filter({hasText:'Rimuovi'}).first().click();
await frame.locator('#category').selectOption('helicopter');await frame.locator('#arrival').fill('20');await frame.locator('#line-length').fill('200');
await frame.locator('#add-unit').click();await frame.locator('#map-b').click({position:{x:180,y:160}});
check('single click inserts typed unit',await frame.locator('#units>div').count()===1&&(await frame.locator('#units>div').innerText()).includes('Elicottero'));
await frame.locator('#units input').fill('30');await frame.locator('#units input').dispatchEvent('change');
await frame.locator('#units select').selectOption('canadair');
await frame.locator('#units button').filter({hasText:'Sposta'}).click();await frame.locator('#map-b').click({position:{x:200,y:180}});
check('move preserves category/time',await frame.locator('#units select').inputValue()==='canadair'&&await frame.locator('#units input').inputValue()==='30');
await frame.locator('#add-unit').click();await frame.locator('#cancel-placement').click();check('cancel creates no unit',await frame.locator('#units>div').count()===1);
await page.getByRole('button',{name:'Monitoraggio',exact:true}).click();await page.getByRole('button',{name:'Simulazioni e risorse',exact:true}).click();
check('navigation preserves draft',await frame.locator('#units>div').count()===1);
await page.locator('[data-lab=evacuation]').click();check('evacuation retained',await page.locator('.comparison').isVisible());await page.locator('[data-lab=fire]').click();check('return to fire',await frame.locator('#add-unit').isVisible());
let submitted;await page.route('**/api/firelab',async route=>{if(route.request().method()==='POST'){submitted=route.request().postDataJSON();await route.fulfill({status:400,contentType:'application/json',body:JSON.stringify({code:'QA_NO_JOB',detail:'Payload captured without executing native jobs'})});}else await route.continue();});
await frame.locator('#source').selectOption('HISTORICAL');await frame.locator('#hours').selectOption('3');await frame.locator('#run').click();await page.waitForTimeout(500);
check('typed native request body unchanged',submitted?.resources.length===1&&submitted.resources[0].category==='canadair'&&submitted.resources[0].at_minutes===30&&submitted.resources[0].line.length===2&&Object.keys(submitted.resources[0]).sort().join(',')==='at_minutes,category,id,line');fs.writeFileSync(out+'/payload.json',JSON.stringify(submitted,null,2));
for(const width of [375,724,1440]){await page.setViewportSize({width,height:1000});await page.waitForTimeout(600);const child=page.frames().find(f=>f.url().includes('embedded=1'));check('main no overflow '+width,await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));check('studio no overflow '+width,await child.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.addScriptTag({url:'/qa-axe.js'});const mainAxe=await page.evaluate(async()=>(await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}})).violations);fs.writeFileSync(out+'/axe-main-'+width+'.json',JSON.stringify(mainAxe,null,2));check('axe main '+width,mainAxe.length===0);await child.addScriptTag({url:'/qa-axe.js'});const ax=await child.evaluate(async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations;});fs.writeFileSync(out+'/axe-'+width+'.json',JSON.stringify(ax,null,2));check('axe studio '+width,ax.length===0);await page.screenshot({path:out+'/viewport-'+width+'.png',fullPage:true});}
check('no page errors',errors.length===0);
}catch(e){checks.push({name:'fatal',pass:false,detail:e.message});await page.screenshot({path:out+'/failure.png',fullPage:true});}finally{fs.writeFileSync(out+'/verification.json',JSON.stringify({checks,errors},null,2));await browser.close();}console.log(JSON.stringify({checks,errors}));if(checks.some(c=>!c.pass))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
