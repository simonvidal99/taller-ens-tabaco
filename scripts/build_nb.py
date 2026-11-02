"""Construye los dos cuadernos del taller (participantes y facilitador) desde una sola fuente."""
import sys, nbformat as nbf

OUT = "/Users/simonvidal/Desktop/workshop medi/taller/"

def md(t): return nbf.v4.new_markdown_cell(t.strip())
def code(t): return nbf.v4.new_code_cell(t.strip())

def build(facilitador: bool):
    c = []
    claves = ["base", "edad", "cuanto", "prev", "pasivo", "humo", "grupos", "corr",
              "enganoso", "ajuste", "cuatro", "sens", "km", "redactar"]
    N = {k: i + 1 for i, k in enumerate(claves)}   # numeración única; las referencias cruzadas la usan

    def ejercicio(clave, titulo, enunciado, pista, solucion, stub="# TU CÓDIGO AQUÍ\n"):
        c.append(md(f"### ✏️ Ejercicio {N[clave]} — {titulo}\n\n{enunciado}\n\n> **Pista:** {pista}"))
        c.append(code(solucion if facilitador else stub))

    tipo = "FACILITADOR (con soluciones)" if facilitador else "PARTICIPANTES"
    c.append(md(f"""
# Taller: investigar con bases de datos existentes
## Tabaco (activo y pasivo) y riesgo de muerte — Encuesta Nacional de Salud 2016-17

**Versión {tipo}**

**Pregunta de investigación**
1. ¿Cuál es la prevalencia de fumadores y de fumadores pasivos en Chile?
2. ¿Cuál es la asociación entre la exposición al tabaco y el riesgo de muerte?

**Qué vamos a hacer:** ir de la pregunta al resultado, como en un trabajo que se pueda publicar:
`pregunta → datos → variables → prevalencias → asociación → sesgos → cómo reportarlo`.

**Sobre el uso de los datos.** Las bases de la ENS son públicas, anonimizadas y de descarga libre en
[epi.minsal.cl/bases-de-datos](https://epi.minsal.cl/bases-de-datos/). Las condiciones de uso del Minsal piden
**usarlas solo para investigación, citar la fuente y enviar copia de las publicaciones al Minsal**
([condiciones](https://epi.minsal.cl/condiciones-de-uso/)). Confirma con tu comité si tu institución exige alguna constancia.
"""))

    c.append(md("## 0. Preparar el entorno"))
    c.append(code("""
# Solo hace falta en Google Colab o si faltan librerías (puedes ignorar si ya las tienes)
%pip install -q pandas numpy scipy pyreadstat lifelines matplotlib
"""))
    c.append(code("""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import numpy as np, pandas as pd, pyreadstat
from scipy import stats
from lifelines import CoxPHFitter, KaplanMeierFitter
import matplotlib.pyplot as plt
pd.set_option("display.width", 200); pd.set_option("display.max_columns", 30)

# Ruta al archivo. Cámbiala si lo guardaste en otro lugar.
RUTA = Path("datos/Base de datos Encuesta Nacional de Salud 2016-2017(ENS)+DEF2023.sav")
RUTA.exists()
"""))

    c.append(md("""
## 1. Conocer la base

La base **ENS 2016-17 + defunciones 2023** une la encuesta con los registros de muerte hasta 2023.
Cada fila es una persona. Antes de analizar hay que saber **qué es una fila, qué población representa y con qué peso se cuenta**.

El [manual de uso](https://epi.minsal.cl/wp-content/uploads/2019/02/Manual_de_Uso_de_la_base_de_datos_de_la_Encuesta_Nacional_de_Salud_2016_F1_F2_F4_EX1_EX2_14022019.pdf)
indica que, para variables del **cuestionario F1** (como el tabaco), el ponderador es `Fexp_F1p_Corr`
(población objetivo: 14.518.969 personas de 15 años y más).
"""))
    c.append(code("""
df, meta = pyreadstat.read_sav(RUTA)
etiq_var = meta.column_names_to_labels      # nombre -> descripción
etiq_val = meta.variable_value_labels       # nombre -> {código: etiqueta}
print(df.shape)
"""))
    c.append(code("""
# Variables de tabaco del cuestionario (empiezan con 'ta')
for v in [v for v in df.columns if v.startswith("ta") and v[2:3].isdigit()][:22]:
    print(f"{v:8} {etiq_var[v][:95]}")
"""))
    ejercicio(
        "base", "Explora la base",
        "a) ¿Qué variables indican que una persona **falleció** y cuándo? b) ¿Qué variable es el ponderador y cuáles identifican el diseño muestral (estratos y conglomerados)?",
        "Mira las últimas columnas de la base (`df.columns[-10:]`) y busca nombres con `DEF`, `Fexp`, `Estrato`, `Conglomerado`.",
        """
print(df.columns[-10:].tolist())
print([v for v in df.columns if v.startswith("Fexp")][:3], "...")
print("Estratos:", df.Estrato.nunique(), "| Conglomerados:", df.groupby("Estrato").Conglomerado.nunique().sum())
print("Personas con fecha de defunción:", df.ANO_DEF.notna().sum())
""")

    c.append(md("""
## 2. Construir las variables de análisis (ya hecho para ti)

Esta es la parte que más errores produce en un estudio real, así que **lee las decisiones**:

| Variable | Definición | Por qué |
|---|---|---|
| `estado` | nunca / ex / ocasional / diario | de la pregunta `ta3` («¿actualmente fuma cigarrillos?») |
| `fuma_actual` | diario u ocasional | exposición principal |
| `h_casa`, `h_trab`, `h_otro`, `h_exp` | horas diarias de humo ajeno en casa, trabajo/estudio y otros ambientes (la mayor entre día de semana y fin de semana); `h_exp` es la suma | preguntas `ta11`–`ta13` |
| `exp_any` | `h_exp > 0` (≥ 1 hora/día) | definición **nuestra** de exposición pasiva; no hay un estándar único |
| `cig_dia`, `edad_inicio` | cigarrillos al día (solo fumadores actuales) y edad a la que empezó a fumar (quienes alguna vez fumaron) | `ta4` y `ta6` |
| `imc`, `colest` | índice de masa corporal y colesterol total | examen físico y de sangre; hay valores perdidos |
| `t` | años desde la fecha de la encuesta hasta la muerte o hasta el 31-12-2023 | tiempo de seguimiento |
| `muerto` | 1 si hay fecha de defunción | evento |

> **Decisión que debes poder defender:** definir «fumador pasivo» como cualquier exposición > 0 horas es amplio.
> Otro grupo podría usar un umbral (p. ej. ≥ 1 h en el hogar). ¿Cambiaría el resultado?
"""))
    c.append(code("""
lab_ta3 = df.ta3.map(etiq_val["ta3"]).astype(str)
d = pd.DataFrame({
    "w": df.Fexp_F1p_Corr, "estrato": df.Estrato, "cong": df.Conglomerado,
    "edad": df.Edad, "mujer": (df.Sexo == 2).astype(int), "zona": df.Zona,
    "cig_dia": df.ta4, "edad_inicio": df.ta6, "imc": df.IMC, "colest": df.Colesterol_Total,
})
d["estado"] = np.select(
    [lab_ta3.str.contains("NUNCA"), lab_ta3.str.contains("HE DEJADO"),
     lab_ta3.str.contains("OCASIONALMENTE"), lab_ta3.str.contains("UNO O MÁS")],
    ["nunca", "ex", "ocasional", "diario"], default="")
d.loc[d.estado == "", "estado"] = np.nan
d["fuma_actual"] = d.estado.isin(["diario", "ocasional"]).astype(float).where(d.estado.notna())

# Exposición pasiva: horas de humo ajeno (la mayor entre día de semana y fin de semana) en 3 ambientes
d["h_casa"] = np.maximum(df.ta11_1, df.ta11_2)
d["h_trab"] = np.maximum(df.ta12_1, df.ta12_2)
d["h_otro"] = np.maximum(df.ta13_1, df.ta13_2)
d["h_exp"]  = d[["h_casa", "h_trab", "h_otro"]].sum(axis=1)
d["exp_casa"], d["exp_trab"], d["exp_otro"] = (d.h_casa > 0).astype(int), (d.h_trab > 0).astype(int), (d.h_otro > 0).astype(int)
d["exp_any"]  = (d.h_exp > 0).astype(int)

# Supervivencia
entrada = pd.to_datetime(df.Fechaini_F1)
fdef = pd.to_datetime(df.FECHA_DEF, errors="coerce")
d["muerto"] = df.ANO_DEF.notna().astype(int)
d["t"] = ((fdef.where(d.muerto == 1, pd.Timestamp("2023-12-31")) - entrada).dt.days / 365.25).clip(lower=1/365.25)

d["gedad"] = pd.cut(d.edad, [14, 24, 44, 64, 120], labels=["15-24", "25-44", "45-64", "65+"])
d["sexo"] = d.mujer.map({0: "Hombres", 1: "Mujeres"})
d.estado.value_counts(dropna=False)
"""))

    c.append(md("""
## 3. Caja de herramientas (ya escrita)

Cuatro funciones que usarás varias veces. No necesitas modificarlas, pero **sí entender qué hacen**.

- `prevalencia(y, mask)` → porcentaje ponderado con IC 95% que **respeta el diseño muestral** (estratos + conglomerados, linealización de Taylor).
  Un promedio simple de la columna daría un resultado incorrecto, porque la muestra no es un reparto igual de la población.
- `cox(columnas, datos)` → razón de riesgo (HR) de morir con el modelo de Cox, ponderado y con errores estándar agrupados por conglomerado.
- `resumen(x, mask)` → media, mediana y cuartiles **ponderados** de una variable numérica (para describir distribuciones).
- `corr_pond(datos, columnas)` → matriz de correlaciones de Spearman **ponderadas** (usa pares completos: cada par de variables con los casos que tienen ambos datos).

Estas dos últimas entregan estimaciones puntuales, sin intervalo de confianza: sirven para **describir**, no para inferir.
"""))
    c.append(code("""
def prevalencia(y, mask=None):
    \"\"\"% ponderado e IC95% con diseño (estrato + conglomerado). y: serie 0/1 (NaN = sin dato).\"\"\"
    y = y.astype(float)
    ok = y.notna() & (d.w > 0)
    if mask is not None: ok &= mask
    x, w, h, cl = y[ok], d.w[ok], d.estrato[ok], d.cong[ok]
    p = (w * x).sum() / w.sum()
    u = (w * (x - p) / w.sum()).groupby([h, cl]).sum()          # residuos por conglomerado
    g = u.groupby(level=0); nh = g.count(); mu = g.transform("mean")
    var = (((u - mu) ** 2).groupby(level=0).sum() * (nh / (nh - 1).replace(0, np.nan))).dropna().sum()
    se = np.sqrt(var); gl = nh.sum() - len(nh); t = stats.t.ppf(.975, gl)
    return pd.Series({"%": round(100*p, 1), "IC_inf": round(100*max(0, p - t*se), 1), "IC_sup": round(100*min(1, p + t*se), 1), "n": int(ok.sum())}, dtype=object)

def cox(columnas, datos=None, evento="muerto"):
    \"\"\"HR de morir. columnas: variables explicativas (numéricas). Ponderado y agrupado por conglomerado.\"\"\"
    datos = d if datos is None else datos
    x = datos[["t", evento, "w", "cong"] + columnas].dropna(); x = x[x.w > 0]
    m = CoxPHFitter().fit(x, "t", evento, weights_col="w", cluster_col="cong")
    r = m.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%", "p"]].round(3)
    r.columns = ["HR", "IC_inf", "IC_sup", "p"]
    print(f"n = {len(x)} | muertes = {int(x[evento].sum())}")
    return r

def cuantil_pond(x, q=0.5, mask=None):
    \"\"\"Cuantil ponderado de x (q=0.5 es la mediana).\"\"\"
    ok = x.notna() & (d.w > 0)
    if mask is not None: ok &= mask
    xs, ws = x[ok].values, d.w[ok].values
    o = np.argsort(xs); acum = np.cumsum(ws[o]) / ws.sum()
    return xs[o][np.searchsorted(acum, q)]

def resumen(x, mask=None):
    \"\"\"n, media, mediana y cuartiles ponderados.\"\"\"
    ok = x.notna() & (d.w > 0)
    if mask is not None: ok &= mask
    r = {"n": int(ok.sum()), "media": round(np.average(x[ok], weights=d.w[ok]), 1)}
    for nombre, q in [("p25", .25), ("mediana", .5), ("p75", .75)]:
        r[nombre] = round(float(cuantil_pond(x, q, mask)), 1)
    return pd.Series(r, dtype=object)

def corr_pond(datos, columnas):
    \"\"\"Matriz de correlación de Spearman ponderada (pares completos).\"\"\"
    def rango(x, w):                               # rango ponderado entre 0 y 1
        g = pd.DataFrame({"x": x, "w": w}).groupby("x").w.sum().sort_index()
        return x.map((g.cumsum() - g / 2) / g.sum())
    R = pd.DataFrame(np.nan, index=columnas, columns=columnas)
    for a in columnas:
        for b in columnas:
            ok = datos[a].notna() & datos[b].notna() & (datos.w > 0)
            w = datos.w[ok]; ra, rb = rango(datos[a][ok], w), rango(datos[b][ok], w)
            da, db = ra - np.average(ra, weights=w), rb - np.average(rb, weights=w)
            R.loc[a, b] = (w * da * db).sum() / np.sqrt((w * da**2).sum() * (w * db**2).sum())
    return R

prevalencia(d.fuma_actual)      # prueba: ¿cuántos fuman?
"""))

    c.append(md("""
## 4. Parte A — Mirar cómo se distribuyen los datos

Antes de calcular porcentajes o riesgos hay que **mirar las variables**: su forma (histograma), su centro (media o mediana) y su dispersión.
Dos ideas para este bloque:

- **Ponderar cambia la imagen.** La muestra no es una foto de Chile: sobrerrepresenta a algunos grupos. Un histograma con `weights=` dibuja la población, no a quienes respondieron.
- **Media y mediana cuentan historias distintas** cuando la distribución es asimétrica (pocos valores muy altos tiran de la media).
"""))
    ejercicio(
        "edad", "¿Quién respondió y a quién representa? (histograma ponderado)",
        "Dibuja el histograma de la **edad** de dos formas: sin ponderar (las personas que respondieron) y ponderado (la población de Chile que representan). ¿Se parecen? Compara las medianas.",
        "`plt.hist(d.edad, bins=range(15, 100, 5))` y, para el segundo, agrega `weights=d.w`. La mediana ponderada: `cuantil_pond(d.edad)`.",
        """
bins = range(15, 100, 5)
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
ax[0].hist(d.edad, bins=bins, color="#999999", edgecolor="white")
ax[0].set(title=f"Muestra (sin ponderar)\\nmediana {d.edad.median():.0f} años", xlabel="Edad (años)", ylabel="Personas encuestadas")
ax[1].hist(d.edad, bins=bins, weights=d.w / 1e6, color="#2a6f97", edgecolor="white")
ax[1].set(title=f"Población representada (ponderada)\\nmediana {cuantil_pond(d.edad):.0f} años", xlabel="Edad (años)", ylabel="Millones de personas")
plt.tight_layout(); plt.show()
""")
    ejercicio(
        "cuanto", "¿Cuánto y desde cuándo se fuma? (distribuciones asimétricas)",
        "Entre los fumadores actuales, dibuja el histograma de **cigarrillos al día** (`cig_dia`) y, entre quienes alguna vez fumaron, el de la **edad de inicio** (`edad_inicio`). Calcula media y mediana ponderadas de cada una. ¿Por qué la media de cigarrillos supera a la mediana? ¿Qué cantidades se repiten más y por qué?",
        "`resumen(d.cig_dia, d.fuma_actual == 1)` da media y mediana ponderadas. En el gráfico marca ambas con `plt.axvline`.",
        """
fuman = d.fuma_actual == 1
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
for a, col, ok, titulo, bins in [
        (ax[0], "cig_dia", fuman, "Cigarrillos al día (fumadores actuales)", np.arange(0.5, 40.6)),
        (ax[1], "edad_inicio", d.edad_inicio.notna(), "Edad a la que empezó a fumar", np.arange(4.5, 40.6))]:
    x = d[col][ok & d[col].notna()]
    r = resumen(d[col], ok)
    a.hist(x.clip(upper=40), bins=bins, weights=d.w[x.index] / 1e3, color="#2a6f97", edgecolor="white")
    a.axvline(r["mediana"], color="#d1495b", lw=2, label=f"mediana {r['mediana']:.0f}")
    a.axvline(r["media"], color="black", lw=1.5, ls="--", label=f"media {r['media']:.1f}")
    a.set(title=titulo, xlabel="(40 = 40 o más)", ylabel="Miles de personas"); a.legend()
    print(col, r.to_dict())
plt.tight_layout(); plt.show()
x = d.cig_dia[fuman].dropna()
print(f"Fumadores que declaran 5, 10 o 20 cigarrillos: {x.isin([5, 10, 20]).mean():.0%} (n = {len(x)})")
""")

    c.append(md("""
## 5. Parte B — Prevalencia
"""))
    ejercicio(
        "prev", "Prevalencia de fumadores",
        "Calcula la prevalencia de **fumador actual** en toda la población y luego **por sexo y por grupo de edad**. ¿Quién fuma más?",
        "`prevalencia(d.fuma_actual)` da el total. Para un subgrupo pasa una máscara: `prevalencia(d.fuma_actual, d.sexo == 'Hombres')`.",
        """
print("Total:\\n", prevalencia(d.fuma_actual).to_dict())
for g in ["sexo", "gedad"]:
    for k in sorted(d[g].dropna().unique()):
        print(g, k, prevalencia(d.fuma_actual, d[g] == k).to_dict())
""")
    ejercicio(
        "pasivo", "Fumador pasivo",
        "Define **fumador pasivo** como una persona que **no fuma actualmente** (nunca o ex) y está **expuesta al humo ajeno** (`exp_any == 1`). Calcula su prevalencia total y en los tres ambientes (casa, trabajo/estudio, otros).",
        "Usa una máscara: `d.estado.isin(['nunca','ex'])`.",
        """
no_fuma = d.estado.isin(["nunca", "ex"])
print("Pasivo (no fuma + expuesto):", prevalencia(d.exp_any, no_fuma).to_dict())
for amb in ["exp_casa", "exp_trab", "exp_otro"]:
    print(amb, prevalencia(d[amb], no_fuma).to_dict())
""")
    ejercicio(
        "humo", "¿Cuántas horas de humo ajeno? (y cuánto pesa la definición)",
        "Entre quienes **no fuman**, dibuja el histograma de horas diarias de exposición (`h_exp`). a) ¿Qué porcentaje está en cero? b) Entre los expuestos, ¿cuál es la mediana de horas? c) Recalcula la prevalencia de fumador pasivo exigiendo **≥ 2** y **≥ 5** horas diarias en vez de ≥ 1. ¿Cuánto depende el resultado de la definición?",
        "Usa `prevalencia((d.h_exp >= k).astype(float), no_fuma)` con `k = 1, 2, 5`. Para el histograma agrupa las colas con `.clip(upper=12)`.",
        """
no_fuma = d.estado.isin(["nunca", "ex"])
expuesto = no_fuma & (d.h_exp > 0)
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
ax[0].hist(d.h_exp[no_fuma].clip(upper=12), bins=np.arange(-0.5, 12.6), weights=d.w[no_fuma] / 1e6, color="#2a6f97", edgecolor="white")
ax[0].set(title="Todos los que no fuman", xlabel="Horas diarias de humo ajeno (12 = 12 o más)", ylabel="Millones de personas")
ax[1].hist(d.h_exp[expuesto].clip(upper=12), bins=np.arange(0.5, 12.6), weights=d.w[expuesto] / 1e6, color="#d1495b", edgecolor="white")
ax[1].set(title="Solo los expuestos (≥ 1 h)", xlabel="Horas diarias de humo ajeno (12 = 12 o más)", ylabel="Millones de personas")
plt.tight_layout(); plt.show()
print(f"Sin ninguna exposición: {100 - prevalencia(d.exp_any, no_fuma)['%']:.1f}%")
print("Entre expuestos:", resumen(d.h_exp, expuesto).to_dict())
for k in [1, 2, 5]:
    print(f"Pasivo con ≥ {k} h/día:", prevalencia((d.h_exp >= k).astype(float), no_fuma).to_dict())
""")

    c.append(md("""
## 6. Parte C — Antes de modelar: ¿se parecen los grupos?

Si dos grupos difieren en **otras** características, comparar sus resultados sin cuidado lleva a conclusiones falsas. Aquí miramos dos cosas:
las distribuciones de edad de fumadores y no fumadores, y qué variables se mueven juntas (**correlación**).
Recuerda: una correlación mide cuánto *acompañan* dos variables entre sí (de −1 a +1); **no dice que una cause la otra**.
"""))
    ejercicio(
        "grupos", "¿Tienen la misma edad fumadores y no fumadores?",
        "Dibuja, superpuestos, los histogramas de edad de fumadores actuales y de no fumadores (ponderados y normalizados para poder compararlos). Calcula la edad media de cada grupo. **Antes** de correr ningún modelo: si los fumadores son más jóvenes, ¿qué esperas que pase con su riesgo de morir *sin ajustar*?",
        "`plt.hist(s.edad, bins=range(15, 100, 5), weights=s.w, density=True, alpha=.55)` para cada grupo.",
        """
z = d[d.fuma_actual.notna() & (d.w > 0)]
fig, ax = plt.subplots(figsize=(7, 3.8))
for v, lab, col in [(0, "No fuma", "#2a6f97"), (1, "Fuma actualmente", "#d1495b")]:
    s = z[z.fuma_actual == v]
    ax.hist(s.edad, bins=range(15, 100, 5), weights=s.w, density=True, alpha=.55, color=col, label=lab)
ax.set(xlabel="Edad (años)", ylabel="Densidad (ponderada)"); ax.legend(); plt.show()
nombre = {0.0: "No fuma", 1.0: "Fuma actualmente"}
print("Edad media sin ponderar:", {nombre[v]: round(float(s.edad.mean()), 1) for v, s in z.groupby("fuma_actual")})
print("Edad media ponderada:   ", {nombre[v]: round(float(np.average(s.edad, weights=s.w)), 1) for v, s in z.groupby("fuma_actual")})
""")
    ejercicio(
        "corr", "¿Qué variables se mueven juntas? (correlaciones)",
        "Calcula la matriz de correlaciones (Spearman ponderada) entre `edad`, `edad_inicio`, `cig_dia`, `h_casa`, `h_trab`, `h_otro`, `imc` y `colest`, y dibújala como mapa de calor. a) ¿Qué variable se correlaciona con más de las otras? b) ¿Qué ambientes de exposición van juntos? c) ¿Qué te dice esto sobre ajustar por edad? d) ¿Por qué una correlación de 0,28 *no* demuestra que la edad suba el colesterol por sí sola?",
        "`R = corr_pond(d, columnas)`; para el gráfico, `plt.imshow(R, cmap='RdBu_r', vmin=-1, vmax=1)`. Los valores cerca de 0 significan que no se acompañan; ojo con cuántos casos tiene cada par.",
        """
cols = ["edad", "edad_inicio", "cig_dia", "h_casa", "h_trab", "h_otro", "imc", "colest"]
R = corr_pond(d, cols)
fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.4), gridspec_kw={"width_ratios": [1.25, 1]})
im = ax[0].imshow(R, cmap="RdBu_r", vmin=-1, vmax=1)
ax[0].set_xticks(range(len(cols)), cols, rotation=45, ha="right"); ax[0].set_yticks(range(len(cols)), cols)
for i in range(len(cols)):
    for j in range(len(cols)):
        ax[0].text(j, i, f"{R.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
plt.colorbar(im, ax=ax[0], shrink=.8)
ax[1].scatter(d.edad, d.colest, s=6, alpha=.25, color="#2a6f97")
ax[1].set(xlabel="Edad (años)", ylabel="Colesterol total (mg/dL)", title=f"Edad vs colesterol (ρ = {R.loc['edad', 'colest']:.2f})")
plt.tight_layout(); plt.show()
R.round(2)
""")
    c.append(md("""
## 7. Parte D — ¿Fumar se asocia con morir antes?
"""))
    ejercicio(
        "enganoso", "El resultado engañoso",
        f"Retoma lo que viste en el ejercicio {N['grupos']}. Compara el **porcentaje de fallecidos** entre fumadores actuales y no fumadores (sin ajustar) y luego estima el HR **sin ajustar** con `cox(['fuma_actual'])`. ¿Fumar parece proteger? ¿Qué falta?",
        "Compara también la **edad media** de ambos grupos: `d.groupby('fuma_actual').edad.mean()`.",
        """
print(d.groupby("fuma_actual").muerto.mean().mul(100).round(1))
print(d.groupby("fuma_actual").edad.mean().round(1))
cox(["fuma_actual"])
""")
    ejercicio(
        "ajuste", "Ajustar por edad y sexo",
        "Repite el modelo agregando `edad` y `mujer`. ¿Qué pasa con el HR de `fuma_actual`? Explica **por qué** cambia.",
        "`cox(['fuma_actual','edad','mujer'])`.",
        """
cox(["fuma_actual", "edad", "mujer"])
""")
    ejercicio(
        "cuatro", "Fumadores activos, ex fumadores y pasivos",
        "Arma cuatro grupos: **(ref.) nunca fumó y sin exposición**, **pasivo** (nunca fumó y expuesto), **ex fumador** y **fumador actual**. Estima el HR de cada uno ajustando por edad y sexo. ¿Hay evidencia de riesgo en los pasivos? Mira el **número de muertes** de ese grupo antes de concluir.",
        "Crea tres columnas 0/1 (`pasivo`, `ex`, `actual`) y pásalas a `cox(...)` junto a `edad` y `mujer`. Usa solo las filas con `estado` no nulo.",
        """
g = d[d.estado.notna()].copy()
g["pasivo"] = ((g.estado == "nunca") & (g.exp_any == 1)).astype(float)
g["ex"]     = (g.estado == "ex").astype(float)
g["actual"] = g.estado.isin(["diario", "ocasional"]).astype(float)
print(g.assign(grupo=np.select([g.actual == 1, g.ex == 1, g.pasivo == 1], ["actual", "ex", "pasivo"], "ref (nunca, sin exp.)"))
        .groupby("grupo").muerto.agg(["count", "sum"]))
cox(["pasivo", "ex", "actual", "edad", "mujer"], g)
""")
    ejercicio(
        "sens", "¿Y si fueron los enfermos quienes dejaron de fumar? (análisis de sensibilidad)",
        f"Un posible sesgo es la **causalidad inversa**: personas ya enfermas pueden haber dejado de fumar, o morir pronto por una enfermedad previa. Repite el modelo del ejercicio {N['ajuste']} **excluyendo a quienes murieron en los primeros 2 años**. ¿Cambia la conclusión?",
        "Filtra con `~((d.muerto == 1) & (d.t < 2))`.",
        """
cox(["fuma_actual", "edad", "mujer"], d[~((d.muerto == 1) & (d.t < 2))])
""")

    c.append(md(f"""
## 8. Parte E — Curvas de supervivencia

Las curvas muestran la proporción de personas vivas a lo largo del tiempo. Comparar **dentro de un grupo de edad** evita la confusión que viste en el ejercicio {N['enganoso']}.
"""))
    ejercicio(
        "km", "Curva por grupo de edad",
        "Dibuja la supervivencia de fumadores y no fumadores solo entre personas de **40 a 59 años**. ¿Se separan las curvas?",
        "Usa `KaplanMeierFitter().fit(tiempo, evento, weights=peso)` y `.plot_survival_function()`.",
        """
z = d[(d.edad.between(40, 59)) & d.fuma_actual.notna() & (d.w > 0)]
fig, ax = plt.subplots(figsize=(6, 4))
for v, lab in [(0, "No fuma"), (1, "Fuma actual")]:
    s = z[z.fuma_actual == v]
    KaplanMeierFitter().fit(s.t, s.muerto, weights=s.w, label=f"{lab} (n={len(s)})").plot_survival_function(ax=ax, ci_show=False)
ax.set_ylim(0.8, 1.01); ax.set_xlabel("Años desde la encuesta"); ax.set_ylabel("Proporción viva"); ax.grid(alpha=.3)
plt.show()
""")

    c.append(md("""
## 9. De los números a un artículo

### 9.1 Cómo reportar (lista STROBE, versión corta)
- **Diseño y población:** estudio de cohorte con seguimiento por registros, a partir de una encuesta nacional probabilística.
- **Exposición y resultado:** definiciones exactas (ver sección 2) y fecha de cierre del seguimiento (31-12-2023).
- **Estadística:** ponderación, diseño muestral, modelo de Cox, variables de ajuste y análisis de sensibilidad.
- **Resultados:** prevalencias con IC 95%, HR ajustados con IC 95%, **número de muertes por grupo**.
- **Limitaciones:** ver abajo.

### 9.2 Limitaciones que debes declarar
1. **Tabaco medido una sola vez** (al inicio): quien cambió de hábito después queda mal clasificado.
2. **Causalidad inversa y sesgo de supervivencia:** ver el análisis de sensibilidad y las curvas de adultos mayores.
3. **Pocas muertes** en algunos grupos (p. ej. fumadores pasivos) ⇒ sin poder para detectar efectos moderados. *Ausencia de evidencia no es evidencia de ausencia.*
4. **Exposición pasiva autorreportada** y con definición propia, sin biomarcador (cotinina).
5. **Variables de confusión no medidas** (p. ej. nivel socioeconómico, alcohol, comorbilidad).
6. **Causas de muerte:** el registro trae la causa básica en CIE-10; las categorías por causa tienen muy pocos casos.

### 9.3 Escribe tu párrafo de resultados
"""))
    ejercicio(
        "redactar", "Redacta",
        "Con tus números, completa el párrafo (3–5 líneas) como lo escribirías en un *abstract*. Usa tus resultados, no los de un colega.",
        "Incluye: prevalencia (IC 95%), HR ajustado de fumadores activos (IC 95%), qué encontraste en pasivos **y por qué es prudente no concluir**.",
        """
# (Ejemplo de redacción — usa los números de tus resultados)
print(\"\"\"En la ENS 2016-17 (N = 6.233), la prevalencia de fumadores actuales fue de 32,5% (IC 95% 30,4-34,6) y la de fumadores pasivos
entre quienes no fuman de 25,9% (IC 95% 23,1-28,6). Tras 7 años de seguimiento mediano (539 muertes), los fumadores actuales tuvieron un
riesgo de morir 2,0 veces mayor que quienes nunca fumaron y no estaban expuestos (HR 2,04; IC 95% 1,43-2,90), ajustado por edad y sexo.
No encontramos asociación en fumadores pasivos (HR 0,63; IC 95% 0,35-1,16), pero este grupo tuvo solo 24 muertes, por lo que el estudio carece
de poder para descartar un efecto.\"\"\")
""", stub="# Escribe aquí tu párrafo (puedes usar print(\"\"\"...\"\"\"))\n")

    c.append(md("""
## 10. Preguntas para discutir en grupo
1. ¿Por qué el HR sin ajustar (< 1) y el ajustado (> 1) apuntan en direcciones opuestas? ¿Qué otras variables podrían confundir?
2. ¿Qué cambiaría si definimos fumador pasivo con otro umbral? ¿Cómo lo probarías?
3. ¿Qué otras preguntas podrías responder con esta base? (por ejemplo: hipertensión, diabetes, obesidad, o la misma pregunta en la ENS 2003 y 2009-10).
4. ¿Qué haría falta para publicar? (comité, protocolo, preregistro del análisis, revisión de limitaciones).
5. La edad se correlaciona con el colesterol, el IMC y la exposición al humo. ¿Qué otras variables deberías medir y ajustar antes de interpretar un HR como efecto del tabaco?

---
**Fuentes:** Ministerio de Salud de Chile, Departamento de Epidemiología. *Encuesta Nacional de Salud 2016-2017*, base de datos y manual de uso. https://epi.minsal.cl/bases-de-datos/
"""))

    nb = nbf.v4.new_notebook(); nb.cells = c
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    return nb

if __name__ == "__main__":
    for fac, name in [(False, "taller_tabaco_PARTICIPANTES.ipynb"), (True, "taller_tabaco_FACILITADOR.ipynb")]:
        nbf.write(build(fac), OUT + name); print("escrito", name)
