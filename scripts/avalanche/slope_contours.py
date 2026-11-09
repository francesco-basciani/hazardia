"""Continuous terrain contours from actual slope samples, not decorative smoothing."""
def filled_slope_contours(values,affine,level=30,simplify_m=3):
 import numpy as np,matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from shapely.geometry import Polygon,GeometryCollection
 from shapely.ops import unary_union
 a=np.ma.masked_invalid(values)
 if a.count()==0 or float(a.max())<level:return GeometryCollection()
 xs=affine.c+(np.arange(a.shape[1])+.5)*affine.a
 ys=affine.f+(np.arange(a.shape[0])+.5)*affine.e
 fig,ax=plt.subplots()
 try:
  contour=ax.contourf(xs,ys,a,levels=[level,91],corner_mask=False)
  polygons=[]
  for path in contour.collections[0].get_paths():
   rings=path.to_polygons()
   if not rings:continue
   polygon=Polygon(rings[0],rings[1:])
   if not polygon.is_valid:polygon=polygon.buffer(0)
   if not polygon.is_empty:polygons.append(polygon)
  result=unary_union(polygons)
  return result.simplify(simplify_m,preserve_topology=True) if simplify_m else result
 finally:plt.close(fig)
