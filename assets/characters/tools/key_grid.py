"""3x3 クロマキーのグリッドを透過にし、つながったかたまりごとに重心のコマへ振り分けて切り出す
（枠をはみ出した刃・手足も切らない）。usage: key_grid2.py grid.png outdir name green|magenta [flip_idx,...]"""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage
src,outdir,name,key=sys.argv[1:5]
flips=set(int(x) for x in sys.argv[5].split(',')) if len(sys.argv)>5 and sys.argv[5] else set()
NAMES=['idle','ready','step','slash','hurt','down','cast','special','victory']
a=np.asarray(Image.open(src).convert('RGB')).astype(float)
r,g,b=a[...,0],a[...,1],a[...,2]
k=g-np.maximum(r,b) if key=='green' else np.minimum(r,b)-g
alpha=1-np.clip((k-40)/80,0,1)
out=a.copy()
if key=='green': out[...,1]=np.minimum(g,np.maximum(r,b)+10)
else:
    out[...,0]=np.where(k>0,np.minimum(r,g+30),r); out[...,2]=np.where(k>0,np.minimum(b,g+30),b)
H,W=alpha.shape
fg=alpha>0.08
lab,n=ndimage.label(fg)
areas=ndimage.sum(fg,lab,range(1,n+1))
cents=ndimage.center_of_mass(fg,lab,range(1,n+1))
def cell_of(cy,cx): return int(min(2,cx//(W/3))+3*min(2,cy//(H/3)))
# 各コマの体 = 重心がそのコマにある最大のかたまり
body={}
for li in range(1,n+1):
    cy,cx=cents[li-1]; c=cell_of(cy,cx)
    if areas[li-1]>=2000 and (c not in body or areas[li-1]>areas[body[c]-1]): body[c]=li
# 体ごとの距離場で、残りの破片をいちばん近い体へ
dist={c:ndimage.distance_transform_edt(lab!=li) for c,li in body.items()}
cells={i:np.zeros_like(fg) for i in range(9)}
for c,li in body.items(): cells[c]|=lab==li
for li in range(1,n+1):
    if li in body.values() or areas[li-1]<40: continue
    m=lab==li; ys,xs=np.where(m); y,x=ys[len(ys)//2],xs[len(xs)//2]
    c=min(body,key=lambda c:dist[c][y,x])
    if dist[c][y,x]<W/6: cells[c]|=m
rgba=np.dstack([out,alpha*255]).clip(0,255).astype(np.uint8)
os.makedirs(outdir,exist_ok=True)
for i,nm in enumerate(NAMES):
    m=cells[i]
    if not m.any(): print('EMPTY',nm); continue
    ys,xs=np.where(m); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    sub=rgba[y0:y1,x0:x1].copy(); sub[...,3]=np.where(m[y0:y1,x0:x1],sub[...,3],0)
    im=Image.fromarray(sub,'RGBA')
    if i in flips: im=im.transpose(Image.FLIP_LEFT_RIGHT)
    im.save(f'{outdir}/{name}-{nm}.png')
print('ok',name)
