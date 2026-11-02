# Taller: tabaco y riesgo de muerte con la Encuesta Nacional de Salud (Chile)

Material para un taller sobre **cómo investigar con bases de datos existentes**, usando la
Encuesta Nacional de Salud (ENS) 2016-17 del Ministerio de Salud de Chile.

**Preguntas de investigación**
1. ¿Cuál es la prevalencia de fumadores y de fumadores pasivos en Chile?
2. ¿Cuál es la asociación entre la exposición al tabaco y el riesgo de muerte?

## Contenido

| Carpeta | Qué hay |
|---|---|
| `taller/` | Cuadernos (participantes y facilitador), guía del facilitador y presentación en PDF |
| `taller/presentacion/` | Fuente LaTeX (Beamer) y figuras de la presentación |
| `analisis/` | Resultados en CSV y gráficos (ENS 2003 y ENS 2016-17) |
| `scripts/` | Scripts en Python que generan los resultados |

Empieza por [`taller/LEEME.md`](taller/LEEME.md) y [`taller/GUIA_FACILITADOR.md`](taller/GUIA_FACILITADOR.md).

## Resultados principales (ENS 2016-17, 6.233 personas, 539 fallecidos hasta 2023)

| Indicador | Resultado |
|---|---|
| Fumador actual | 32,5% (IC 95% 30,4–34,6) |
| Fumador pasivo (no fuma y está expuesto) | 25,9% (IC 95% 23,1–28,6) |
| HR de morir, fumador actual vs no, sin ajustar | 0,66 (0,44–1,00) |
| HR de morir, fumador actual vs no, ajustado por edad y sexo | 1,83 (1,31–2,56) |
| HR, fumador actual vs nunca fumó y sin exposición | 2,04 (1,43–2,90) |
| HR, fumador pasivo (24 muertes) | 0,63 (0,35–1,16), no concluyente |

Lección central del taller: sin ajustar por edad los fumadores parecen vivir más (confusión).

## Datos

**Los datos no están en este repositorio.** Se descargan desde
[epi.minsal.cl/bases-de-datos](https://epi.minsal.cl/bases-de-datos/); instrucciones en
[`taller/datos/LEEME_DATOS.md`](taller/datos/LEEME_DATOS.md). Condiciones de uso del Minsal: solo investigación,
citar la fuente y enviar copia de las publicaciones.

## Limitaciones

- Tabaco medido una sola vez; exposición pasiva autorreportada y con definición propia.
- Errores estándar de mortalidad agrupados por conglomerado, sin incorporar el estrato.
- La prevalencia de 32,5% no fue contrastada con el informe oficial.
- Los scripts tienen rutas absolutas del equipo de origen.

## Fuente

Ministerio de Salud de Chile, Departamento de Epidemiología. *Encuesta Nacional de Salud 2016-2017*, base de datos y manual de uso.
