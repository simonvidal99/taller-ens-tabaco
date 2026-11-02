# Propuesta de análisis: tabaco y riesgo de muerte (ENS 2016-17)

## La idea en una frase

Usamos una base pública que ya existe (la Encuesta Nacional de Salud 2016-17) para contar cuánta gente fuma en Chile y ver si fumar se asocia con morir antes. No se recolecta nada nuevo: el taller enseña a investigar con datos que otros ya levantaron.

**Las dos preguntas del taller**

1. ¿Cuál es la prevalencia de fumadores y de fumadores pasivos en Chile?
2. ¿Cuál es la asociación entre la exposición al tabaco y el riesgo de muerte?

**Por qué esta base:** es la única nacional que mide tabaco y que el Minsal ya cruzó con los registros de defunción hasta 2023. Así sabemos quién fumaba al inicio y quién murió después.

## Los datos

La base reúne 6.233 personas de 15 años o más, encuestadas en 2016-17, y registra si murieron hasta el 31-12-2023 (539 fallecidos; seguimiento mediano de 7,1 años). Es pública y anonimizada: se baja de [epi.minsal.cl](https://epi.minsal.cl/bases-de-datos/).

Cada fila es una persona. Como la encuesta no reparte a todos por igual, cada persona trae un **peso** que dice a cuántos chilenos representa (en total, 14.518.969).

| Qué necesitamos | Columnas | Para qué sirve |
| --- | --- | --- |
| Peso y diseño de la muestra | `Fexp_F1p_Corr`, `Estrato`, `Conglomerado` | Que los porcentajes representen a Chile y que los intervalos de confianza sean honestos |
| Fuma o no | `ta3` | Fumador actual, ex fumador o nunca fumó |
| Cuánto y desde cuándo fuma | `ta4` (cigarrillos al día), `ta6` (edad de inicio) | Describir el hábito |
| Humo ajeno | `ta11`, `ta12`, `ta13` (horas en casa, trabajo/estudio y otros lugares) | Definir al fumador pasivo |
| Muerte | `FECHA_DEF`, `ANO_DEF` | Saber quién murió y cuándo |
| Otras características | `Edad`, `Sexo`, `IMC`, `Colesterol_Total` | Ajustar y explorar |

La definición de «fumador pasivo» es nuestra: no fuma hoy y estuvo expuesto al humo ajeno al menos una hora en alguno de los tres ambientes. La encuesta no trae una variable ya armada.

## El análisis paso a paso

El taller sigue el camino de una investigación real, en seis pasos. Cada uno responde una pregunta simple.

1. **Conocer la base.** ¿Qué es una fila, a quién representa y con qué peso se cuenta? Sin esto, los porcentajes no sirven.
2. **Mirar cómo se distribuyen los datos.** Histogramas de edad, de cigarrillos al día, de edad de inicio y de horas de humo ajeno. Sirve para entender a la población antes de calcular nada.
3. **Calcular prevalencias.** ¿Qué porcentaje fuma? ¿Qué porcentaje de quienes no fuman está expuesto al humo? Siempre con intervalo de confianza.
4. **Revisar si los grupos son comparables.** ¿Fumadores y no fumadores tienen la misma edad? ¿Qué variables se mueven juntas (correlaciones)?
5. **Medir la asociación con la muerte.** Comparamos quién murió hasta 2023 según su exposición, primero sin ajustar y luego ajustando por edad y sexo.
6. **Poner a prueba el resultado.** Excluimos las muertes tempranas, dibujamos curvas de supervivencia y declaramos las limitaciones.

**Palabras clave, en simple**

| Término | Qué significa |
| --- | --- |
| Prevalencia | Porcentaje de la población que tiene una característica en un momento (por ejemplo, fuma hoy) |
| Ponderador (peso) | Cuántas personas de Chile representa cada encuestado; corrige que la muestra no sea un reparto igual |
| Intervalo de confianza 95% | Rango donde probablemente está el valor real; mientras más angosto, más precisa la estimación |
| Histograma | Gráfico de barras que muestra cuántas personas caen en cada tramo de una variable |
| Media y mediana | Promedio y valor del medio; si hay pocos valores muy altos, la media sube y la mediana no |
| Correlación | Número entre −1 y +1 que dice cuánto acompañan dos variables entre sí; no prueba que una cause la otra |
| Hazard ratio (HR) | Cuántas veces es mayor el riesgo de morir en un grupo que en otro, en cualquier momento del seguimiento. HR 2 = el doble |
| Ajustar | Comparar grupos como si tuvieran la misma edad y sexo, para que eso no distorsione el resultado |
| Confusión | Cuando otra variable (como la edad) explica una diferencia que parecía venir de la exposición |

## Distribuciones y correlaciones

Antes de calcular riesgos, el taller mira la forma de los datos con histogramas y correlaciones. Cada gráfico prepara una decisión posterior: por qué ponderar, cómo definir al fumador pasivo y por qué ajustar por edad.

| Qué se mira | Qué se ve (ENS 2016-17) | Para qué sirve en nuestra pregunta |
| --- | --- | --- |
| Histograma de edad, sin ponderar y ponderado | Mediana de 50 años en la muestra y de 41 en la población | Muestra por qué hay que usar el peso: la muestra tiene más adultos mayores que Chile |
| Cigarrillos al día (fumadores actuales) | Mediana 7, media 12,7; 35% declara exactamente 5, 10 o 20 | Distribución asimétrica: la media exagera, y la gente redondea lo que declara |
| Edad de inicio | Mediana 17 años (la mitad empezó entre los 15 y los 19) | Describe el hábito: casi todo el mundo parte en la adolescencia |
| Horas de humo ajeno (quienes no fuman) | 74% no tiene exposición; entre expuestos la mediana es 2 horas | Justifica la definición de pasivo; con ≥ 1 h es 25,9%, con ≥ 2 h 14,9% y con ≥ 5 h 4,9% |
| Histograma de edad, fumadores contra no fumadores | Edad media ponderada de 39 contra 45 años | Anticipa el resultado engañoso: los fumadores son más jóvenes, así que mueren menos sin ajustar |
| Mapa de correlaciones | Edad con colesterol 0,28, con IMC 0,24 y con exposición en el trabajo −0,17 | La edad se mueve junto con casi todo, así que hay que ajustar por ella |

Las tres exposiciones al humo (casa, trabajo y otros lugares) se correlacionan entre sí (0,29 a 0,38): quien está expuesto en un lugar suele estarlo en otros. Y quienes fuman más cigarrillos al día también están más expuestos al humo en casa (0,18).

Las correlaciones son de Spearman, ponderadas. Son descriptivas: no tienen intervalo de confianza y no prueban causa.

## Resultados de referencia y cómo leerlos

El 32,5% de los chilenos de 15 años o más fuma, y fumar se asocia con morir antes solo después de ajustar por edad. Estos son los números que el cuaderno reproduce.

| Indicador | Resultado (IC 95%) | Cómo leerlo |
| --- | --- | --- |
| Fumador actual | 32,5% (30,4–34,6) | Uno de cada tres; 36,7% en hombres y 28,5% en mujeres |
| Fumador pasivo (no fuma y está expuesto) | 25,9% (23,1–28,6) | Definición propia: al menos 1 hora diaria en casa, trabajo u otros lugares |
| HR de morir, fumador actual contra no fumador, sin ajustar | 0,66 (0,44–1,00) | Parece que fumar protege, pero es un espejismo |
| El mismo HR, ajustado por edad y sexo | 1,83 (1,31–2,56) | Al comparar personas de la misma edad, fumar casi duplica el riesgo |
| Fumador actual contra quien nunca fumó y no está expuesto | 2,04 (1,43–2,90) | Referencia más limpia: el riesgo se duplica |
| Ex fumador, misma referencia | 1,33 (0,99–1,78) | Riesgo intermedio, en el límite de lo significativo |
| Fumador pasivo, misma referencia | 0,63 (0,35–1,16) | No concluyente: solo 24 muertes |

**La lección central.** Sin ajustar, los fumadores mueren menos (5,6% contra 9,9%) porque son más jóvenes. El histograma de edad lo muestra antes de correr el modelo. Al ajustar, el efecto aparece.

**Sobre los fumadores pasivos.** Que el intervalo incluya al 1 no significa que no haya efecto: con 24 muertes el estudio no tiene poder para detectarlo. «Ausencia de evidencia no es evidencia de ausencia».

## Limitaciones y preguntas probables

El análisis muestra asociación, no causa, y tiene límites que conviene declarar antes de que los pregunten.

| Pregunta probable | Respuesta honesta |
| --- | --- |
| ¿Por qué no promediar sin más? | Sin ponderar, los fumadores salen 28,2% en vez de 32,5%, y el intervalo se ve el doble de angosto de lo que corresponde |
| ¿Esto prueba que fumar mata? | No. Es un estudio observacional. Ajustamos por edad y sexo, pero faltan nivel socioeconómico, alcohol y enfermedades previas |
| ¿Y si los enfermos ya habían dejado de fumar? | Es la causalidad inversa. Al excluir las muertes de los primeros 2 años el HR sigue en 2,00 (1,39–2,88) |
| ¿Por qué no hay efecto en los fumadores pasivos? | Hay 24 muertes en ese grupo: falta poder estadístico, no hay evidencia de que sea inocuo |
| ¿Las correlaciones prueban algo? | Solo describen qué variables van juntas. Una correlación de 0,28 entre edad y colesterol no dice que la edad cause el colesterol por sí sola |
| ¿El tabaco se midió bien? | Una sola vez, al inicio, y por autorreporte. Quien cambió de hábito después queda mal clasificado |
| ¿La definición de pasivo es estándar? | No, es nuestra. Cambia mucho con el umbral: 25,9% con ≥ 1 h, 14,9% con ≥ 2 h y 4,9% con ≥ 5 h |
| ¿Son confiables los intervalos de la mortalidad? | Agrupan por conglomerado pero no incorporan el estrato; son una aproximación |
| ¿Se comparó el 32,5% con el informe oficial de la ENS? | No se verificó todavía; es un pendiente |

Uso de los datos: son públicos y anonimizados, pero el Minsal pide usarlos solo para investigación, citar la fuente y enviarles copia de las publicaciones. Conviene confirmar con el comité de ética de la institución.

## Cómo se desarrolla el taller

El taller dura unas 3 horas, con 14 ejercicios en un cuaderno de Python; se recorta a 2,5 horas omitiendo los ejercicios 3, 6 y 12. Los participantes escriben entre una y cinco líneas por ejercicio: las funciones complejas ya vienen escritas.

| Minutos | Bloque | Ejercicios |
| --- | --- | --- |
| 0–15 | Presentación: pregunta, ética y condiciones de uso | — |
| 15–30 | Conocer la base | 1 |
| 30–55 | Parte A: distribuciones (histogramas) | 2 y 3 |
| 55–80 | Parte B: prevalencias | 4, 5 y 6 |
| 80–95 | Pausa | — |
| 95–125 | Parte C: ¿se parecen los grupos? Edad y correlaciones | 7 y 8 |
| 125–155 | Parte D: asociación con la muerte | 9, 10 y 11 |
| 155–170 | Sensibilidad y curvas de supervivencia | 12 y 13 |
| 170–185 | Redactar el párrafo de resultados y discutir | 14 |

**Materiales:** el cuaderno de participantes, el cuaderno del facilitador con soluciones, la guía del facilitador y una presentación de 19 diapositivas. Los datos se descargan aparte desde el Minsal.
