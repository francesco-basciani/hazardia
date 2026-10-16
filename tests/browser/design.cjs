// Presentation acceptance against a disposable same-VM service. No model submissions.
const {chromium}=require(process.env.HAZARDIA_PLAYWRIGHT_PATH||'playwright');
const fs=require('fs'),path=require('path');let browser;
(async()=>{
 const out=process.argv[2],base=process.env.HAZARDIA_BASE_URL||'http://127.0.0.1:8081';fs.mkdirSync(out,{recursive:true});
 browser=await chromium.launch({headless:true,executablePath:process.env.HAZARDIA_BROWSER_EXECUTABLE||undefined});
 const ctx=await browser.newContext({baseURL:base,viewport:{width:1440,height:1000},reducedMotion:'reduce',bypassCSP:true});
 const p=await ctx.newPage(),checks=[],errors=[],posts=[];p.on('pageerror',e=>errors.push(e.message));p.on('request',r=>{if(r.method()==='POST')posts.push(new URL(r.url()).pathname)});
 const check=(id,ok,detail)=>{checks.push({id,status:ok?'PASS':'FAIL',detail});console.log(id,ok?'PASS':'FAIL')};
 await p.goto(base);await p.waitForFunction(()=>document.querySelector('#monitor-map').dataset.hazards==='FIRE,FLOOD');
 const sizes=[[320,740],[375,812],[600,960],[768,1024],[1024,768],[1440,1000],[1920,1080],[812,375]];
 for(const [width,height] of sizes){
  await p.setViewportSize({width,height});
  for(const section of ['map','results','sources','help']){
   await p.locator('button[data-view="'+section+'"]').click();
   const d=await p.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,clipped:[...document.querySelectorAll('button,input,select')].filter(e=>e.getClientRects().length&&!e.closest('.leaflet-container')).map(e=>({id:e.id||e.textContent.trim(),left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right})).filter(e=>e.left<-.5||e.right>innerWidth+.5)}));
   check(`fit-${width}x${height}-${section}`,d.scroll<=width+1&&d.clipped.length===0,d);
  }
  await p.locator('button[data-view="map"]').click();
  const nav=await p.locator('.main-nav button').evaluateAll(es=>es.map(e=>({name:e.textContent,height:e.getBoundingClientRect().height,width:e.getBoundingClientRect().width})));
  check(`navigation-touch-targets-${width}x${height}`,nav.every(e=>e.height>=44&&e.width>=44),nav);
  await p.screenshot({path:path.join(out,`monitor-${width}x${height}.png`),fullPage:true});
 }
 await p.setViewportSize({width:375,height:812});await p.locator('button[data-view="results"]').click();await p.locator('#sidebar-toggle').click();
 check('mobile-planner-accessible',await p.locator('#control-sidebar').isVisible()&&await p.locator('#hazard').isVisible());await p.locator('#sidebar-toggle').click();
 await p.locator('button[data-view="map"]').focus();await p.keyboard.press('Enter');
 check('visible-keyboard-focus',(await p.locator('button[data-view="map"]').evaluate(e=>getComputedStyle(e).outlineStyle))!=='none');
 check('reduced-motion',await p.locator('.main-nav button').first().evaluate(e=>getComputedStyle(e).transitionDuration==='0s'));
 await p.goto(base+'/physical-fire.html');await p.waitForFunction(()=>document.querySelector('#physical-status').textContent.includes('Due raster nativi'));
 const axePath=process.env.HAZARDIA_AXE_PATH||require.resolve('axe-core/axe.min.js');await p.addScriptTag({path:axePath});
 for(const [width,height] of sizes){await p.setViewportSize({width,height});const d=await p.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));check(`physical-fit-${width}x${height}`,d.scroll<=width+1,d);}
 for(const width of [375,768,1440]){await p.setViewportSize({width,height:1000});const a=await p.evaluate(()=>axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}));fs.writeFileSync(path.join(out,'axe-physical-'+width+'.json'),JSON.stringify(a,null,2));check('physical-axe-'+width,a.violations.length===0,a.violations.map(v=>({id:v.id,targets:v.nodes.map(n=>n.target)})));}
 check('no-native-model-submissions',!posts.includes('/api/jobs'),posts);check('no-js-errors',!errors.length,errors);
 fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({at:new Date().toISOString(),browser:await browser.version(),checks,errors,posts},null,2));await browser.close();if(checks.some(c=>c.status==='FAIL'))process.exitCode=1;
})().catch(async e=>{console.error(e);await browser?.close();process.exitCode=1});
