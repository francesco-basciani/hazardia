/* Shared consultation time. Sources retain their own validity and granularity. */
export class MonitorTimeline{
 constructor(notify=()=>{},start=Date.now()){this.start=Math.floor(start/3600000)*3600000;this.sources=new Map();this.at=null;this.notify=notify;this.listeners=new Set();}
 times(){const times=new Set();for(const windows of this.sources.values())for(const [from,to] of windows){const a=Date.parse(from),b=Date.parse(to);if(!Number.isFinite(a)||!Number.isFinite(b)||b<=a||b-a>14*86400000)continue;for(let t=Math.max(this.start,Math.ceil(a/3600000)*3600000);t<b;t+=3600000)times.add(new Date(t).toISOString().replace('.000Z','Z'));}return [...times].sort();}
 update(source,windows){const before=this.times().join();this.sources.set(source,windows);const times=this.times();if(!this.at&&times.length)this.at=times[0];if(before!==times.join())for(const fn of this.listeners)fn();}
 subscribe(fn){this.listeners.add(fn);return()=>this.listeners.delete(fn);}
 select(at){if(!Number.isFinite(Date.parse(at)))return;this.at=at;this.notify({at});}
 covered(source,at=this.at){const t=Date.parse(at);return (this.sources.get(source)||[]).some(([from,to])=>Date.parse(from)<=t&&t<Date.parse(to));}
}
export const monitorTimeline=new MonitorTimeline(detail=>document.dispatchEvent(new CustomEvent('hazardia-monitor-time',{detail})));
