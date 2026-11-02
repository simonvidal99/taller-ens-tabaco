import numpy as np, pandas as pd, pyreadstat, warnings
from scipy import stats
from lifelines import CoxPHFitter
warnings.filterwarnings("ignore"); pd.set_option("display.width",220)
OUT="/Users/simonvidal/Desktop/workshop medi/analisis/"
f="/Users/simonvidal/Desktop/workshop medi/descargas_minsal/ens_mortalidad_2023/Base de datos Encuesta Nacional de Salud 2016-2017(ENS)+DEF2023.sav"
df,m=pyreadstat.read_sav(f); V=m.variable_value_labels
ta3=df.ta3.map(V["ta3"]).astype(str)
d=pd.DataFrame({"w":df.Fexp_F1p_Corr,"h":df.Estrato,"c":df.Conglomerado,"edad":df.Edad,"mujer":(df.Sexo==2).astype(int),"zona":df.Zona})
d["estado"]=np.select([ta3.str.contains("NUNCA"),ta3.str.contains("HE DEJADO"),ta3.str.contains("OCASIONALMENTE"),ta3.str.contains("UNO O MÁS")],["nunca","ex","ocasional","diario"],default="")
d.loc[d.estado=="","estado"]=np.nan
hrs=df[["ta11_1","ta11_2","ta12_1","ta12_2","ta13_1","ta13_2"]]
d["exp_casa"]=((df.ta11_1>0)|(df.ta11_2>0)).astype(int)
d["exp_trab"]=((df.ta12_1>0)|(df.ta12_2>0)).astype(int)
d["exp_otro"]=((df.ta13_1>0)|(df.ta13_2>0)).astype(int)
d["exp_any"]=(d[["exp_casa","exp_trab","exp_otro"]].sum(axis=1)>0).astype(int)
print("estratos:",d.h.nunique(),"conglomerados:",d.groupby('h').c.nunique().sum(),"| estratos con 1 solo conglomerado:",(d.groupby('h').c.nunique()==1).sum())
print("N población (suma pesos):",round(d.w.sum()),"| edad min:",d.edad.min())
# estimador de proporción con linealización (ultimate cluster)
def prop(x,w,h,c):
    k=x.notna()&(w>0); x,w,h,c=x[k],w[k],h[k],c[k]
    p=(w*x).sum()/w.sum(); u=(w*(x-p)/w.sum()).groupby([h,c]).sum()
    g=u.groupby(level=0); nh=g.count(); mu=g.transform("mean")
    v=((u-mu)**2).groupby(level=0).sum()*(nh/(nh-1).replace(0,np.nan)); v=v.dropna().sum()
    se=np.sqrt(v); df_=(nh>1).sum()*0+ (nh.sum()-len(nh)); t=stats.t.ppf(.975,max(df_,1))
    return p*100,max(0,(p-t*se))*100,min(1,(p+t*se))*100,int(k.sum())
def fmt(r): return f"{r[0]:.1f} ({r[1]:.1f}-{r[2]:.1f})"
d["gedad"]=pd.cut(d.edad,[14,24,44,64,120],labels=["15-24","25-44","45-64","65+"])
d["sexoL"]=d.mujer.map({0:"Hombres",1:"Mujeres"}); d["zonaL"]=d.zona.map({1:"Urbana",2:"Rural"})
d["actual"]=d.estado.isin(["diario","ocasional"]).astype(float).where(d.estado.notna())
ind={"Fumador actual (diario u ocasional)":d.actual,"  Fuma a diario":(d.estado=="diario").astype(float).where(d.estado.notna()),
 "  Fuma ocasionalmente":(d.estado=="ocasional").astype(float).where(d.estado.notna()),"Ex fumador":(d.estado=="ex").astype(float).where(d.estado.notna()),
 "Nunca fumó":(d.estado=="nunca").astype(float).where(d.estado.notna())}
rows=[]
for nm,y in ind.items():
    r={"Indicador":nm,"Total":fmt(prop(y,d.w,d.h,d.c))}
    for g in ["sexoL","zonaL","gedad"]:
        for k in sorted(d[g].dropna().unique(),key=str):
            s=d[g]==k; r[str(k)]=fmt(prop(y[s],d.w[s],d.h[s],d.c[s]))
    rows.append(r)
