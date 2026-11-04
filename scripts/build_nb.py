"""Construye los tres cuadernos del taller (participantes, facilitador y versión resuelta neutra) desde una sola fuente."""
import sys, nbformat as nbf

OUT = "/Users/simonvidal/Desktop/workshop medi/taller/"

def md(t): return nbf.v4.new_markdown_cell(t.strip())
def code(t): return nbf.v4.new_code_cell(t.strip())

def build(facilitador: bool, tipo=None):
    c = []
    claves = ["pesos", "prev", "pasivo", "grupos", "corr", "enganoso", "ajuste", "cuatro", "km"]
    N = {k: i + 1 for i, k in enumerate(claves)}   # numeración única; las referencias cruzadas la usan

    def ejercicio(clave, titulo, enunciado, pista, solucion, stub="# TU CÓDIGO AQUÍ\n"):
        c.append(md(f"### ✏️ Ejercicio {N[clave]} — {titulo}\n\n{enunciado}\n\n> **Pista:** {pista}"))
        c.append(code(solucion if facilitador else stub))

    tipo = tipo or ("FACILITADOR (con soluciones)" if facilitador else "PARTICIPANTES")
    c.append(md(f"""
# Taller: investigar con bases de datos existentes
## Tabaco (activo y pasivo) y riesgo de muerte — Encuesta Nacional de Salud 2016-17

**Versión {tipo}**

**Pregunta de investigación**
1. ¿Cuál es la prevalencia de fumadores y de fumadores pasivos en Chile?
2. ¿Cuál es la asociación entre la exposición al tabaco y el riesgo de muerte?

**Qué vamos a hacer:** ir de la pregunta al resultado con datos reales:
`pregunta → datos → prevalencias → asociación con la muerte → ¿podemos creer el resultado?`.

**Sobre el uso de los datos.** Las bases de la ENS son públicas, anonimizadas y de descarga libre en
[epi.minsal.cl/bases-de-datos](https://epi.minsal.cl/bases-de-datos/). Las condiciones de uso del Minsal piden
**usarlas solo para investigación, citar la fuente y enviar copia de las publicaciones al Minsal**
([condiciones](https://epi.minsal.cl/condiciones-de-uso/)).
"""))

    # ------------------------------------------------------------------ 0. Entorno
    c.append(md("## 0. Preparar el entorno"))
    c.append(code("""
# Solo hace falta en Google Colab o si faltan librerías (puedes ignorar si ya las tienes)
%pip install -q pandas numpy scipy pyreadstat lifelines matplotlib
"""))
    c.append(code("""
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
from scipy import stats
from lifelines import CoxPHFitter, KaplanMeierFitter
import matplotlib.pyplot as plt

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

# Ruta al archivo. Cámbiala si lo guardaste en otro lugar.
RUTA = Path("datos/Base de datos Encuesta Nacional de Salud 2016-2017(ENS)+DEF2023.sav")
RUTA.exists()   # debe mostrar True
"""))

    # ------------------------------------------------------------------ 1. Conocer la base
    c.append(md("""
## 1. Conocer la base (ejemplo resuelto)

La base **ENS 2016-17 + defunciones 2023** une la encuesta con los registros de muerte hasta 2023.
**Cada fila es una persona.** Antes de analizar, hay que entender una idea: el **peso**.

### ¿Qué es el peso y para qué lo necesitamos?

La encuesta no preguntó a todos los chilenos: entrevistó a 6.233 personas elegidas por sorteo.
Lo que queremos decir al final es algo sobre **Chile**, no sobre esas 6.233 personas. Pero el sorteo no dio a todos la misma
probabilidad de salir, y algunos grupos quedaron sobrerrepresentados (verás un caso en el ejercicio 1).

Para corregirlo, cada persona trae un **peso**: **a cuántas personas de Chile representa**.
Si alguien tiene peso 2.000, sus respuestas valen por 2.000 personas. Al calcular un porcentaje, cada persona cuenta según su peso:
eso es una **prevalencia ponderada**. Sin pesos, calcularíamos el porcentaje de la *muestra* y no el de *Chile*.

El sorteo fue además **por etapas** (se eligieron zonas geográficas llamadas *conglomerados*, dentro de grupos llamados *estratos*).
Las personas de un mismo conglomerado se parecen entre sí, así que hay **menos información** que la que sugiere el número de encuestados.
Por eso el intervalo de confianza debe calcularse usando ese diseño. Las funciones del taller ya lo hacen; tú solo debes saber que existe.

El [manual de uso](https://epi.minsal.cl/wp-content/uploads/2019/02/Manual_de_Uso_de_la_base_de_datos_de_la_Encuesta_Nacional_de_Salud_2016_F1_F2_F4_EX1_EX2_14022019.pdf)
indica que, para las preguntas del **cuestionario F1** (donde está el tabaco), el peso es la columna `Fexp_F1p_Corr`.
"""))
    c.append(code("""
# Leer el archivo: base_original son los datos; meta guarda las descripciones de cada columna
base_original, meta = pyreadstat.read_sav(RUTA)
descripcion_variable = meta.column_names_to_labels    # nombre de columna -> descripción
etiquetas_valores = meta.variable_value_labels        # nombre de columna -> {código: etiqueta}

# Resumen de lo que contiene
peso_original = base_original.Fexp_F1p_Corr
print("Personas encuestadas:      ", len(base_original))
print("Personas que representan:  ", f"{peso_original.sum():,.0f}".replace(",", "."))
print("Peso de cada persona: mínimo", round(peso_original.min()), "| máximo", round(peso_original.max()))
print("Estratos:", base_original.Estrato.nunique(),
      "| Conglomerados:", base_original.groupby("Estrato").Conglomerado.nunique().sum())
print("Fallecidos hasta 2023 (tienen fecha de defunción, FECHA_DEF):", base_original.ANO_DEF.notna().sum())
"""))
    c.append(code("""
# Variables de tabaco del cuestionario (sus nombres empiezan con 'ta')
variables_tabaco = [nombre for nombre in base_original.columns
                    if nombre.startswith("ta") and nombre[2:3].isdigit()]

for nombre in variables_tabaco[:22]:
    print(f"{nombre:8} {descripcion_variable[nombre][:95]}")
"""))

    # ------------------------------------------------------------------ 2. Variables
    c.append(md("""
## 2. Construir las variables de análisis (ya hecho para ti)

Cada variable que usaremos sale de una o más preguntas de la encuesta. Lee las decisiones:

| Variable | Definición | De dónde sale |
|---|---|---|
| `peso`, `estrato`, `conglomerado` | peso de cada persona y diseño de la muestra | `Fexp_F1p_Corr`, `Estrato`, `Conglomerado` |
| `edad`, `mujer`, `sexo`, `area`, `grupo_edad` | edad en años, 1 si es mujer, sexo, zona urbana/rural y tramo de edad | datos de la persona |
| `estado_fumador` | nunca / ex / ocasional / diario | pregunta `ta3` («¿actualmente fuma cigarrillos?») |
| `fuma_actual` | 1 si fuma a diario u ocasionalmente, 0 si no | exposición principal |
| `horas_casa`, `horas_trabajo`, `horas_otros`, `horas_humo_total` | horas diarias de humo ajeno en casa, trabajo/estudio y otros ambientes (la mayor entre día de semana y fin de semana); el total es la suma | preguntas `ta11`–`ta13` |
| `expuesto_humo` | 1 si `horas_humo_total` > 0 (≥ 1 hora/día) | **nuestra** regla para «expuesto al humo ajeno» |
| `cigarrillos_dia` | cigarrillos al día (solo fumadores actuales) | `ta4` |
| `imc`, `colesterol` | índice de masa corporal y colesterol total | examen físico y de sangre; hay valores perdidos |
| `anios_seguimiento` | años desde la fecha de la encuesta hasta la muerte o hasta el 31-12-2023 | tiempo de seguimiento |
| `fallecido` | 1 si hay fecha de defunción | evento |

### ¿Qué significa que `expuesto_humo` sea «una definición nuestra»?

La encuesta pregunta **cuántas horas** la persona estuvo cerca de humo de cigarrillo ajeno. Pero **no existe una variable ya hecha que diga «esta persona es fumadora pasiva»**,
ni una regla única sobre desde cuántas horas alguien merece ese nombre. Alguien tiene que decidirlo, y aquí decidimos que basta **al menos 1 hora al día**.
Otro equipo podría exigir 2 o 5 horas, y el porcentaje de fumadores pasivos cambiaría (lo verás en el ejercicio 3).
Por eso en un trabajo siempre hay que **escribir la definición exacta** que se usó.
"""))
    c.append(code("""
# --- Tabla de trabajo: una fila por persona, con nombres fáciles de leer ---
datos = pd.DataFrame({
    "peso": base_original.Fexp_F1p_Corr,
    "estrato": base_original.Estrato,
    "conglomerado": base_original.Conglomerado,
    "edad": base_original.Edad,
    "mujer": (base_original.Sexo == 2).astype(int),     # 1 = mujer, 0 = hombre
    "zona": base_original.Zona,
    "cigarrillos_dia": base_original.ta4,
    "imc": base_original.IMC,
    "colesterol": base_original.Colesterol_Total,
})

# --- Estado de tabaquismo, a partir del texto de la respuesta a ta3 ---
respuesta_ta3 = base_original.ta3.map(etiquetas_valores["ta3"]).astype(str)
datos["estado_fumador"] = np.select(
    [respuesta_ta3.str.contains("NUNCA"),
     respuesta_ta3.str.contains("HE DEJADO"),
     respuesta_ta3.str.contains("OCASIONALMENTE"),
     respuesta_ta3.str.contains("UNO O MÁS")],
    ["nunca", "ex", "ocasional", "diario"],
    default="")
datos.loc[datos.estado_fumador == "", "estado_fumador"] = np.nan    # sin dato

# fuma_actual: 1 si fuma a diario u ocasionalmente, 0 si no, vacío si no hay dato
datos["fuma_actual"] = (datos.estado_fumador.isin(["diario", "ocasional"])
                        .astype(float)
                        .where(datos.estado_fumador.notna()))

# --- Horas diarias de humo ajeno (se toma la mayor entre día de semana y fin de semana) ---
datos["horas_casa"] = np.maximum(base_original.ta11_1, base_original.ta11_2)
datos["horas_trabajo"] = np.maximum(base_original.ta12_1, base_original.ta12_2)
datos["horas_otros"] = np.maximum(base_original.ta13_1, base_original.ta13_2)
datos["horas_humo_total"] = datos[["horas_casa", "horas_trabajo", "horas_otros"]].sum(axis=1)

# Expuesto = al menos 1 hora al día (nuestra definición)
datos["expuesto_casa"] = (datos.horas_casa > 0).astype(int)
datos["expuesto_trabajo"] = (datos.horas_trabajo > 0).astype(int)
datos["expuesto_otros"] = (datos.horas_otros > 0).astype(int)
datos["expuesto_humo"] = (datos.horas_humo_total > 0).astype(int)

# --- Seguimiento: años desde la encuesta hasta la muerte (o hasta el 31-12-2023) ---
fecha_encuesta = pd.to_datetime(base_original.Fechaini_F1)
fecha_muerte = pd.to_datetime(base_original.FECHA_DEF, errors="coerce")
fecha_cierre = pd.Timestamp("2023-12-31")

datos["fallecido"] = base_original.ANO_DEF.notna().astype(int)
fecha_final = fecha_muerte.where(datos.fallecido == 1, fecha_cierre)
anios = (fecha_final - fecha_encuesta).dt.days / 365.25
datos["anios_seguimiento"] = anios.clip(lower=1 / 365.25)     # evita tiempos de 0

# --- Etiquetas para tablas y gráficos ---
datos["grupo_edad"] = pd.cut(datos.edad, [14, 24, 44, 64, 120], labels=["15-24", "25-44", "45-64", "65+"])
datos["sexo"] = datos.mujer.map({0: "Hombres", 1: "Mujeres"})
datos["area"] = datos.zona.map({1.0: "Urbana", 2.0: "Rural"})

# Revisión: ¿cuántas personas hay en cada estado?
datos.estado_fumador.value_counts(dropna=False)
"""))

    # ------------------------------------------------------------------ 3. Herramientas
    c.append(md("""
## 3. Caja de herramientas (ya escrita)

Funciones que usarás varias veces. No necesitas modificarlas, pero **sí entender qué hacen**.

- `prevalencia(indicador, filtro)` → porcentaje ponderado con IC 95% que **respeta el diseño muestral** (estratos + conglomerados).
  Un promedio simple de la columna daría el porcentaje de la muestra, no el de Chile.
- `cox(columnas, tabla)` → razón de riesgo (HR) de morir con el modelo de Cox, ponderado y con errores estándar agrupados por conglomerado (lo explicamos más adelante).
- `resumen_ponderado(x, filtro)` y `cuantil_ponderado(x)` → media, mediana y cuartiles **ponderados** de una variable numérica.
- `correlacion_ponderada(tabla, columnas)` → matriz de correlaciones de Spearman **ponderadas** (con pares completos: cada par usa los casos que tienen ambos datos).

`resumen_ponderado`, `cuantil_ponderado` y `correlacion_ponderada` entregan estimaciones puntuales, sin intervalo de confianza: sirven para **describir**, no para inferir.
"""))
    c.append(code('''
def prevalencia(indicador, filtro=None):
    """Porcentaje ponderado con IC 95%, respetando el diseño muestral (estratos y conglomerados).

    indicador: serie con 1 (tiene la característica), 0 (no la tiene) o NaN (sin dato).
    filtro: serie True/False para calcular solo en un subgrupo (opcional).
    """
    indicador = indicador.astype(float)

    # Casos que sí se pueden usar: con dato, con peso, y dentro del filtro
    casos_validos = indicador.notna() & (datos.peso > 0)
    if filtro is not None:
        casos_validos &= filtro

    valor = indicador[casos_validos]
    peso = datos.peso[casos_validos]
    estrato = datos.estrato[casos_validos]
    conglomerado = datos.conglomerado[casos_validos]

    # 1) Porcentaje ponderado: cada persona cuenta según su peso
    proporcion = (peso * valor).sum() / peso.sum()

    # 2) Error estándar que respeta el diseño: se suma el aporte de cada conglomerado
    #    y se mide cuánto varían esos aportes dentro de cada estrato
    aporte = (peso * (valor - proporcion) / peso.sum()).groupby([estrato, conglomerado]).sum()
    por_estrato = aporte.groupby(level=0)
    n_conglomerados = por_estrato.count()
    aporte_medio = por_estrato.transform("mean")
    suma_cuadrados = ((aporte - aporte_medio) ** 2).groupby(level=0).sum()
    factor_correccion = n_conglomerados / (n_conglomerados - 1).replace(0, np.nan)
    varianza = (suma_cuadrados * factor_correccion).dropna().sum()
    error_estandar = np.sqrt(varianza)

    # 3) Intervalo de confianza 95% (t de Student; gl = conglomerados - estratos)
    grados_libertad = n_conglomerados.sum() - len(n_conglomerados)
    t_critico = stats.t.ppf(0.975, grados_libertad)
    limite_inferior = max(0, proporcion - t_critico * error_estandar)
    limite_superior = min(1, proporcion + t_critico * error_estandar)

    return pd.Series({"%": round(100 * proporcion, 1),
                      "IC_inf": round(100 * limite_inferior, 1),
                      "IC_sup": round(100 * limite_superior, 1),
                      "n": int(casos_validos.sum())}, dtype=object)


def cox(columnas, tabla=None, evento="fallecido"):
    """Razón de riesgo (HR) de morir con el modelo de Cox, ponderado y agrupado por conglomerado.

    columnas: lista de variables explicativas (numéricas).
    tabla: datos a usar (por defecto, toda la tabla `datos`).
    """
    if tabla is None:
        tabla = datos
    columnas_del_modelo = ["anios_seguimiento", evento, "peso", "conglomerado"] + columnas
    casos = tabla[columnas_del_modelo].dropna()
    casos = casos[casos.peso > 0]

    modelo = CoxPHFitter().fit(casos, duration_col="anios_seguimiento", event_col=evento,
                               weights_col="peso", cluster_col="conglomerado")

    resultado = modelo.summary[["exp(coef)", "exp(coef) lower 95%", "exp(coef) upper 95%", "p"]].round(3)
    resultado.columns = ["HR", "IC_inf", "IC_sup", "p"]
    print(f"n = {len(casos)} | muertes = {int(casos[evento].sum())}")
    return resultado


def cuantil_ponderado(x, q=0.5, filtro=None):
    """Cuantil ponderado de x (q = 0.5 es la mediana)."""
    casos_validos = x.notna() & (datos.peso > 0)
    if filtro is not None:
        casos_validos &= filtro

    valores = x[casos_validos].values
    pesos = datos.peso[casos_validos].values

    orden = np.argsort(valores)
    peso_acumulado = np.cumsum(pesos[orden]) / pesos.sum()
    return valores[orden][np.searchsorted(peso_acumulado, q)]


def resumen_ponderado(x, filtro=None):
    """Número de casos, media y cuartiles ponderados."""
    casos_validos = x.notna() & (datos.peso > 0)
    if filtro is not None:
        casos_validos &= filtro

    resultado = {"n": int(casos_validos.sum()),
                 "media": round(np.average(x[casos_validos], weights=datos.peso[casos_validos]), 1)}
    for nombre, q in [("p25", 0.25), ("mediana", 0.5), ("p75", 0.75)]:
        resultado[nombre] = round(float(cuantil_ponderado(x, q, filtro)), 1)
    return pd.Series(resultado, dtype=object)


def correlacion_ponderada(tabla, columnas):
    """Matriz de correlación de Spearman ponderada (usa los pares completos)."""

    def rango_ponderado(x, pesos):
        # Posición de cada valor entre 0 y 1, contando el peso de cada persona
        peso_por_valor = pd.DataFrame({"x": x, "peso": pesos}).groupby("x").peso.sum().sort_index()
        posicion = (peso_por_valor.cumsum() - peso_por_valor / 2) / peso_por_valor.sum()
        return x.map(posicion)

    matriz = pd.DataFrame(np.nan, index=columnas, columns=columnas)
    for col_a in columnas:
        for col_b in columnas:
            casos = tabla[col_a].notna() & tabla[col_b].notna() & (tabla.peso > 0)
            pesos = tabla.peso[casos]
            rango_a = rango_ponderado(tabla[col_a][casos], pesos)
            rango_b = rango_ponderado(tabla[col_b][casos], pesos)

            # Correlación de Pearson entre los rangos (= Spearman), con pesos
            desv_a = rango_a - np.average(rango_a, weights=pesos)
            desv_b = rango_b - np.average(rango_b, weights=pesos)
            covarianza = (pesos * desv_a * desv_b).sum()
            matriz.loc[col_a, col_b] = covarianza / np.sqrt((pesos * desv_a ** 2).sum() * (pesos * desv_b ** 2).sum())
    return matriz


# Prueba: ¿qué porcentaje de Chile fuma actualmente?
prevalencia(datos.fuma_actual)
'''))

    # ------------------------------------------------------------------ 4. Parte A
    c.append(md("""
## 4. Parte A — ¿Por qué ponderar?

Un **histograma** muestra cuántas personas caen en cada tramo de una variable. Si le pasamos los pesos (`weights=`), dibuja a **Chile** y no a quienes respondieron.
"""))
    ejercicio(
        "pesos", "¿A quién representa la muestra? (histograma ponderado)",
        "a) Dibuja el histograma de la **edad** de dos formas: sin ponderar (las personas que respondieron) y ponderado (la población que representan). ¿Qué grupo de edad está sobrerrepresentado en la muestra? b) Calcula la prevalencia de **fumador actual** sin ponderar (promedio simple) y ponderada. ¿Por qué difieren? (Piensa: ¿los adultos mayores fuman más o menos que los demás?)",
        "`plt.hist(datos.edad, bins=range(15, 100, 5))`; para el segundo agrega `weights=datos.peso`. El promedio simple es `datos.fuma_actual.mean()`; el ponderado, `prevalencia(datos.fuma_actual)`.",
        """
tramos_edad = range(15, 100, 5)
fig, ejes = plt.subplots(1, 2, figsize=(10, 3.6))

# Izquierda: las personas que respondieron (sin ponderar)
ejes[0].hist(datos.edad, bins=tramos_edad, color="#999999", edgecolor="white")
ejes[0].set(title=f"Muestra (sin ponderar)\\nmediana {datos.edad.median():.0f} años",
            xlabel="Edad (años)", ylabel="Personas encuestadas")

# Derecha: la población que representan (cada persona pesa según su peso)
ejes[1].hist(datos.edad, bins=tramos_edad, weights=datos.peso / 1e6, color="#2a6f97", edgecolor="white")
ejes[1].set(title=f"Población representada (ponderada)\\nmediana {cuantil_ponderado(datos.edad):.0f} años",
            xlabel="Edad (años)", ylabel="Millones de personas")
plt.tight_layout()
plt.show()

# Porcentaje de cada tramo de edad, en la muestra y en Chile
pct_muestra = datos.grupo_edad.value_counts(normalize=True, sort=False) * 100
pct_chile = datos.groupby("grupo_edad", observed=True).peso.sum() / datos.peso.sum() * 100
print(pd.DataFrame({"% en la muestra": pct_muestra, "% en Chile (ponderado)": pct_chile}).round(1))

# Fumador actual: promedio simple vs. ponderado
print("Fumador actual SIN ponderar:", round(100 * datos.fuma_actual.mean(), 1), "%")
print("Fumador actual PONDERADO:   ", prevalencia(datos.fuma_actual).to_dict())
""")

    # ------------------------------------------------------------------ 5. Parte B
    c.append(md("""
## 5. Parte B — Prevalencias
"""))
    ejercicio(
        "prev", "Prevalencia de fumadores",
        "Calcula la prevalencia de **fumador actual** en toda la población y luego **por sexo, por zona (urbana/rural) y por grupo de edad**. ¿Quién fuma más?",
        "`prevalencia(datos.fuma_actual)` da el total. Para un subgrupo pasa un filtro: `prevalencia(datos.fuma_actual, datos.sexo == 'Hombres')`.",
        """
print("Total:", prevalencia(datos.fuma_actual).to_dict())

# Una prevalencia por cada categoría de sexo, zona y grupo de edad
for variable in ["sexo", "area", "grupo_edad"]:
    for categoria in sorted(datos[variable].dropna().unique()):
        resultado = prevalencia(datos.fuma_actual, datos[variable] == categoria)
        print(variable, categoria, resultado.to_dict())
""")
    ejercicio(
        "pasivo", "Fumador pasivo y su definición",
        "Define **fumador pasivo** como una persona que **no fuma actualmente** (nunca o ex) y está **expuesta al humo ajeno** (`expuesto_humo == 1`).\n\na) Calcula su prevalencia total y en los tres ambientes (casa, trabajo/estudio, otros).\n\nb) Entre quienes no fuman, dibuja el histograma de horas diarias de exposición (`horas_humo_total`). ¿Qué porcentaje no tiene ninguna exposición? Entre los expuestos, ¿cuál es la mediana de horas?\n\nc) Recalcula la prevalencia de fumador pasivo exigiendo **≥ 2** y **≥ 5** horas diarias en vez de ≥ 1. ¿Cuánto depende el resultado de la regla que elegimos?",
        "Usa un filtro: `no_fuma = datos.estado_fumador.isin(['nunca', 'ex'])`. Para los umbrales: `prevalencia((datos.horas_humo_total >= k).astype(float), no_fuma)` con `k = 1, 2, 5`.",
        """
# Quienes no fuman actualmente (nunca fumaron o son ex fumadores)
no_fuma = datos.estado_fumador.isin(["nunca", "ex"])

# a) Prevalencia de fumador pasivo, en total y por ambiente
print("Pasivo (no fuma + expuesto):", prevalencia(datos.expuesto_humo, no_fuma).to_dict())
for ambiente in ["expuesto_casa", "expuesto_trabajo", "expuesto_otros"]:
    print(ambiente, prevalencia(datos[ambiente], no_fuma).to_dict())

# b) Histogramas de horas de exposición (12 = 12 horas o más)
expuestos = no_fuma & (datos.horas_humo_total > 0)
fig, ejes = plt.subplots(1, 2, figsize=(10, 3.6))

ejes[0].hist(datos.horas_humo_total[no_fuma].clip(upper=12), bins=np.arange(-0.5, 12.6),
             weights=datos.peso[no_fuma] / 1e6, color="#2a6f97", edgecolor="white")
ejes[0].set(title="Todos los que no fuman",
            xlabel="Horas diarias de humo ajeno (12 = 12 o más)", ylabel="Millones de personas")

ejes[1].hist(datos.horas_humo_total[expuestos].clip(upper=12), bins=np.arange(0.5, 12.6),
             weights=datos.peso[expuestos] / 1e6, color="#d1495b", edgecolor="white")
ejes[1].set(title="Solo los expuestos (≥ 1 h)",
            xlabel="Horas diarias de humo ajeno (12 = 12 o más)", ylabel="Millones de personas")
plt.tight_layout()
plt.show()

sin_exposicion = 100 - prevalencia(datos.expuesto_humo, no_fuma)["%"]
print(f"Sin ninguna exposición: {sin_exposicion:.1f}%")
print("Entre expuestos:", resumen_ponderado(datos.horas_humo_total, expuestos).to_dict())

# c) ¿Cuánto cambia la prevalencia según el umbral de horas?
for horas_minimas in [1, 2, 5]:
    pasivo_con_umbral = (datos.horas_humo_total >= horas_minimas).astype(float)
    print(f"Pasivo con ≥ {horas_minimas} h/día:", prevalencia(pasivo_con_umbral, no_fuma).to_dict())
""")

    # ------------------------------------------------------------------ 6. Parte C
    c.append(md("""
## 6. Parte C — Antes de comparar: ¿se parecen los grupos?

Si dos grupos difieren en **otras** características, comparar sus resultados sin cuidado lleva a conclusiones falsas. Aquí miramos la edad de fumadores y no fumadores y,
de forma opcional, qué variables se mueven juntas (**correlación**: un número entre −1 y +1 que mide cuánto *acompañan* dos variables entre sí; **no dice que una cause la otra**).
"""))
    ejercicio(
        "grupos", "¿Tienen la misma edad fumadores y no fumadores?",
        "Dibuja, superpuestos, los histogramas de edad de fumadores actuales y de no fumadores (ponderados y normalizados para poder compararlos). Calcula la edad media de cada grupo. **Antes** de correr ningún modelo: si los fumadores son más jóvenes, ¿qué esperas que pase con su riesgo de morir *sin ajustar*?",
        "`plt.hist(grupo.edad, bins=range(15, 100, 5), weights=grupo.peso, density=True, alpha=.55)` para cada grupo.",
        """
# Solo personas con dato de tabaquismo y con peso
con_dato = datos[datos.fuma_actual.notna() & (datos.peso > 0)]

fig, ax = plt.subplots(figsize=(7, 3.8))
for valor, etiqueta, color in [(0, "No fuma", "#2a6f97"), (1, "Fuma actualmente", "#d1495b")]:
    grupo = con_dato[con_dato.fuma_actual == valor]
    ax.hist(grupo.edad, bins=range(15, 100, 5), weights=grupo.peso,
            density=True, alpha=0.55, color=color, label=etiqueta)
ax.set(xlabel="Edad (años)", ylabel="Densidad (ponderada)")
ax.legend()
plt.show()

# Edad media de cada grupo, sin ponderar y ponderada
nombre_grupo = {0.0: "No fuma", 1.0: "Fuma actualmente"}
edad_media_simple = {}
edad_media_ponderada = {}
for valor, grupo in con_dato.groupby("fuma_actual"):
    edad_media_simple[nombre_grupo[valor]] = round(float(grupo.edad.mean()), 1)
    edad_media_ponderada[nombre_grupo[valor]] = round(float(np.average(grupo.edad, weights=grupo.peso)), 1)
print("Edad media sin ponderar:", edad_media_simple)
print("Edad media ponderada:   ", edad_media_ponderada)
""")
    ejercicio(
        "corr", "(Opcional) ¿Qué variables se mueven juntas? (correlaciones)",
        "Calcula la matriz de correlaciones (Spearman ponderada) entre `edad`, `cigarrillos_dia`, `horas_casa`, `horas_trabajo`, `horas_otros`, `imc` y `colesterol`, y dibújala como mapa de calor. a) ¿Qué variable se correlaciona con más de las otras? b) ¿Qué ambientes de exposición van juntos? c) ¿Qué te dice esto sobre ajustar por edad? d) ¿Por qué una correlación de 0,28 *no* demuestra que la edad suba el colesterol por sí sola?",
        "`matriz_corr = correlacion_ponderada(datos, columnas)`; para el gráfico, `plt.imshow(matriz_corr, cmap='RdBu_r', vmin=-1, vmax=1)`. Ojo con cuántos casos tiene cada par: `cigarrillos_dia` solo existe para fumadores actuales.",
        """
columnas_corr = ["edad", "cigarrillos_dia", "horas_casa", "horas_trabajo", "horas_otros", "imc", "colesterol"]
matriz_corr = correlacion_ponderada(datos, columnas_corr)

fig, ejes = plt.subplots(1, 2, figsize=(11.5, 4.4), gridspec_kw={"width_ratios": [1.25, 1]})

# Izquierda: mapa de calor con el valor de cada correlación escrito encima
mapa = ejes[0].imshow(matriz_corr, cmap="RdBu_r", vmin=-1, vmax=1)
ejes[0].set_xticks(range(len(columnas_corr)), columnas_corr, rotation=45, ha="right")
ejes[0].set_yticks(range(len(columnas_corr)), columnas_corr)
for fila in range(len(columnas_corr)):
    for columna in range(len(columnas_corr)):
        ejes[0].text(columna, fila, f"{matriz_corr.iloc[fila, columna]:.2f}",
                     ha="center", va="center", fontsize=8)
plt.colorbar(mapa, ax=ejes[0], shrink=0.8)

# Derecha: un ejemplo concreto (edad contra colesterol)
ejes[1].scatter(datos.edad, datos.colesterol, s=6, alpha=0.25, color="#2a6f97")
ejes[1].set(xlabel="Edad (años)", ylabel="Colesterol total (mg/dL)",
            title=f"Edad vs colesterol (ρ = {matriz_corr.loc['edad', 'colesterol']:.2f})")
plt.tight_layout()
plt.show()

matriz_corr.round(2)
""")

    # ------------------------------------------------------------------ 7. Parte D
    c.append(md("""
## 7. Parte D — ¿Fumar se asocia con morir antes?

### Cómo leer un HR (el modelo de Cox, en simple)

Queremos comparar qué tan probable es morir en distintos grupos. Hay un detalle: **no todos fueron seguidos el mismo tiempo**.
Una persona encuestada a inicios de 2016 tiene más años de seguimiento que una de 2017, y quienes siguen vivos en 2023 solo sabemos que sobrevivieron *al menos* hasta esa fecha.

El **modelo de Cox** resuelve esto: compara el riesgo de morir **en cada momento** del seguimiento entre los grupos, usando a quienes seguían vivos en ese momento. Así aprovecha a todos.
Su resultado es el **HR** (*hazard ratio*, razón de riesgos). No necesitas la matemática; basta saber leerlo:

| HR | Significa |
|---|---|
| 1 | el grupo tiene el mismo riesgo de morir que el grupo de comparación |
| 2 | el doble de riesgo |
| 0,5 | la mitad del riesgo |

Cada HR viene con su **intervalo de confianza (IC 95%)**: si el rango incluye al 1, la diferencia no es clara.
**Ajustar** por edad y sexo significa comparar personas de la misma edad y sexo, para que eso no distorsione el resultado.
"""))
    ejercicio(
        "enganoso", "El resultado engañoso",
        f"Retoma lo que viste en el ejercicio {N['grupos']}. Compara el **porcentaje de fallecidos** entre fumadores actuales y no fumadores (sin ajustar) y luego estima el HR **sin ajustar** con `cox(['fuma_actual'])`. ¿Fumar parece proteger? ¿Qué falta?",
        "Compara también la **edad media** de ambos grupos: `datos.groupby('fuma_actual').edad.mean()`.",
        """
# Porcentaje de fallecidos y edad media, según fume o no (0 = no fuma, 1 = fuma)
print("% de fallecidos:")
print(datos.groupby("fuma_actual").fallecido.mean().mul(100).round(1))
print()
print("Edad media (años):")
print(datos.groupby("fuma_actual").edad.mean().round(1))

# HR sin ajustar: compara fumadores con no fumadores, sin mirar la edad
cox(["fuma_actual"])
""")
    ejercicio(
        "ajuste", "Ajustar por edad y sexo",
        "Repite el modelo agregando `edad` y `mujer`. ¿Qué pasa con el HR de `fuma_actual`? Explica **por qué** cambia.",
        "`cox(['fuma_actual', 'edad', 'mujer'])`.",
        """
# HR ajustado: compara fumadores con no fumadores de la misma edad y sexo
cox(["fuma_actual", "edad", "mujer"])
""")
    ejercicio(
        "cuatro", "Fumadores activos, ex fumadores y pasivos",
        "Arma cuatro grupos: **(ref.) nunca fumó y sin exposición**, **pasivo** (nunca fumó y expuesto), **ex fumador** y **fumador actual**. Estima el HR de cada uno ajustando por edad y sexo. ¿Hay evidencia de riesgo en los pasivos? Mira el **número de muertes** de ese grupo antes de concluir.",
        "Crea tres columnas 0/1 (`pasivo`, `ex`, `actual`) y pásalas a `cox(...)` junto a `edad` y `mujer`. Usa solo las filas con `estado_fumador` no nulo.",
        """
# Solo personas con dato de tabaquismo
tabla_grupos = datos[datos.estado_fumador.notna()].copy()

# Tres columnas 0/1; el grupo de comparación es quien nunca fumó y no está expuesto
tabla_grupos["pasivo"] = ((tabla_grupos.estado_fumador == "nunca") & (tabla_grupos.expuesto_humo == 1)).astype(float)
tabla_grupos["ex"] = (tabla_grupos.estado_fumador == "ex").astype(float)
tabla_grupos["actual"] = tabla_grupos.estado_fumador.isin(["diario", "ocasional"]).astype(float)

# Cuántas personas y cuántas muertes hay en cada grupo (¡mira los pasivos!)
tabla_grupos["grupo"] = np.select(
    [tabla_grupos.actual == 1, tabla_grupos.ex == 1, tabla_grupos.pasivo == 1],
    ["actual", "ex", "pasivo"],
    default="referencia (nunca, sin exposición)")
print(tabla_grupos.groupby("grupo").fallecido.agg(personas="count", muertes="sum"))

# HR de cada grupo contra la referencia, ajustado por edad y sexo
cox(["pasivo", "ex", "actual", "edad", "mujer"], tabla_grupos)
""")

    # ------------------------------------------------------------------ 8. Parte E
    c.append(md(f"""
## 8. Parte E — Curvas de supervivencia

Las curvas muestran la proporción de personas vivas a lo largo del tiempo. Comparar **dentro de un grupo de edad** evita la confusión que viste en el ejercicio {N['enganoso']}.
"""))
    ejercicio(
        "km", "Curva por grupo de edad",
        "Dibuja la supervivencia de fumadores y no fumadores solo entre personas de **40 a 59 años**. ¿Se separan las curvas?",
        "Usa `KaplanMeierFitter().fit(tiempo, evento, weights=peso)` y `.plot_survival_function()`.",
        """
# Solo personas de 40 a 59 años con dato de tabaquismo
de_40_a_59 = datos[datos.edad.between(40, 59) & datos.fuma_actual.notna() & (datos.peso > 0)]

fig, ax = plt.subplots(figsize=(6, 4))
for valor, etiqueta in [(0, "No fuma"), (1, "Fuma actual")]:
    grupo = de_40_a_59[de_40_a_59.fuma_actual == valor]
    curva = KaplanMeierFitter().fit(grupo.anios_seguimiento, grupo.fallecido,
                                    weights=grupo.peso, label=f"{etiqueta} (n={len(grupo)})")
    curva.plot_survival_function(ax=ax, ci_show=False)

ax.set_ylim(0.8, 1.01)
ax.set_xlabel("Años desde la encuesta")
ax.set_ylabel("Proporción viva")
ax.grid(alpha=0.3)
plt.show()
""")

    # ------------------------------------------------------------------ 9. Discusión
    c.append(md("""
## 9. Preguntas para discutir en grupo
1. ¿Por qué el HR sin ajustar (< 1) y el ajustado (> 1) apuntan en direcciones opuestas? ¿Qué otras variables podrían confundir?
2. ¿Qué cambiaría si definimos fumador pasivo con otro umbral? ¿Cómo lo probarías?
3. ¿Qué otras preguntas podrías responder con esta base? (por ejemplo: hipertensión, diabetes, obesidad, o la misma pregunta en la ENS 2003 y 2009-10).
4. La edad se correlaciona con el colesterol, el IMC y la exposición al humo. ¿Qué otras variables deberías medir y ajustar antes de interpretar un HR como efecto del tabaco?

---
**Fuentes:** Ministerio de Salud de Chile, Departamento de Epidemiología. *Encuesta Nacional de Salud 2016-2017*, base de datos y manual de uso. https://epi.minsal.cl/bases-de-datos/
"""))

    nb = nbf.v4.new_notebook(); nb.cells = c
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    return nb

if __name__ == "__main__":
    for fac, tipo, name in [(False, None, "taller_tabaco_PARTICIPANTES.ipynb"),
                            (True, None, "taller_tabaco_FACILITADOR.ipynb"),
                            (True, "resuelta (paso a paso, con explicaciones y pauta de resolución)", "taller_tabaco_RESUELTO.ipynb")]:
        nbf.write(build(fac, tipo), OUT + name); print("escrito", name)
