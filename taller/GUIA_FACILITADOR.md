# Guía del facilitador — Taller: investigar con bases de datos existentes
**Tema:** tabaco (activo y pasivo) y riesgo de muerte, Encuesta Nacional de Salud (ENS) 2016-17

## 1. Objetivo
Que cada participante recorra, con datos reales, el camino completo de una investigación con una base existente:
pregunta → datos → variables → prevalencias → asociación → sesgos → cómo reportar.

**Al terminar, el participante debe poder:**
1. Identificar qué es una fila, qué peso usar y cómo se declara el diseño muestral.
2. Calcular prevalencias ponderadas con IC 95%.
3. Estimar una asociación con supervivencia (HR) y explicar por qué hay que ajustar por edad.
4. Reconocer límites: poca potencia, causalidad inversa, definiciones propias de la exposición.

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

## 3. Cuadernos
| Archivo | Para quién | Contenido |
|---|---|---|
| `taller_tabaco_PARTICIPANTES.ipynb` | participantes | Explicaciones + ejercicios con espacio en blanco |
| `taller_tabaco_FACILITADOR.ipynb` | facilitador | Igual, con **soluciones y salidas ya ejecutadas** |

Los participantes escriben 1–5 líneas por ejercicio. Las funciones `prevalencia()` y `cox()` ya vienen escritas; no
se pide programar el diseño muestral, sí entender qué hace.

## 4. Propuesta de tiempos (≈ 2,5 h; recortable a 2 h omitiendo ejercicios 7 y 8)
| Min | Bloque | Ejercicio | Qué subrayar |
|---|---|---|---|
| 0–15 | Presentación: pregunta, ética y condiciones de uso | — | Datos anónimos y públicos; citar y enviar copia al Minsal |
| 15–35 | Conocer la base | 1 | Fila = persona; ponderador `Fexp_F1p_Corr`; estratos y conglomerados |
| 35–50 | Construir variables | (lectura) | Cada definición es una decisión; «fumador pasivo» es **nuestra** definición |
| 50–80 | Prevalencia | 2 y 3 | Por qué no basta el promedio simple (ver §6) |
| 80–95 | Pausa | | |
| 95–125 | Asociación con la muerte | 4 y 5 | **El resultado engañoso**: confusión por edad |
| 125–145 | Fumadores activos, ex y pasivos | 6 | Mirar el número de muertes antes de concluir |
| 145–165 | Sensibilidad y curvas | 7 y 8 | Causalidad inversa; comparar dentro de un grupo de edad |
| 165–180 | Redactar y discutir | 9 + §8 | Qué falta para publicar |

## 5. Clave de respuestas (resultados de referencia)
Verificados al ejecutar el cuaderno del facilitador. Pueden variar en el último decimal según la versión de las librerías.

**Prevalencias** (ponderadas, con estratos y conglomerados):

| Indicador | Resultado (IC 95%) |
|---|---|
| Fumador actual, total | **32,5%** (30,4–34,6) |
| Hombres / Mujeres | 36,7% / 28,5% |
| Por edad 15-24 / 25-44 / 45-64 / 65+ | 30,0% / 42,7% / 30,6% / 11,9% |
| Fumador pasivo (no fuma actualmente y expuesto) | **25,9%** (23,1–28,6), n = 4.473 |
| En el hogar / trabajo-estudio / otros (entre quienes no fuman) | 7,3% / 14,0% / 14,7% |

**Mortalidad** (n = 6.233; 539 muertes; seguimiento mediano 7,1 años):

| Modelo | HR (IC 95%) |
|---|---|
| Fumador actual vs no, **sin ajustar** | 0,66 (0,44–1,00) |
| Fumador actual vs no, **ajustado por edad y sexo** | **1,83** (1,31–2,56) |
| 4 grupos, ref. nunca fumó y sin exposición: pasivo | 0,63 (0,35–1,16), 24 muertes |
| ex fumador | 1,33 (0,99–1,78) |
| fumador actual | **2,04** (1,43–2,90) |
| Excluyendo muertes < 2 años | 2,00 (1,39–2,88) |

