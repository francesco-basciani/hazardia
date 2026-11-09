// Rendering eligibility only; native hazard/snow values and geometries are preserved.
export function potentialSurface(p){
 if(p.potential_class>=3)return {visible:true,kind:'potential'};
 if(p.terrain_steep===true&&[0,2].includes(p.potential_class))return {visible:true,kind:'unverified_slope'};
 return {visible:false,kind:'not_mapped_steep_slope'};
}
