# Guía del facilitador — Taller: investigar con bases de datos existentes
**Tema:** tabaco (activo y pasivo) y riesgo de muerte, Encuesta Nacional de Salud (ENS) 2016-17

## 1. Objetivo
Que cada participante recorra, con datos reales, el camino de una investigación con una base existente:
pregunta → datos → prevalencias → asociación con la muerte → ¿podemos creer el resultado?

**Al terminar, el participante debe poder explicar con sus palabras:**
1. **Qué es el peso** de cada encuestado (a cuántas personas de Chile representa) y por qué, sin él, se calcula el porcentaje de la muestra y no el de Chile.
2. **Qué es una prevalencia ponderada**: un porcentaje donde cada persona cuenta según su peso, con su intervalo de confianza.
3. **Qué hace una definición propia de exposición** (por ejemplo, «fumador pasivo = al menos 1 hora al día») y por qué hay que escribirla y probar otras.
4. **Qué es un HR** y por qué, para compararlo, hay que ajustar por edad.
5. Leer un histograma y una matriz de correlaciones sin confundir correlación con causa.

Los análisis más avanzados (por ejemplo, excluir muertes tempranas para descartar causalidad inversa) **no forman parte del taller**; las limitaciones se mencionan en una diapositiva, sin ejercicios.