> **Ojo con las dos cifras para «fumador actual»:** 1,83 compara con *todos los no fumadores* (incluye ex fumadores y pasivos);
> 2,04 compara con quienes *nunca fumaron y no están expuestos*. Si preguntan, es una lección sobre **elegir el grupo de referencia**.

## 6. Puntos de enseñanza (y cómo abordarlos)
1. **Peso y diseño muestral.** Un promedio simple no representa a Chile. Sin ponderar, la prevalencia de fumadores sale
   **28,2%** en vez de 32,5%. Y el IC con diseño es el doble de ancho que el de una muestra aleatoria simple
   (30,4–34,6, ancho 4,2 puntos, frente a 27,1–29,4, ancho 2,2 puntos): ignorar el diseño da una precisión falsa.
2. **Confusión (ejercicio 4 → 5).** Fumadores: 5,6% fallecidos; no fumadores: 9,9% (¡aparente efecto protector!).
   La edad media es 43,1 vs 51,2 años. Al ajustar, el HR pasa de 0,66 a 1,83.
3. **Potencia.** Solo 24 muertes entre los fumadores pasivos. *Ausencia de evidencia no es evidencia de ausencia.* Pedir
   que redacten la conclusión sin afirmar «el tabaco pasivo no hace daño».
4. **Definir la exposición.** Probar otra definición de «pasivo» (p. ej. solo exposición en el hogar) y ver si cambia.
5. **Causalidad inversa y sesgo de supervivencia.** Ejercicio 7 y curvas.

## 7. Errores frecuentes
- Usar un ponderador equivocado. Para el cuestionario F1 (tabaco) es `Fexp_F1p_Corr`; los exámenes de sangre usan otros.
- Interpretar `p > 0,05` como «no hay efecto».
- Olvidar que `fuma_actual` tiene valores perdidos (`NaN`); verificar el `n` de cada análisis.
- Leer `ta3` como número: viene codificado; el cuaderno mapea las etiquetas.
- Comparar HR sin fijar el grupo de referencia.

## 8. Limitaciones de este material (decláralas)
- **Tabaco medido una vez**, al inicio del seguimiento.
- **Errores estándar de la mortalidad:** el modelo de Cox agrupa por conglomerado pero **no incorpora el estrato**.
  Las prevalencias sí usan estrato + conglomerado.
- **Exposición pasiva:** definición propia, autorreportada, sin cotinina.
- **Causas de muerte:** las categorías por causa (p. ej. cáncer de pulmón) tienen muy pocos casos; no se incluyen en el taller.
- **Cifras de referencia:** la prevalencia de 32,5% parece coherente con la publicada para la ENS 2016-17, pero **no se verificó**
  contra el informe oficial.
- El ejercicio con la ENS 2003 muestra resultados distintos (HR ajustado 1,24, no significativo, con 20 años de seguimiento);
  útil como discusión de sesgos, no incluida en los cuadernos.

## 9. Extensiones para quien termine antes
- Repetir con otra variable de resultado (hipertensión, diabetes, obesidad).
- Cambiar la definición de «fumador pasivo» y comparar.
- Analizar por sexo o por zona.
- Contrastar con la ENS 2009-10 y 2003 (misma base de mortalidad, otros `.sav`).
- Hospitalizaciones: la base **«ENS con egresos hospitalarios»** ([minuta](https://epi.minsal.cl/bases-de-datos/)) permite estudiar ingresos por causa.

## 10. Para publicar (conversación final)
- Redactar el protocolo y el plan de análisis **antes** de mirar los resultados.
- Reportar con la lista **STROBE** (cohortes).
- Consultar al comité de ética de la institución: son datos anónimos y públicos, pero muchas instituciones piden una constancia.
- Condiciones de uso del Minsal: solo investigación, citar la fuente y enviar copia de la publicación.
