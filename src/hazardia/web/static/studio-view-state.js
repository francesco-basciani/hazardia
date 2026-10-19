/* Playback clocks belong to a browser tab, never to the VM job worker. */
export function playbackEntryHour(saved,navigationType='navigate'){
 if(!saved||!Number.isFinite(saved.hour)||saved.hour<0||saved.hour>72)return 0;
 const recoverCalculation=saved.batchActive&&Number.isFinite(saved.resumeFromHour);
 return recoverCalculation||navigationType==='reload'||navigationType==='back_forward'?saved.hour:0;
}
