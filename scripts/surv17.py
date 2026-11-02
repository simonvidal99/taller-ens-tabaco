import numpy as np, pandas as pd, pyreadstat, warnings, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lifelines import CoxPHFitter, KaplanMeierFitter
warnings.filterwarnings("ignore")
OUT="/Users/simonvidal/Desktop/workshop medi/analisis/"
f="/Users/simonvidal/Desktop/workshop medi/descargas_minsal/ens_mortalidad_2023/Base de datos Encuesta Nacional de Salud 2016-2017(ENS)+DEF2023.sav"
df,m=pyreadstat.read_sav(f); V=m.variable_value_labels
print("Sexo:",df.Sexo.value_counts().to_dict(),V.get("Sexo"))
ent=pd.to_datetime(df.Fechaini_F1,errors="coerce"); print("entrada inválida:",ent.isna().sum(),"| rango:",ent.min().date(),ent.max().date())
fdef=pd.to_datetime(df.FECHA_DEF,errors="coerce"); dead=df.ANO_DEF.notna()
print("muertes sin fecha parseable:",(dead&fdef.isna()).sum())
end=pd.Timestamp("2023-12-31")
t=((fdef.where(dead,end)-ent).dt.days/365.25); print("muertes con fecha <= entrada:",(t<=0)[dead].sum()); t=t.clip(lower=1/365.25)
ta3=df.ta3.map(V["ta3"]).astype(str)
d=pd.DataFrame({"t":t,"muerto":dead.astype(int),"edad":df.Edad,"mujer":(df.Sexo==2).astype(int),"w":df.Fexp_F1p_Corr,"cl":df.Conglomerado,
  "rural":(df.Zona!=1).astype(int),"diag":df.DIAG1.astype(str).str.strip()})
d["estado"]=np.select([ta3.str.contains("NUNCA"),ta3.str.contains("HE DEJADO"),ta3.str.contains("OCASIONALMENTE"),ta3.str.contains("UNO O MÁS")],[0,1,2,3],default=np.nan)
d.loc[d.estado.isna(),"estado"]=np.nan
print("estado (0 nunca,1 ex,2 ocasional,3 diario):",d.estado.value_counts(dropna=False).sort_index().to_dict())
d["actual"]=d.estado.isin([2,3]).astype(float).where(d.estado.notna())
print("Zona valores:",df.Zona.value_counts().to_dict(),"| edad:",df.Edad.describe()[["min","mean","max"]].round(1).to_dict())
print("seguimiento mediano (años):",round(d.t.median(),1),"| pers-año:",round(d.t.sum()))
d["gedad"]=pd.cut(d.edad,[17,39,59,74,120],labels=["18-39","40-59","60-74","75+"])
tab=d.dropna(subset=["actual"]).groupby(["gedad","actual"],observed=True).muerto.agg(["mean","sum","count"]); tab["mean"]=(tab["mean"]*100).round(1)
print("\nMortalidad cruda % por edad y tabaco (actual 0/1):\n",tab.to_string()); tab.to_csv(OUT+"ens2016_mortalidad_cruda_por_edad_y_tabaco.csv")
def cox(cols,data,label,nm=None):
    x=data[["t","muerto","w","cl"]+cols].dropna(); x=x[x.w>0]
    c=CoxPHFitter().fit(x,"t","muerto",weights_col="w",cluster_col="cl")
    s=c.summary[["exp(coef)","exp(coef) lower 95%","exp(coef) upper 95%","p"]].round(3); s.columns=["HR","IC_inf","IC_sup","p"]
    s.insert(0,"modelo",label); s["n"]=len(x); s["muertes"]=int(x.muerto.sum()); return s
r=[]
r.append(cox(["actual"],d,"1. Sin ajustar"))
r.append(cox(["actual","edad","mujer"],d,"2. Ajust. edad+sexo"))
r.append(cox(["actual","edad","mujer","rural"],d,"3. Ajust. edad+sexo+zona"))
d["ex"]=(d.estado==1).astype(float).where(d.estado.notna()); d["ocas"]=(d.estado==2).astype(float).where(d.estado.notna()); d["diario"]=(d.estado==3).astype(float).where(d.estado.notna())
r.append(cox(["ex","ocas","diario","edad","mujer"],d,"4. Nunca(ref)/ex/ocasional/diario"))
# dosis cig/día
cig=df.ta4.where(df.ta4<90); d["cig"]=cig
x=d[d.estado==3].copy(); x["c10_19"]=x.cig.between(10,19).astype(float).where(x.cig.notna()); x["c20"]=(x.cig>=20).astype(float).where(x.cig.notna())
r.append(cox(["c10_19","c20","edad","mujer"],x,"5. Diarios: 10-19 y >=20 cig vs <10"))
# sensibilidad: excluir 2 primeros años
d2=d.copy(); keep=~((d2.muerto==1)&(d2.t<2)); r.append(cox(["actual","edad","mujer"],d2[keep],"6. Excluye muertes <2 años"))
res=pd.concat(r); res.to_csv(OUT+"ens2016_cox_mortalidad_total.csv"); print("\n",res.to_string())
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
    if y.muerto.sum()<10: print("omitida (pocas muertes):",cz,int(y.muerto.sum())); continue
    rc.append(cox(["actual","edad","mujer"],y,cz).loc[["actual"]])
rc=pd.concat(rc); rc.to_csv(OUT+"ens2016_cox_por_causa.csv"); print("\nHR fumador actual vs no por causa (ajust. edad+sexo):\n",rc.to_string())
fig,ax=plt.subplots(1,2,figsize=(11,4.2))
for a,(lo,hi) in zip(ax,[(40,59),(60,120)]):
    z=d[(d.edad>=lo)&(d.edad<=hi)].dropna(subset=["actual"]); z=z[z.w>0]
    for v,lab,col in [(0,"No fuma","#1b6ca8"),(1,"Fuma actual","#c0392b")]:
        k=KaplanMeierFitter().fit(z.t[z.actual==v],z.muerto[z.actual==v],weights=z.w[z.actual==v],label=f"{lab} (n={int((z.actual==v).sum())})"); k.plot_survival_function(ax=a,color=col,ci_show=False)
    a.set_title(f"ENS 2016-17: supervivencia, edad {lo}-{hi if hi<120 else '+'}"); a.set_xlabel("Años desde la encuesta"); a.set_ylabel("Proporción viva"); a.set_ylim(0.5,1.01); a.grid(alpha=.3)
plt.tight_layout(); plt.savefig(OUT+"ens2016_supervivencia_KM_por_tabaco.png",dpi=130); print("\nfigura ok")
