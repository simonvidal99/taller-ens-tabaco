# Taller: tabaco y riesgo de muerte con la Encuesta Nacional de Salud (Chile)

> **English summary.** Workshop materials on *how to do research with existing databases*, using Chile's
> National Health Survey (ENS) 2016-17 linked to death records through 2023. It answers two questions:
> (1) what is the prevalence of smokers and passive smokers, and (2) is tobacco exposure associated with mortality?
> Includes participant and facilitator notebooks (Python), a facilitator guide, a Beamer slide deck (PDF),
> result tables and the analysis scripts. **The raw survey data are not included**; see [Datos](#datos).
> Documentation is in Spanish.

Material para un taller sobre **cómo investigar con bases de datos existentes**, usando la
Encuesta Nacional de Salud (ENS) 2016-17 del Ministerio de Salud de Chile, cruzada con defunciones hasta 2023.

**Preguntas de investigación**
1. ¿Cuál es la prevalencia de fumadores y de fumadores pasivos en Chile?
2. ¿Cuál es la asociación entre la exposición al tabaco y el riesgo de muerte?

---

## ¿Por dónde empiezo? (según quién seas)

| Si eres… | Mira primero | Después |
|---|---|---|
| **Facilitador** (vas a dictar el taller) | [`taller/GUIA_FACILITADOR.md`](taller/GUIA_FACILITADOR.md): objetivos, tiempos, clave de respuestas, errores frecuentes | [`taller/taller_tabaco_FACILITADOR.ipynb`](taller/taller_tabaco_FACILITADOR.ipynb) (con soluciones) y la [presentación](taller/presentacion_taller_tabaco.pdf) |
| **Participante** | [`taller/taller_tabaco_PARTICIPANTES.ipynb`](taller/taller_tabaco_PARTICIPANTES.ipynb): 9 ejercicios con espacio para tu código | [`taller/LEEME.md`](taller/LEEME.md) para ejecutarlo |
| **Quien solo quiere los resultados** | [`analisis/`](analisis/): tablas en CSV y gráficos | Sección [Resultados](#resultados-principales) más abajo |
| **Quien quiere reproducir o auditar el análisis** | [`scripts/`](scripts/) y [`scripts/LEEME.md`](scripts/LEEME.md) | [`taller/datos/LEEME_DATOS.md`](taller/datos/LEEME_DATOS.md) para obtener los datos |

## Qué hay en cada carpeta

```
.
├── README.md                          ← estás aquí
├── taller/
│   ├── GUIA_FACILITADOR.md            guía: tiempos, clave de respuestas, puntos de enseñanza
│   ├── taller_tabaco_PARTICIPANTES.ipynb   ejercicios en blanco (se reparte)
│   ├── taller_tabaco_FACILITADOR.ipynb     igual, con soluciones y salidas ejecutadas
│   ├── presentacion_taller_tabaco.pdf      presentación (19 diapositivas)
│   ├── presentacion/                  fuente LaTeX (Beamer) y figuras
│   └── datos/                         aquí va el .sav descargado (no incluido)
├── analisis/                          resultados en CSV y gráficos
└── scripts/                           código Python que genera todo lo anterior
```

### Archivos de `analisis/`

| Archivo | Contenido |
|---|---|
| `ens2016_prevalencias.csv` | Prevalencia (IC 95%) de tabaquismo activo y pasivo por sexo, zona y edad. **ENS 2016-17** |
| `ens2016_cox_mortalidad_total.csv` | Razones de riesgo (HR) de morir según tabaco. ENS 2016-17 |
| `ens2016_cox_tabaco_pasivo.csv` | HR para fumadores activos, ex fumadores y pasivos. ENS 2016-17 |
| `ens2016_cox_por_causa.csv` | HR por causa de muerte (pocos casos; interpretar con cautela) |
| `ens2016_mortalidad_cruda_por_edad_y_tabaco.csv` | Mortalidad cruda por edad: muestra la confusión por edad |
| `ens2016_supervivencia_KM_por_tabaco.png` | Curvas de supervivencia por grupo de edad |
| `cox_mortalidad_total.csv`, `cox_por_causa.csv`, `mortalidad_cruda_por_edad_y_tabaco.csv`, `supervivencia_KM_por_tabaco.png` | El análisis de mortalidad y tabaco con la **ENS 2003** (sin el prefijo `ens2016_`), útil para contrastar: seguimiento de 20 años, resultado menos claro |
| `ens2003_prevalencias.csv` | Prevalencias de enfermedades crónicas (HTA, diabetes, obesidad, etc.) en la ENS 2003. No es de tabaco; fue un primer ejercicio |

---

## Resultados principales

ENS 2016-17: 6.233 personas, 539 fallecidos hasta el 31-12-2023, seguimiento mediano 7,1 años.
Prevalencias ponderadas con estratos y conglomerados.

| Indicador | Resultado |
|---|---|
| Fumador actual | **32,5%** (IC 95% 30,4–34,6) |
| Fumador pasivo (no fuma y está expuesto) | **25,9%** (23,1–28,6) |
| HR de morir, fumador actual vs no, **sin ajustar** | 0,66 (0,44–1,00) |
| HR, fumador actual vs no, **ajustado por edad y sexo** | 1,83 (1,31–2,56) |
| HR, fumador actual vs nunca fumó y sin exposición | **2,04** (1,43–2,90) |
| HR, fumador pasivo (solo 24 muertes) | 0,63 (0,35–1,16), **no concluyente** |

**Lección central:** sin ajustar por edad los fumadores parecen vivir más, porque son más jóvenes (confusión).
Y «no encontramos asociación» en fumadores pasivos refleja poca potencia, no ausencia de efecto.

## Cómo ejecutar el taller

1. Descargar los datos (ver abajo) y dejar el `.sav` en `taller/datos/`.
2. Abrir un cuaderno en Jupyter o en [Google Colab](https://colab.research.google.com/) (en Colab, subir el `.sav`).
3. Ejecutar las celdas en orden. La primera instala las librerías: `pandas numpy scipy pyreadstat lifelines matplotlib`.

El cuaderno del facilitador se ejecutó completo, sin errores, antes de subirlo.

## Datos

**Los datos no están en este repositorio.** Se descargan desde
[epi.minsal.cl/bases-de-datos](https://epi.minsal.cl/bases-de-datos/): base **«ENS + Defunción (Mortalidad) 2023»**.
El archivo se llama `.zip` pero es un **RAR**. Instrucciones completas en
[`taller/datos/LEEME_DATOS.md`](taller/datos/LEEME_DATOS.md).

Condiciones de uso del Minsal: solo para investigación, citar la fuente y enviar copia de las publicaciones
([condiciones](https://epi.minsal.cl/condiciones-de-uso/)).

## Limitaciones

- Tabaco medido una sola vez; exposición pasiva autorreportada y con definición propia (≥ 1 hora de exposición en cualquier ambiente).
- Los errores estándar de mortalidad agrupan por conglomerado pero **no incorporan el estrato**.
- La prevalencia de 32,5% **no fue contrastada** con el informe oficial de la ENS.
- Estudio observacional: asociación, no causalidad.
- Los scripts tienen rutas absolutas del equipo de origen; hay que editarlas antes de ejecutarlos.

## Fuente

Ministerio de Salud de Chile, Departamento de Epidemiología. *Encuesta Nacional de Salud 2016-2017*,
base de datos y manual de uso. https://epi.minsal.cl/bases-de-datos/
