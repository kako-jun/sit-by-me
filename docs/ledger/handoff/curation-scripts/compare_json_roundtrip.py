import sys,json
sys.path.insert(0,'/home/kako-jun/repos/2026/sit-by-me-wt-ledger-master/.claude/skills/sit-field-background/tools')
import ledger_build as B
O='/tmp/claude-1001/-home-kako-jun-repos-private-freeza/9f3f94f0-2c9d-45f2-a837-2e8539f6df7f/scratchpad/lm/orig/'
def norm(o):
    if isinstance(o,dict): return {k:norm(v) for k,v in o.items() if not(v in ([],None) and not isinstance(v,(int,float)) ) and k!='_provenance'}
    if isinstance(o,list): return [norm(x) for x in o]
    return o
def diff(a,b,path=''):
    out=[]
    if isinstance(a,dict) and isinstance(b,dict):
        for k in sorted(set(a)|set(b)):
            if k not in a: out.append((path+'/'+k,'<none>',b[k]))
            elif k not in b: out.append((path+'/'+k,a[k],'<none>'))
            else: out+=diff(a[k],b[k],path+'/'+k)
    elif isinstance(a,list) and isinstance(b,list) and len(a)==len(b):
        for i,(x,y) in enumerate(zip(a,b)): out+=diff(x,y,f'{path}[{i}]')
    elif a!=b: out.append((path,a,b))
    return out
def run(verbose=5):
    T=B.tables(); res={}
    for m in ['TRM-05','TRM-04','TRM-02','TRM-03']:
        res[m]=diff(norm(json.load(open(O+m+'-plan.json'))),norm(B.build_plan(T,m)))
    res['decor']=diff(norm(json.load(open(O+'decor-pools.json'))),norm(B.build_decor(T)))
    res['conn']=diff(norm(json.load(open(O+'connections.json'))),norm(B.build_connections(T)))
    return res
if __name__=='__main__':
    for k,d in run().items():
        print(k,len(d)); [print('  ',str(x)[:300]) for x in d[:int(sys.argv[1]) if len(sys.argv)>1 else 5]]
