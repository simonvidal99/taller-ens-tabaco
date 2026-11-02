import sys, numpy as np, pyreadstat, pandas as pd
pd.set_option("display.width",220)
df, meta = pyreadstat.read_sav(sys.argv[1], encoding="latin1")
W = {"hta1":"fact_af2","hta":"fact_af2","obesidad1":"fact_af2","sind_met":"fact_aex","diabetes1":"fact_aex",
     "dislipidemia1":"fact_aex","renal1":"fact_aex","depresion1":"fact_af1","ecv1":"fact_af1","epoc1":"fact_af1"}
NAME = {"hta1":"HTA","obesidad1":"Obesidad (IMC>=30)","diabetes1":"Diabetes","dislipidemia1":"Dislipidemia",
        "sind_met":"Síndrome metabólico","renal1":"Insuf. renal crónica","depresion1":"Depresión (último año)",
        "ecv1":"Enf. cardiovascular sintom.","epoc1":"Síntomas resp. crónicos"}
def prev(d, c):
    w = d[W[c]]; m = d[c].notna() & (w>0); x=d.loc[m,c]; w=w[m]
    if len(x)==0: return (np.nan,)*3+(0,)
    p=(x*w).sum()/w.sum(); neff=w.sum()**2/(w**2).sum()
    se=np.sqrt(p*(1-p)/neff)   # Kish n efectivo, sin diseño muestral
    return p*100,(p-1.96*se)*100,(p+1.96*se)*100,len(x)
df["edadg"]=pd.cut(df.edad,[15,24,44,64,120],labels=["16-24","25-44","45-64","65+"])
df["sexoL"]=df.sexo.map({1:"Hombres",2:"Mujeres"}); df["zonaL"]=df.zona.map({1:"Urbana",2:"Rural"})
rows=[]
for c in NAME:
    r={"Condición":NAME[c],"Pond.":W[c]}
    p,l,u,n=prev(df,c); r["Total"]=f"{p:.1f} ({l:.1f}-{u:.1f})"; r["n"]=n
    for g in ["sexoL","zonaL","edadg"]:
        for k,d in df.groupby(g,observed=True): r[str(k)]=f"{prev(d,c)[0]:.1f}"
    rows.append(r)
t=pd.DataFrame(rows); print(t.to_string(index=False))
t.to_csv(sys.argv[2],index=False)
print("\nHTA cruda sin ponderar:", round(df.hta1.mean()*100,1))
# hta por tomas
print("\nHTA medida (PAS>=140 o PAD>=90, prom 2 tomas) ponderada af2:")
s=(df.pa_sis1+df.pa_sis2)/2; d_=(df.pa_dia1+df.pa_dia2)/2
m=s.notna()&(df.fact_af2>0); h=((s>=140)|(d_>=90))[m]; w=df.fact_af2[m]
print(round((h*w).sum()/w.sum()*100,1), "n=",m.sum())
print("hta1 vs ar_hta (dx previo) cruce n:"); print(pd.crosstab(df.hta1,df.ar_hta))
