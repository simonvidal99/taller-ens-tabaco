# Tutorial: conseguir los datos y cargarlos en el cuaderno

Los datos **no vienen con el cuaderno**: hay que bajarlos del Minsal, abrir el archivo comprimido y dejar el `.sav` donde el cuaderno lo busca.
Tiempo estimado: 10 minutos. Hazlo **antes del taller**.

**Qué vas a tener al final:** un archivo llamado exactamente

`Base de datos Encuesta Nacional de Salud 2016-2017(ENS)+DEF2023.sav` (unos 34 MB)

## Paso 1. Descargar el archivo

1. Entra a [epi.minsal.cl/bases-de-datos](https://epi.minsal.cl/bases-de-datos/).
2. Busca la base **«ENS + Defunción (Mortalidad) 2023»** y descárgala. Pesa unos 6 MB.
   Enlace directo (puede cambiar con el tiempo): <https://epi.minsal.cl/wp-content/uploads/2026/07/Base_ENS_Mortalidad_2023.zip>
3. Se guarda como `Base_ENS_Mortalidad_2023.zip`, normalmente en la carpeta *Descargas*.

> Condiciones de uso del Minsal: solo para investigación, citar la fuente y enviar copia de las publicaciones ([condiciones](https://epi.minsal.cl/condiciones-de-uso/)).

## Paso 2. Abrir el archivo (la parte que más confunde)

**Aunque se llama `.zip`, en realidad es un archivo RAR.** El descompresor normal de Windows o Mac puede fallar o decir que el archivo está dañado. No lo está: necesitas un programa que abra RAR.

| Sistema | Qué hacer |
|---|---|
| **Windows** | Instala [7-Zip](https://www.7-zip.org/) (gratis). Clic derecho sobre el archivo → *7-Zip* → *Extraer aquí*. |
| **Mac** | Instala [The Unarchiver](https://theunarchiver.com/) (gratis, en la App Store). Doble clic sobre el archivo. |
| **Linux** | `sudo apt install unrar` o `7z x Base_ENS_Mortalidad_2023.zip`. |

Dentro hay **tres** archivos `.sav`, uno por encuesta:

| Archivo (empieza con) | Encuesta | ¿Lo usamos? |
|---|---|---|
| `ENS_2003_...` | ENS 2003 | No |
| `ENCUESTA NACIONAL DE SALUD-ENS 2009-2010...` | ENS 2009-10 | No |
| **`Base de datos Encuesta Nacional de Salud 2016-2017(ENS)+DEF2023.sav`** | **ENS 2016-17** | **Sí** |

## Paso 3. Dejar el archivo donde el cuaderno lo busca

El cuaderno busca el archivo en esta ruta, **relativa a donde está el cuaderno**:

```
datos/Base de datos Encuesta Nacional de Salud 2016-2017(ENS)+DEF2023.sav
```

Elige **una** de estas dos opciones.

### Opción A: Google Colab (sin instalar nada)

1. Abre el cuaderno de participantes directamente desde GitHub:
   <https://colab.research.google.com/github/simonvidal99/taller-ens-tabaco/blob/main/taller/taller_tabaco_PARTICIPANTES.ipynb>
   (necesitas una cuenta de Google).
2. En el panel izquierdo, haz clic en el icono de la **carpeta** (*Archivos*).
3. Arrastra el `.sav` de 2016-17 hasta ese panel, o usa el botón de **subir** (flecha hacia arriba).
   Espera a que termine la barra de progreso (son 34 MB).
4. En la celda que define `RUTA` (la segunda del cuaderno), cambia la línea por:

   ```python
   RUTA = Path("/content/Base de datos Encuesta Nacional de Salud 2016-2017(ENS)+DEF2023.sav")
   ```
5. Ejecuta esa celda: debe mostrar `True`.

> **Ojo:** en Colab los archivos subidos **se borran** cuando la sesión se cierra o se reinicia. Si te desconectas, hay que subir el archivo otra vez.

### Opción B: Python en tu computador

1. Descarga el material: en [el repositorio](https://github.com/simonvidal99/taller-ens-tabaco) haz clic en **Code → Download ZIP** y descomprímelo.
2. Copia el `.sav` dentro de la carpeta `taller/datos/` del material descargado.
3. Instala las librerías (en una terminal) y abre Jupyter:

   ```bash
   pip install pandas numpy scipy pyreadstat lifelines matplotlib jupyter
   ```
   ```bash
   jupyter notebook
   ```
4. Abre `taller/taller_tabaco_PARTICIPANTES.ipynb`. No hay que cambiar la ruta, siempre que el `.sav` esté en `taller/datos/`.

## Paso 4. Comprobar que funciona

Ejecuta las dos primeras celdas del cuaderno. La segunda termina con `RUTA.exists()` y debe mostrar:

```
True
```

Luego ejecuta la celda de la sección 1. Debe imprimir, entre otras cosas, **6233** personas encuestadas y **539** fallecidos hasta 2023. Si esos números coinciden, estás listo.

## Si algo falla

| Síntoma | Causa probable | Solución |
|---|---|---|
| El `.zip` no se abre o dice «dañado» | Es un RAR | Usa 7-Zip o The Unarchiver (paso 2) |
| `RUTA.exists()` muestra `False` o aparece `FileNotFoundError` | El archivo no está en la carpeta correcta, o su nombre no coincide | Revisa que esté en `datos/` (o en `/content/` en Colab) y que el nombre sea idéntico, incluidos los paréntesis y el `+DEF2023` |
| En Colab funcionaba y ahora no | La sesión se reinició y se borró el archivo | Súbelo otra vez |
| `ModuleNotFoundError: No module named 'pyreadstat'` (o `lifelines`) | Faltan librerías | Ejecuta la primera celda del cuaderno, o `pip install pyreadstat lifelines` |
| Aparecen tres `.sav` y no sé cuál es | Cada uno es una encuesta distinta | Usa el que contiene `2016-2017` |
| La descarga da error 404 | El Minsal cambió el enlace | Entra a [epi.minsal.cl/bases-de-datos](https://epi.minsal.cl/bases-de-datos/) y busca la base «ENS + Defunción (Mortalidad) 2023» |

## Referencia

Ministerio de Salud de Chile, Departamento de Epidemiología. *Encuesta Nacional de Salud 2016-2017*, base de datos y manual de uso.
<https://epi.minsal.cl/bases-de-datos/>
