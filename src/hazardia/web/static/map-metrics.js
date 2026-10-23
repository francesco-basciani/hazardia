if(new URLSearchParams(location.search).has('diagnostics')){
/* Small bounded QA probe: DOM-readable timings, no telemetry or network output. */
const root=document.documentElement,start=performance.now(),samples=[],frames=[];let last=0,firstTile=null,firstWeather=null;
try{new PerformanceObserver(list=>{for(const x of list.getEntries())if(/\/api\/(maps|weather|monitoring\/radar)/.test(x.name)){samples.push({path:new URL(x.name).pathname,ms:Math.round(x.duration*10)/10,bytes:x.transferSize});if(samples.length>160)samples.shift();}}).observe({type:'resource',buffered:true});}catch{}
function tick(now){if(!document.hidden&&last){frames.push(now-last);if(frames.length>120)frames.shift();}last=now;requestAnimationFrame(tick);}requestAnimationFrame(tick);
setInterval(()=>{const map=document.getElementById('monitor-map');if(!map)return;const tiles=[...map.querySelectorAll('.leaflet-tile')];const loaded=tiles.filter(x=>x.complete&&x.naturalWidth>0).length;if(loaded&&firstTile===null)firstTile=performance.now()-start;const labels=map.querySelectorAll('.weather-site').length;if(labels&&firstWeather===null)firstWeather=performance.now()-start;const wind=[...map.querySelectorAll('canvas')].find(c=>c.dataset.frameP95Ms);const sorted=[...frames].sort((a,b)=>a-b);root.dataset.mapMetrics=JSON.stringify({firstTileMs:firstTile,firstWeatherMs:firstWeather,loadedTiles:loaded,totalTiles:tiles.length,rafP95Ms:sorted[Math.ceil(sorted.length*.95)-1]||null,resources:samples,wind:wind?.dataset||{},at:new Date().toISOString()});},500);

}
