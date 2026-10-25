if(new URLSearchParams(location.search).has('diagnostics')){
/* Small bounded QA probe: DOM-readable timings, no telemetry or network output. */
const root=document.documentElement,start=performance.now(),samples=[],frames=[];let last=0,firstTile=null,firstWeather=null;
try{new PerformanceObserver(list=>{for(const x of list.getEntries())if(/\/api\/(maps|weather|monitoring\/radar)/.test(x.name)){samples.push({path:new URL(x.name).pathname,ms:Math.round(x.duration*10)/10,bytes:x.transferSize});if(samples.length>160)samples.shift();}}).observe({type:'resource',buffered:true});}catch{}
function tick(now){if(!document.hidden&&last){frames.push(now-last);if(frames.length>120)frames.shift();}last=now;requestAnimationFrame(tick);}requestAnimationFrame(tick);
setInterval(()=>{const map=document.getElementById('monitor-map');if(!map)return;const tiles=[...map.querySelectorAll('.leaflet-tile')];const loaded=tiles.filter(x=>x.complete&&x.naturalWidth>0).length;if(loaded&&firstTile===null)firstTile=performance.now()-start;const labels=map.querySelectorAll('.weather-site').length;if(labels&&firstWeather===null)firstWeather=performance.now()-start;const wind=[...map.querySelectorAll('canvas')].find(c=>c.dataset.frameP95Ms);const sorted=[...frames].sort((a,b)=>a-b);root.dataset.mapMetrics=JSON.stringify({firstTileMs:firstTile,firstWeatherMs:firstWeather,loadedTiles:loaded,totalTiles:tiles.length,rafP95Ms:sorted[Math.ceil(sorted.length*.95)-1]||null,resources:samples,wind:wind?.dataset||{},at:new Date().toISOString()});},500);

}

if(new URLSearchParams(location.search).has('diagnostics')){
 // Opt-in, bounded visual-feedback and heap probe. Never sends telemetry.
 const feedback=[],longTasks=[];let pending=0;
 document.addEventListener('click',sample,true);document.addEventListener('change',sample,true);document.addEventListener('keydown',sample,true);
 function sample(event){const el=event.target;if(!el?.closest?.('#monitor-map,.console-left,.console-right,.console-top-tools,.console-map-actions'))return;const start=performance.now(),action=event.type+':'+(el.id||el.getAttribute('aria-label')||el.tagName);pending++;requestAnimationFrame(()=>requestAnimationFrame(()=>{feedback.push({action,ms:performance.now()-start});if(feedback.length>400)feedback.shift();pending--;}));}
 try{new PerformanceObserver(list=>{for(const e of list.getEntries()){longTasks.push({ms:e.duration,at:e.startTime});if(longTasks.length>80)longTasks.shift();}}).observe({type:'longtask',buffered:true});}catch{}
 setInterval(()=>{document.documentElement.dataset.auditMetrics=JSON.stringify({feedback,longTasks,pending,heap:performance.memory?{used:performance.memory.usedJSHeapSize,total:performance.memory.totalJSHeapSize,limit:performance.memory.jsHeapSizeLimit}:null,domNodes:document.getElementsByTagName('*').length,ageMs:performance.now(),navigation:performance.getEntriesByType('navigation').map(n=>({duration:n.duration,dom:n.domContentLoadedEventEnd,load:n.loadEventEnd})),device:{agent:navigator.userAgent,cores:navigator.hardwareConcurrency,dpr:devicePixelRatio,width:innerWidth,height:innerHeight},at:new Date().toISOString()});},1000);
}
