/* Display-only raster clipping in screen space; native pixels and georeferencing stay unchanged. */
export function rasterComparison({map,divider,handle}) {
  let position=50,enabled=false,drag=null;
  const layers=new Set();
  function update() {
    const box=map.getContainer().getBoundingClientRect(),cut=box.left+box.width*position/100;
    divider.style.left=position+'%';
    const pixels=box.width*position/100;handle.style.transform='translate('+(pixels<23?'0':pixels>box.width-23?'-100':'-50')+'%, -50%)';
    handle.setAttribute('aria-valuenow',String(Math.round(position)));
    handle.setAttribute('aria-valuetext',Math.round(position)+'% sinistra, '+Math.round(100-position)+'% destra');
    for(const entry of layers) {
      const image=entry.layer.getElement();if(!image)continue;
      if(!enabled||!entry.side){image.style.clipPath='';continue;}
      const rect=image.getBoundingClientRect();if(!rect.width)continue;
      const p=Math.max(0,Math.min(100,100*(cut-rect.left)/rect.width));
      image.style.clipPath=entry.side==='left'?`inset(0 ${100-p}% 0 0)`:`inset(0 0 0 ${p}%)`;
      image.dataset.compareSide=entry.side;
    }
  }
  function setPosition(value){position=Math.max(0,Math.min(100,value));update();}
  function endDrag(e){if(e&&drag&&e.pointerId!==drag.id)return;if(drag?.mapWasEnabled)map.dragging.enable();drag=null;}
  handle.addEventListener('pointerdown',e=>{
    if(drag||e.button!==0)return;e.preventDefault();e.stopPropagation();
    drag={id:e.pointerId,mapWasEnabled:map.dragging.enabled()};map.dragging.disable();handle.setPointerCapture(e.pointerId);
  });
  handle.addEventListener('pointermove',e=>{
    if(!drag||drag.id!==e.pointerId)return;
    const box=map.getContainer().getBoundingClientRect();setPosition((e.clientX-box.left)/box.width*100);
  });
  handle.addEventListener('pointerup',endDrag);handle.addEventListener('pointercancel',endDrag);handle.addEventListener('lostpointercapture',endDrag);
  handle.addEventListener('keydown',e=>{
    const delta=e.shiftKey?10:2;
    const values={ArrowLeft:position-delta,ArrowDown:position-delta,ArrowRight:position+delta,ArrowUp:position+delta,Home:0,End:100};
    if(e.key in values){e.preventDefault();e.stopPropagation();setPosition(values[e.key]);}
  });
  handle.addEventListener('click',e=>e.stopPropagation());
  map.on('move zoom zoomend resize',update);
  return {
    add(layer,side){const entry={layer,side};layers.add(entry);layer.on('load',update);update();},
    clear(){layers.clear();},
    enable(value){enabled=value;divider.hidden=!value;if(!value)endDrag();update();},
    update,
  };
}
