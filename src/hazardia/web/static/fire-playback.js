// Display-only dissolve between immutable native samples. No interpolated physics product.
export function frameBlend(series,h){
 if(!series?.frames?.length||!Number.isFinite(h)||h<0)return null;
 const time=f=>(f.elapsed_s??f.hour*3600)/3600,frames=series.frames,last=frames.at(-1);
 if(h>time(last)+1e-8)return null;
 let left=null,right=null;for(const f of frames){if(time(f)<=h+1e-8)left=f;else{right=f;break;}}
 if(!right)return {left,right:null,mix:0,sample:left};
 const from=left?time(left):0,to=time(right);if(to-from>.250001)return null;
 return {left,right,mix:Math.max(0,Math.min(1,(h-from)/(to-from))),sample:left};
}
export function nextSample(seriesList,h){return Math.min(...seriesList.flatMap(r=>(r?.frames||[]).map(f=>(f.elapsed_s??f.hour*3600)/3600).filter(t=>t>h+1e-8)));}
export function fireRaster(L,series,cache,opacity){
 const Raster=L.Layer.extend({
  onAdd(map){this.map=map;this.canvas=L.DomUtil.create('canvas','fire-blend-layer',map.getPane('overlayPane'));this.canvas.setAttribute('aria-hidden','true');this.canvas.style.pointerEvents='none';this.canvas.style.position='absolute';this.context=this.canvas.getContext('2d');map.on('moveend zoomend resize',this.position,this);this.position();},
  position(){if(!this.map)return;const bounds=L.latLngBounds(series.bounds),nw=this.map.latLngToLayerPoint(bounds.getNorthWest()),se=this.map.latLngToLayerPoint(bounds.getSouthEast()),size=se.subtract(nw);L.DomUtil.setPosition(this.canvas,nw);this.canvas.style.width=size.x+'px';this.canvas.style.height=size.y+'px';},
  setOpacity(alpha){this.canvas.style.opacity=alpha;this.native?.setOpacity(alpha);},
  paint(h,alpha){const pair=frameBlend(series,h);if(!pair)return;const key=[pair.left?.url,pair.right?.url].join('|');this.canvas.dataset.hour=String(h);this.canvas.dataset.left=pair.left?.url||'';this.canvas.dataset.right=pair.right?.url||'';this.canvas.dataset.mix=String(pair.mix);this.canvas.dataset.qualification='DISPLAY_DISSOLVE_NOT_NATIVE_SAMPLE';this.canvas.style.opacity=alpha;
   if(pair.mix<1e-8&&pair.left){this.canvas.hidden=true;if(this.nativeKey!==pair.left.url){this.native?.remove();this.native=L.imageOverlay(cache.get(pair.left.url).url,series.bounds,{opacity:alpha,interactive:false}).addTo(this.map);this.native.getElement().dataset.sourceUrl=pair.left.url;this.nativeKey=pair.left.url;}this.native.setOpacity(alpha);return;}
   this.native?.remove();this.native=null;this.nativeKey=null;this.canvas.hidden=false;const a=pair.left?cache.get(pair.left.url)?.image:null,b=pair.right?cache.get(pair.right.url)?.image:null;if((pair.left&&!a)||(pair.right&&!b))return;
   const image=b||a,w=Math.min(1024,image.naturalWidth),height=Math.max(1,Math.round(image.naturalHeight*w/image.naturalWidth));if(key!==this.key){this.canvas.width=w;this.canvas.height=height;this.key=key;}
   const c=this.context;c.clearRect(0,0,w,height);c.globalCompositeOperation='source-over';if(a){c.globalAlpha=1-pair.mix;c.drawImage(a,0,0,w,height);}if(b){c.globalCompositeOperation='lighter';c.globalAlpha=pair.mix;c.drawImage(b,0,0,w,height);}c.globalAlpha=1;c.globalCompositeOperation='source-over';
  },
  onRemove(map){map.off('moveend zoomend resize',this.position,this);this.native?.remove();this.canvas.remove();this.map=null;}
 });return new Raster();
}
