import numpy as np, pandas as pd, pyreadstat, warnings, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lifelines import CoxPHFitter, KaplanMeierFitter
warnings.filterwarnings("ignore")
OUT="/Users/simonvidal/Desktop/workshop medi/analisis/"
f="/Users/simonvidal/Desktop/workshop medi/descargas_minsal/ens_mortalidad_2023/ENS_2003_Ministerio_de_Salud_Chile_Dpto_Epidemiología_VENT+DEF2023.sav"
df,m=pyreadstat.read_sav(f,encoding="latin1")
# fecha de entrada
ok=df.v2_a.between(2003,2003)&df.v2_m.between(1,12)&df.v2_d.between(1,31)
ent=pd.to_datetime(dict(year=df.v2_a.where(ok),month=df.v2_m.where(ok),day=df.v2_d.where(ok)),errors="coerce")
med=ent.dropna().sort_values().iloc[len(ent.dropna())//2]
print("fechas de entrada válidas:",ent.notna().sum(),"| rango:",ent.min().date(),ent.max().date(),"| mediana (imputada al resto):",med.date())
ent=ent.fillna(med)
dead=df.ANO_DEF.notna()
fdef=pd.to_datetime(df.FECHA_DEF,errors="coerce")
end=pd.Timestamp("2023-12-31")
t=((fdef.where(dead,end)-ent).dt.days/365.25)
print("muertes con fecha antes de entrada:",(t<=0)[dead].sum(),"-> se fija en 1 día")
t=t.clip(lower=1/365.25)
d=pd.DataFrame({"t":t,"muerto":dead.astype(int),"edad":df.edad,"mujer":(df.sexo==2).astype(int),"w":df.fact_af1,
 "fuma":df.Fumador_Actual,"diag":df.DIAG1.astype(str).str.strip()})
# estado tabaco 3 niveles
st=pd.Series(np.nan,index=df.index)
st[df.p111==2]=0                       # nunca
st[df.p112==3]=1                       # ex fumador
st[df.p112.isin([1,2])]=2              # actual
st[(df.Fumador_Actual==1)&st.isna()]=2 # los <1 mes de Fumador_Actual
d["estado"]=st
print("\nestado tabaco (0 nunca,1 ex,2 actual):",d.estado.value_counts(dropna=False).sort_index().to_dict())
print("tiempo seguimiento mediano (años):",round(d.t.median(),1),"| personas-año:",round(d.t.sum()))
# 1) mortalidad por edad: ¿quién muere?
d["gedad"]=pd.cut(d.edad,[15,39,59,74,120],labels=["16-39","40-59","60-74","75+"])
tab=d.dropna(subset=["fuma"]).groupby(["gedad","fuma"],observed=True).muerto.agg(["mean","sum","count"])
tab["mean"]=(tab["mean"]*100).round(1); print("\nMortalidad cruda (%) por edad y tabaco (fuma 0=no,1=sí):\n",tab.to_string())
tab.to_csv(OUT+"mortalidad_cruda_por_edad_y_tabaco.csv")
# 2) Cox
def cox(cols,data,label):
    x=data[["t","muerto","w"]+cols].dropna(); x=x[x.w>0]
    c=CoxPHFitter().fit(x,"t","muerto",weights_col="w",robust=True)
    s=c.summary[["exp(coef)","exp(coef) lower 95%","exp(coef) upper 95%","p"]].round(3); s.columns=["HR","IC_inf","IC_sup","p"]; s.insert(0,"modelo",label); s["n"]=len(x); s["muertes"]=int(x.muerto.sum())
    return s,c
r=[]
s,_=cox(["fuma"],d,"1. Sin ajustar"); r.append(s)
s,c2=cox(["fuma","edad","mujer"],d,"2. Ajustado edad+sexo"); r.append(s)
d["ex"]=(d.estado==1).astype(float).where(d.estado.notna()); d["actual"]=(d.estado==2).astype(float).where(d.estado.notna())
s,_=cox(["ex","actual","edad","mujer"],d,"3. Nunca/ex/actual, ajust."); r.append(s)
# dosis: cigarrillos/día entre fumadores actuales
d["cig"]=df.p113_t.where(df.p113_t<99)
x=d[d.estado==2]; x=x.assign(cig10=x.cig/10, anos10=df.p114_a.where(df.p114_a<99).loc[x.index]/10)
s,_=cox(["cig10","edad","mujer"],x,"4. Dosis: +10 cig/día (solo actuales)"); r.append(s)
res=pd.concat(r); res.to_csv(OUT+"cox_mortalidad_total.csv"); print("\n",res.to_string())
# 3) por causa
def causa(dg):
    if dg.startswith(("C33","C34")): return "Cáncer pulmón"
    if dg.startswith("C"): return "Otros cánceres"
    if dg.startswith("I"): return "Circulatorio"
    if dg.startswith("J"): return "Respiratorio"
    if dg[:1] in "VWXY": return "Causas externas"
    return "Otras" if dg else ""
d["causa"]=d.diag.map(causa); print("\nmuertes por causa:",d[d.muerto==1].causa.value_counts().to_dict())
rc=[]
for cz in ["Circulatorio","Cáncer pulmón","Otros cánceres","Respiratorio","Causas externas"]:
    y=d.assign(ev=((d.causa==cz)&(d.muerto==1)).astype(int)).drop(columns="muerto").rename(columns={"ev":"muerto"})
    if y.muerto.sum()<15: continue
    s,_=cox(["fuma","edad","mujer"],y,cz); rc.append(s.loc[["fuma"]])
rc=pd.concat(rc); rc.to_csv(OUT+"cox_por_causa.csv"); print("\nHR fumador actual vs no, por causa (ajust. edad+sexo):\n",rc.to_string())
# 4) KM 40-59
fig,ax=plt.subplots(1,2,figsize=(11,4.2))
for a,(lo,hi) in zip(ax,[(40,59),(60,120)]):
    z=d[(d.edad>=lo)&(d.edad<=hi)].dropna(subset=["fuma"]); z=z[z.w>0]
    for v,lab,col in [(0,"No fuma","#1b6ca8"),(1,"Fuma actual","#c0392b")]:
        k=KaplanMeierFitter().fit(z.t[z.fuma==v],z.muerto[z.fuma==v],weights=z.w[z.fuma==v],label=f"{lab} (n={int((z.fuma==v).sum())})"); k.plot_survival_function(ax=a,color=col,ci_show=False)
    a.set_title(f"Supervivencia, edad {lo}-{hi if hi<120 else '+'} al ingreso"); a.set_xlabel("Años desde la encuesta (2003)"); a.set_ylabel("Proporción viva"); a.set_ylim(0,1.02); a.grid(alpha=.3)
plt.tight_layout(); plt.savefig(OUT+"supervivencia_KM_por_tabaco.png",dpi=130)
print("\nfigura guardada")