# pasivos
nf=d.estado.isin(["nunca","ex"]); nn=d.estado=="nunca"
for nm,y in {"Expuesto al humo ajeno, algún ambiente (TODOS)":d.exp_any,"  en el hogar (TODOS)":d.exp_casa,"  en trabajo/estudio (TODOS)":d.exp_trab,"  otros ambientes (TODOS)":d.exp_otro}.items():
    r={"Indicador":nm,"Total":fmt(prop(y.astype(float),d.w,d.h,d.c))}
    for g in ["sexoL","zonaL","gedad"]:
        for k in sorted(d[g].dropna().unique(),key=str):
            s=d[g]==k; r[str(k)]=fmt(prop(y[s].astype(float),d.w[s],d.h[s],d.c[s]))
    rows.append(r)
for nm,mask in [("FUMADOR PASIVO: no fuma actualmente (nunca+ex), expuesto",nf),("FUMADOR PASIVO: nunca fumó, expuesto",nn)]:
    y=d.exp_any.astype(float); r={"Indicador":nm,"Total":fmt(prop(y[mask],d.w[mask],d.h[mask],d.c[mask]))}
    for g in ["sexoL","zonaL","gedad"]:
        for k in sorted(d[g].dropna().unique(),key=str):
            s=mask&(d[g]==k); r[str(k)]=fmt(prop(y[s],d.w[s],d.h[s],d.c[s]))
    rows.append(r)
t=pd.DataFrame(rows); print("\nPREVALENCIAS % (IC95%) — ENS 2016-17, diseño: estrato+conglomerado+Fexp_F1p_Corr\n"); print(t.to_string(index=False)); t.to_csv(OUT+"ens2016_prevalencias.csv",index=False)
# personas estimadas
N=d.w.sum(); a=d.actual.notna()&(d.w>0); print("\nFumadores actuales estimados (millones):",round(((d.actual*d.w)[a].sum()/d.w[a].sum())*N/1e6,2),"de",round(N/1e6,2))
# Mortalidad
ent=pd.to_datetime(df.Fechaini_F1); fdef=pd.to_datetime(df.FECHA_DEF,errors="coerce"); dead=df.ANO_DEF.notna()
tt=((fdef.where(dead,pd.Timestamp("2023-12-31"))-ent).dt.days/365.25).clip(lower=1/365.25)
d["t"]=tt; d["muerto"]=dead.astype(int)
d["g_nunca_noexp"]=((d.estado=="nunca")&(d.exp_any==0)).astype(float); 
d["pasivo"]=((d.estado=="nunca")&(d.exp_any==1)).astype(float); d["ex_"]=(d.estado=="ex").astype(float); d["act"]=d.estado.isin(["diario","ocasional"]).astype(float)
def cox(cols,x,label):
    x=x[["t","muerto","w","c"]+cols].dropna(); x=x[x.w>0]
    c=CoxPHFitter().fit(x,"t","muerto",weights_col="w",cluster_col="c")
    s=c.summary[["exp(coef)","exp(coef) lower 95%","exp(coef) upper 95%","p"]].round(3); s.columns=["HR","IC_inf","IC_sup","p"]; s.insert(0,"modelo",label); s["n"]=len(x); s["muertes"]=int(x.muerto.sum()); return s
res=[]
k=d.estado.notna()
res.append(cox(["pasivo","ex_","act","edad","mujer"],d[k],"A. 4 grupos (ref: nunca fumó y sin exposición)"))
nev=d[d.estado=="nunca"]
res.append(cox(["exp_any","edad","mujer"],nev,"B. Solo nunca fumadores: expuesto vs no"))
res.append(cox(["exp_casa","exp_trab","exp_otro","edad","mujer"],nev,"C. Solo nunca fumadores: por ambiente"))
nfm=d[nf]; res.append(cox(["exp_any","edad","mujer"],nfm,"D. Nunca+ex fumadores: expuesto vs no"))
R=pd.concat(res); R.to_csv(OUT+"ens2016_cox_tabaco_pasivo.csv"); print("\nMORTALIDAD y exposición pasiva (cluster-robusto, ponderado)\n"); print(R.to_string())
print("\nn por grupo (4 grupos):",{"ref nunca sin exp":int(d.g_nunca_noexp[k].sum()),"pasivo":int(d.pasivo[k].sum()),"ex":int(d.ex_[k].sum()),"actual":int(d.act[k].sum())})
print("muertes por grupo:",{"ref":int(d.muerto[k&(d.g_nunca_noexp==1)].sum()),"pasivo":int(d.muerto[k&(d.pasivo==1)].sum()),"ex":int(d.muerto[k&(d.ex_==1)].sum()),"actual":int(d.muerto[k&(d.act==1)].sum())})
