import re, pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.ticker
A="/Users/simonvidal/Desktop/workshop medi/analisis/"; O="/Users/simonvidal/Desktop/workshop medi/taller/presentacion/figs/"
AZ,RJ,GR="#1b6ca8","#c0392b","#6b7280"
plt.rcParams.update({"font.size":15,"axes.spines.top":False,"axes.spines.right":False,"font.family":"sans-serif"})
P=pd.read_csv(A+"ens2016_prevalencias.csv")
def parse(s):
    a=re.match(r"\s*([\d.]+) \(([\d.]+)-([\d.]+)\)",s); return tuple(map(float,a.groups()))
r=P[P.Indicador.str.startswith("Fumador actual")].iloc[0]
cols=["Total","Hombres","Mujeres","Urbana","Rural","15-24","25-44","45-64","65+"]
v=[parse(r[c]) for c in cols]
fig,ax=plt.subplots(figsize=(10,4.6))
colr=[GR]+[AZ]*4+[RJ]*4
for i,(c,(p,lo,hi)) in enumerate(zip(cols,v)):
    ax.bar(i,p,color=colr[i],width=.7); ax.errorbar(i,p,yerr=[[p-lo],[hi-p]],color="k",capsize=4,lw=1.5)
    ax.text(i,hi+1.2,f"{p:.1f}".replace(".",","),ha="center",fontsize=14,fontweight="bold")
ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols); ax.set_ylabel("Fumador actual (%)"); ax.set_ylim(0,52)
ax.axvline(0.5,color="#ddd"); ax.axvline(4.5,color="#ddd",ls="--")
plt.tight_layout(); plt.savefig(O+"fig_prevalencia.png",dpi=170); plt.close()
# pasivo por ambiente (entre quienes no fuman: tomamos filas TODOS no; usar las de total poblacion)
rows={"Algún ambiente":"Expuesto al humo ajeno, algún ambiente (TODOS)","Hogar":"  en el hogar (TODOS)","Trabajo/estudio":"  en trabajo/estudio (TODOS)","Otros ambientes":"  otros ambientes (TODOS)"}
fig,ax=plt.subplots(figsize=(7.2,4.4))
for i,(k,n) in enumerate(rows.items()):
    p,lo,hi=parse(P[P.Indicador==n].iloc[0]["Total"]); ax.barh(i,p,color=AZ if i else GR); ax.errorbar(p,i,xerr=[[p-lo],[hi-p]],color="k",capsize=4)
    ax.text(hi+1,i,f"{p:.1f}".replace(".",","),va="center",fontweight="bold")
ax.set_yticks(range(4)); ax.set_yticklabels(list(rows)); ax.invert_yaxis(); ax.set_xlabel("% de la población 15+ expuesta al humo ajeno"); ax.set_xlim(0,48)
plt.tight_layout(); plt.savefig(O+"fig_pasivo.png",dpi=170); plt.close()
# forest
T=pd.read_csv(A+"ens2016_cox_tabaco_pasivo.csv"); M=pd.read_csv(A+"ens2016_cox_mortalidad_total.csv")
g=lambda df,mod,cov:df[(df.modelo.str.startswith(mod))&(df.covariate==cov)].iloc[0]
items=[("Fumador actual vs no\nSIN ajustar",g(M,"1.","actual" if "actual" in M.covariate.values else "fuma"),GR),
       ("Fumador actual vs no\najustado edad y sexo",g(M,"2.","actual"),AZ),
       ("Pasivo (nunca fumó, expuesto)",g(T,"A.","pasivo"),AZ),
       ("Ex fumador",g(T,"A.","ex_"),AZ),("Fumador actual",g(T,"A.","act"),RJ)]
fig,ax=plt.subplots(figsize=(10,4.6))
for i,(lab,row,c) in enumerate(items):
    ax.errorbar(row.HR,i,xerr=[[row.HR-row.IC_inf],[row.IC_sup-row.HR]],fmt="o",color=c,capsize=5,ms=9,lw=2.2)
    f2=lambda x: f"{round(x+1e-9,2):.2f}"
    ax.text(3.35,i,f"{f2(row.HR)} ({f2(row.IC_inf)}–{f2(row.IC_sup)})".replace(".",","),va="center",fontsize=13)
ax.axvline(1,color="k",ls="--",lw=1); ax.set_xscale("log"); ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator()); ax.set_xticks([.5,1,2,3]); ax.set_xticklabels(["0,5","1","2","3"]); ax.set_xlim(.3,3.3)
ax.set_yticks(range(len(items))); ax.set_yticklabels([i[0] for i in items]); ax.invert_yaxis(); ax.set_xlabel("Razón de riesgo (HR) de morir  —  referencia: 1")
ax.axhline(1.5,color="#ddd")
plt.tight_layout(); plt.subplots_adjust(right=0.74); plt.savefig(O+"fig_forest.png",dpi=170); plt.close()
import shutil; shutil.copy(A+"ens2016_supervivencia_KM_por_tabaco.png",O+"fig_km.png"); print("ok",items[0][1].to_dict())
