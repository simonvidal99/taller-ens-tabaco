# Scripts de análisis

Scripts en Python usados para generar los resultados de `analisis/`, los gráficos y los cuadernos del taller.

| Script | Qué hace |
|---|---|
| `prev2.py` | Prevalencias ponderadas de condiciones crónicas, ENS 2003 |
| `surv.py` | Supervivencia (Cox) y tabaco, ENS 2003 + defunciones |
| `surv17.py` | Supervivencia (Cox) y tabaco, ENS 2016-17 + defunciones |
| `prev17.py` | Prevalencia de fumadores y fumadores pasivos (con diseño muestral) y mortalidad por exposición pasiva, ENS 2016-17 |
| `figs.py` | Gráficos de la presentación |
| `build_nb.py` | Genera los dos cuadernos de `taller/` |

**Ojo:** las rutas de archivos están escritas para el equipo donde se hicieron (`/Users/simonvidal/...`).
Hay que editarlas antes de ejecutar. Dependencias: `pandas numpy scipy pyreadstat lifelines matplotlib nbformat`.
