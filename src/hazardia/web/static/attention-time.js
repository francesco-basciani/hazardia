/* A bulletin day is metadata; only the half-open validity window selects a product. */
export function productAt(products,at){
 const t=Date.parse(at);if(!Number.isFinite(t))return null;
 return products.find(p=>Date.parse(p.valid_from)<=t&&t<Date.parse(p.valid_until))||null;
}
export function validityState(products,at,isFresh){
 const product=productAt(products,at);
 return {product,status:!product?'UNAVAILABLE':isFresh(product)?'FRESH':'STALE'};
}