## 2. Antes del taller (checklist)
- [ ] Descargar la base **«ENS + Defunción (Mortalidad) 2023»** de [epi.minsal.cl/bases-de-datos](https://epi.minsal.cl/bases-de-datos/)
      (enlace directo: `https://epi.minsal.cl/wp-content/uploads/2026/07/Base_ENS_Mortalidad_2023.zip`, 6,2 MB).
- [ ] **El archivo se llama `.zip` pero es un RAR.** Hace falta 7-Zip, WinRAR o The Unarchiver para abrirlo.
      Dentro hay tres archivos `.sav` (ENS 2003, 2009-10 y 2016-17); se usa el de **2016-2017**.
- [ ] Descargar el [manual de uso ENS 2016-17](https://epi.minsal.cl/wp-content/uploads/2019/02/Manual_de_Uso_de_la_base_de_datos_de_la_Encuesta_Nacional_de_Salud_2016_F1_F2_F4_EX1_EX2_14022019.pdf).
- [ ] Decidir cómo se ejecuta el cuaderno: **Google Colab** (sin instalar nada, sube el `.sav` a la sesión) o Python local con
      `pandas numpy scipy pyreadstat lifelines matplotlib`.
- [ ] Probar el cuaderno del facilitador completo en el mismo equipo/sala (ejecuta en pocos minutos).
- [ ] Revisar el correo de coordinación: la pregunta del taller es *«¿Cuál es la prevalencia de fumadores y fumadores pasivos en Chile? ¿Cuál es la asociación entre exposición a tabaco y riesgo de muerte?»*.

## 3. Materiales
| Archivo | Para quién | Contenido |
|---|---|---|
| `taller_tabaco_PARTICIPANTES.ipynb` | participantes | Explicaciones + 9 ejercicios con espacio en blanco |
| `taller_tabaco_FACILITADOR.ipynb` | facilitador | Igual, con **soluciones y salidas ya ejecutadas** |
| `presentacion_taller_tabaco.pdf` | facilitador | 17 diapositivas: contexto, resultados y limitaciones |

Los participantes escriben 1–5 líneas por ejercicio. Las funciones `prevalencia()`, `cox()`, `resumen_ponderado()`,
`cuantil_ponderado()` y `correlacion_ponderada()` ya vienen escritas; no se pide programar el diseño muestral ni la correlación ponderada, sí entender qué hacen.
Las correlaciones y resúmenes ponderados son descriptivos: no traen intervalo de confianza.

**La sección 1 del cuaderno** (conocer la base, qué es el peso) **y la sección 2** (variables) se muestran como ejemplo resuelto: se ejecutan y se comentan, no se piden como ejercicio.

### ¿La presentación va antes o en paralelo al cuaderno?
Propuesta (confirmar con el equipo): **en paralelo y en bloques cortos.** Se presentan las diapositivas de contexto (pregunta, base, variables, peso) antes de abrir el cuaderno;
luego, cada diapositiva de resultados se muestra **después** de que los participantes calculen lo suyo, para comparar. Cada una lleva abajo a la derecha una etiqueta «Cuaderno: ejercicio N».
Si se prefiere presentar todo antes, los participantes verían las respuestas antes de calcularlas: en ese caso conviene omitir las diapositivas de resultados.

## 4. Propuesta de tiempos (≈ 2 h 15; ≈ 1 h 50 sin el ejercicio 5 y sin el 9)
| Min | Bloque | Cuaderno | Diapositivas | Qué subrayar |
|---|---|---|---|---|
| 0–15 | Presentación | — | Qué vamos a hacer, Pregunta, Por qué una base existente, La base, Variables | Datos anónimos y públicos; citar y enviar copia al Minsal. «Fumador pasivo» es **nuestra** definición |
| 15–25 | Conocer la base y el peso | Secciones 1 y 2 (ejemplo resuelto) | Qué es el peso | Fila = persona; peso = a cuántas personas representa; estratos y conglomerados |
| 25–40 | ¿Por qué ponderar? | Ejercicio 1 | Ponderar cambia el resultado | Los 65+ están de más en la muestra y fuman poco: sin pesos, 28,2% en vez de 32,5% |
| 40–60 | Prevalencias | Ejercicios 2 y 3 | Resultado 1, Resultado 2 | Cómo cambia el porcentaje de pasivos con el umbral (25,9%, 14,9%, 4,9%) |
| 60–70 | Pausa | | | |
| 70–85 | ¿Se parecen los grupos? | Ejercicio 4 (y 5 opcional) | — | Los fumadores son más jóvenes; correlación no es causa |
| 85–110 | Asociación con la muerte | Ejercicios 6, 7 y 8 | Cómo leer un HR, Resultado 3, Resultado 4 | **El resultado engañoso**: confusión por edad; mirar el número de muertes |
| 110–120 | Curvas de supervivencia | Ejercicio 9 | Curvas de supervivencia | Comparar dentro de un grupo de edad |
| 120–135 | Discusión y cierre | Sección 9 | Limitaciones | Las preguntas para discutir son el cierre del taller |

## 5. Clave de respuestas (resultados de referencia)
Verificados al ejecutar el cuaderno del facilitador. Pueden variar en el último decimal según la versión de las librerías.

**Peso y diseño** (ejercicio 1; ejemplo resuelto):

| Dato | Resultado |
|---|---|
| Personas encuestadas / población representada | 6.233 / 14.518.969 (peso mínimo 3, máximo 24.000; promedio ≈ 2.300) |
| Estratos / conglomerados | 30 / 1.077 |
| Mediana de edad, muestra / Chile | 50 / 41 años |
| 65+ en la muestra / en Chile | 24,3% / 13,3% |
| Fumador actual, sin ponderar / ponderado | 28,2% / **32,5%** |

**Prevalencias** (ponderadas, con estratos y conglomerados):

| Indicador | Resultado (IC 95%) |
|---|---|
| Fumador actual, total | **32,5%** (30,4–34,6) |
| Hombres / Mujeres | 36,7% / 28,5% |
| Urbana / Rural | 33,8% / 21,9% |
| Por edad 15-24 / 25-44 / 45-64 / 65+ | 30,0% / 42,7% / 30,6% / 11,9% |
| Fumador pasivo (no fuma actualmente y expuesto) | **25,9%** (23,1–28,6), n = 4.473 |
| En el hogar / trabajo-estudio / otros (entre quienes no fuman) | 7,3% / 14,0% / 14,7% |
| Pasivo con ≥ 1 h / ≥ 2 h / ≥ 5 h diarias | 25,9% / 14,9% / 4,9% |
| Sin exposición alguna (entre quienes no fuman) | 74,1% (mediana de 2 h entre expuestos) |

**Edad y correlaciones** (ejercicios 4 y 5):

| Ejercicio | Resultado de referencia |
|---|---|
| 4. Edad media, no fuma / fuma | Ponderada 45,0 / 39,3; sin ponderar 51,2 / 43,1 |
| 5. Correlaciones (Spearman ponderada) | Edad con colesterol 0,28, con IMC 0,24, con exposición en el trabajo −0,17 y en otros lugares −0,19. Entre exposiciones: 0,29 a 0,38. Cigarrillos al día con horas en casa: 0,18 |

**Mortalidad** (n = 6.233; 539 muertes; seguimiento mediano 7,1 años):

| Modelo | HR (IC 95%) |
|---|---|
| Fumador actual vs no, **sin ajustar** | 0,66 (0,44–1,00) |
| Fumador actual vs no, **ajustado por edad y sexo** | **1,83** (1,31–2,56) |
| 4 grupos, ref. nunca fumó y sin exposición: pasivo | 0,63 (0,35–1,16), 24 muertes |
| ex fumador | 1,33 (0,99–1,78) |
| fumador actual | **2,04** (1,43–2,90) |

> **Ojo con las dos cifras para «fumador actual»:** 1,83 compara con *todos los no fumadores* (incluye ex fumadores y pasivos);
> 2,04 compara con quienes *nunca fumaron y no están expuestos*. Si preguntan, es una lección sobre **elegir el grupo de referencia**.

## 6. Puntos de enseñanza (y cómo abordarlos)
1. **Peso y diseño muestral (ejercicio 1).** Un promedio simple representa a la muestra, no a Chile. Los mayores de 65 son 24% de quienes
   respondieron pero 13% de Chile, y solo el 11,9% de ellos fuma: por eso sin ponderar sale 28,2% en vez de 32,5%.
   El intervalo de confianza con diseño es el doble de ancho que el de una muestra aleatoria simple (4,2 contra 2,2 puntos): ignorar el diseño da una precisión falsa.
2. **Definir la exposición (ejercicio 3).** La encuesta pregunta horas, no define «fumador pasivo». Con ≥ 1 h es 25,9%; con ≥ 2 h, 14,9%; con ≥ 5 h, 4,9%.
   Pedir a los participantes que propongan su regla y la justifiquen.
3. **Confusión (ejercicios 4 → 6 → 7).** Primero se ve que los fumadores son más jóvenes (ejercicio 4), luego que parecen
   morir menos: 5,6% fallecidos contra 9,9% (¡aparente efecto protector!). La edad media es 43,1 contra 51,2 años (sin ponderar).
   Al ajustar, el HR pasa de 0,66 a 1,83.
4. **Qué es un HR.** HR 1 = igual riesgo, 2 = el doble, 0,5 = la mitad; si el intervalo incluye al 1 la diferencia no es clara.
   No hace falta explicar la matemática del modelo de Cox: basta la idea de que compara el riesgo en cada momento del seguimiento.
5. **Poca potencia (ejercicio 8).** Solo 24 muertes entre los fumadores pasivos. *Ausencia de evidencia no es evidencia de ausencia.*
   Pedir que redacten la conclusión sin afirmar «el tabaco pasivo no hace daño».
6. **Correlación no es causa (ejercicio 5, opcional).** La edad es la variable que más se mueve con las otras; eso es una razón para
   ajustar, no una prueba de efecto. Una correlación de 0,28 es débil: el diagrama de dispersión se ve como una nube.

## 7. Errores frecuentes
- Usar un ponderador equivocado. Para el cuestionario F1 (tabaco) es `Fexp_F1p_Corr`; los exámenes de sangre usan otros.
- Dibujar un histograma sin `weights=` y concluir sobre «Chile»: describe solo a quienes respondieron.
- Interpretar `p > 0,05` como «no hay efecto».
- Olvidar que `fuma_actual` tiene valores perdidos (`NaN`); verificar el `n` de cada análisis.
- Leer `ta3` como número: viene codificado; el cuaderno mapea las etiquetas.
- Comparar HR sin fijar el grupo de referencia.
- Leer una correlación como causa, o creer que un valor cercano a 0 prueba que no hay relación (solo mide relación monótona).
- Olvidar que `cigarrillos_dia` solo existe para fumadores actuales: las correlaciones con ella usan menos casos.

## 8. Limitaciones de este material (decláralas)
- **Tabaco medido una vez**, al inicio del seguimiento.
- **Errores estándar de la mortalidad:** el modelo de Cox agrupa por conglomerado pero **no incorpora el estrato**.
  Las prevalencias sí usan estrato + conglomerado.
- **Exposición pasiva:** definición propia, autorreportada, sin cotinina.
- **Causas de muerte:** las categorías por causa (p. ej. cáncer de pulmón) tienen muy pocos casos; no se incluyen en el taller.
- **Cifras de referencia:** la prevalencia de 32,5% parece coherente con la publicada para la ENS 2016-17, pero **no se verificó**
  contra el informe oficial.
- **Causalidad inversa:** no se ejercita en el taller. En el análisis completo, al excluir las muertes de los primeros 2 años el HR ajustado se mantiene (2,00; IC 95% 1,39–2,88).

## 9. Extensiones para quien termine antes
- Repetir con otra variable de resultado (hipertensión, diabetes, obesidad).
- Cambiar la definición de «fumador pasivo» y comparar.
- Analizar por sexo o por zona.
- Dosis y riesgo: ¿sube el riesgo con los cigarrillos al día (`cigarrillos_dia`)?
- Contrastar con la ENS 2009-10 y 2003 (misma base de mortalidad, otros `.sav`).
- Hospitalizaciones: la base **«ENS con egresos hospitalarios»** ([minuta](https://epi.minsal.cl/bases-de-datos/)) permite estudiar ingresos por causa.
