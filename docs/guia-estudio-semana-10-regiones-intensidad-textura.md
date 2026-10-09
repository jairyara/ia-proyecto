# Guía de estudio y sustentación — Semana 10

**Tema:** regiones, histogramas de intensidad y textura LBP en imágenes de paquetes.  
**Propósito:** explicar **lo implementado en el proyecto**, sus decisiones y sus límites; no sustituir la explicación general de la guía de clase.  
**Código principal:** [`src/semana10_texturas.py`](../src/semana10_texturas.py). **Resultados:** [`reports/semana10.md`](../reports/semana10.md).

## La idea en 30 segundos

Tomamos las vistas laterales del piloto sintético auditado. De cada imagen de **entrenamiento** obtenemos un vector de 53 números: **3 medidas de regiones**, **32 probabilidades de intensidad** y **18 probabilidades de textura LBP**. Comparamos descriptivamente las etiquetas conocidas `danado` e `intacto`. **No se entrena un clasificador, no se predice el estado de un paquete y no se toma una decisión de despacho.**

## Secuencia del proyecto: qué entra, qué sale y por qué

| Paso | En el código | Qué debemos decir al sustentarlo |
|---|---|---|
| 1. Inventario y partición | `preparar_piloto(raiz)` en `src/vision/particion.py`; manifiesto `data/manifests/piloto-visual-v1.json` | Se reutiliza la partición por `grupo_origen` de Semana 8: 150 imágenes para entrenamiento y 50 reservadas. El helper audita las 200 para reconstruirla; **solo las 150 de entrenamiento reciben descriptores de Semana 10**. Así evitamos mirar el conjunto de prueba durante esta exploración. |
| 2. Lectura | `leer_gris(ruta)` | Valida que el original sea PNG RGB de 960×540; lo convierte a gris `uint8` y 480×270 con Lanczos. No modifica el original. El 16×16 de Semana 8 era para el MLP; aquí se conserva más detalle local para LBP. |
| 3. Regiones | `threshold_otsu`, `gris > umbral`, `measure.label(..., connectivity=2)`, `regionprops` | Otsu elige un umbral global; la máscara selecciona píxeles claros. `connectivity=2` en 2D considera ocho vecinos. El filtro **`area > 50`** descarta componentes pequeños a esta resolución; no es un tamaño físico ni una prueba de daño. |
| 4. Intensidad | `np.histogram(..., bins=32, range=(0, 256)) / gris.size` | Cuenta píxeles en 32 intervalos de ancho 8; cada valor es una proporción y el bloque suma 1. Mide la distribución de tonos de **toda la escena**, no solo del cartón. |
| 5. Textura | `local_binary_pattern(gris, 16, 2, method="uniform")`; `np.bincount(...)` | LBP compara patrones locales de vecindad. Con `P=16` y método uniforme se agrupa en 18 categorías (`P+2`); normalizamos para que el bloque sume 1. También incluye banda y fondo. |
| 6. Vector y evidencia | `np.concatenate`, `np.stack`, `np.save`, JSON, PNG | Por imagen: **3 + 32 + 18 = 53** valores. La matriz es **150×53**, en el orden de `ids_entrenamiento` del JSON. Las etiquetas e IDs **no** son columnas del vector. |
| 7. Publicación | `api/routers/vision_semana10.py`; `Semana10View.jsx` y `Semana10Charts.jsx` | La extracción es offline. La API solo lee evidencias y verifica hashes; Órbita muestra imagen y máscara de cada caso y permite **Ambos / Dañado / Intacto**. Abrir el dashboard no vuelve a calcular descriptores. |

### El vector, sin confundir sus bloques

```text
índices 0–2    área media / píxeles, desviación de área / píxeles, n.º de regiones válidas
índices 3–34   32 probabilidades de intensidad
índices 35–52  18 probabilidades de LBP uniforme
```

Las áreas están expresadas como **fracción del área de la imagen**; el conteo de regiones queda separado porque no tiene la misma unidad. Un vector con tres ceros al inicio puede significar **sin regiones válidas**; no significa «intacto». El JSON conserva la bandera `sin_regiones_validas` para evitar esa lectura.

## Decisiones diferentes de la práctica de clase

1. **Una observación logística coherente.** La guía docente ilustra regiones/intensidad con monedas y textura con ladrillos. Aquí calculamos los tres bloques sobre **la misma vista lateral de un paquete** para que cada fila represente una sola observación trazable.
2. **Un conjunto auditado y una partición protegida.** No elegimos dos imágenes a conveniencia ni usamos los 50 casos reservados para decidir si el descriptor «funciona». La comparación por clase es descriptiva sobre entrenamiento y no es una evaluación independiente.
3. **Probabilidades, no densidad de histograma.** La opción `density=True` de NumPy normaliza el **área** del histograma; con bins de ancho 8, sus alturas no suman 1. Aquí dividimos los conteos por el número de píxeles para obtener probabilidades cuya suma sí es 1.
4. **Sin máscara inventada del paquete.** Otsu no conoce la semántica de la escena: también resalta partes de la banda transportadora. Como no tenemos una ROI o máscara de verdad terreno fiable para estos originales, los histogramas y LBP abarcan toda la imagen y se declara esa contaminación.
5. **Separación entre experimento y operación.** Los artefactos versionados y sus hashes hacen reproducible la consulta; no convierten el descriptor en detector ni lo conectan con reglas de rechazo, cuarentena o despacho.

## Qué resultados sí se pueden defender

En las 150 imágenes analizadas hay 75 por clase. Las medianas de regiones válidas son **33** (`danado`) y **34** (`intacto`); las medianas del área media son **1,5138 %** y **1,4698 %** de la imagen. Estas cifras cercanas **no demuestran separación de clases**. En los dos ejemplos visuales, la máscara revela componentes de la banda, no solo del paquete.

La prueba exploratoria de sumar **20 niveles de gris** a esos dos ejemplos dejó igual el conteo de regiones válidas, mientras el histograma de intensidad cambió notablemente y LBP muy poco. Es evidencia **para dos imágenes y una perturbación artificial**, no una prueba de robustez frente a cámaras o iluminación real. Los detalles numéricos y la figura están en el [informe](../reports/semana10.md).

**Siguiente paso defendible:** delimitar el paquete con ROI o máscaras anotadas; controlar cambios de iluminación y fondo; y solo después definir un clasificador y evaluarlo en los 50 casos reservados. No afirmar una mejora respecto al MLP de Semana 8: aquel obtuvo `accuracy=0,48` frente a una línea base de `0,50`, y Semana 10 todavía no tiene métrica de clasificación.

## Python y NumPy que sí conviene saber explicar

No hay una sintaxis nueva que sea el centro de la semana. Estos detalles importan porque afectan el resultado o la lectura del código:

| Expresión real | Explicación puntual | Error habitual |
|---|---|---|
| `def extraer_caracteristicas(gris, *, area_minima=AREA_MINIMA)` | El `*` obliga a escribir `area_minima=...` al llamar la función; evita confundir el parámetro con otro argumento posicional. | Creer que el `*` multiplica o desempaqueta aquí. |
| `gris.dtype == np.uint8`, `gris.ndim == 2` | `uint8` es entero sin signo de 0 a 255; `ndim == 2` exige una matriz en gris, no RGB de tres canales. El contrato se comprueba antes de Otsu y LBP. | Pasar flotantes 0–1 o una imagen RGB y asumir que producen el mismo descriptor. |
| `mascara = gris > umbral` | Comparación vectorizada: devuelve una matriz booleana de igual tamaño. `measure.label` agrupa sus píxeles verdaderos; no «reconoce paquetes». | Interpretar `True` como «dañado». |
| `areas = np.asarray([...], dtype=np.float64)` | Una comprensión selecciona `region.area > area_minima`; `np.asarray` permite calcular media/desviación numéricas y controlar el tipo. | Confundir `regiones_totales` con las que sobreviven al filtro. |
| `if areas.size else 0.0` | Evita calcular media/desviación de un arreglo vacío (que darían valores no finitos). La bandera del JSON conserva el significado de ese cero. | Concluir que cero equivale a clase intacta. |
| `np.histogram(...)[0] / gris.size` | `[0]` toma los conteos, no los bordes de los intervalos; dividir por todos los píxeles convierte conteos en proporciones. | Decir que se usó `density=True` o que 32 bins son 32 imágenes. |
| `lbp.astype(np.int64).ravel()` y `np.bincount(..., minlength=18)` | `ravel()` aplana la imagen de códigos LBP a un vector; `bincount` cuenta cada categoría y `minlength` conserva las 18 posiciones aunque alguna no aparezca. | Pensar que `ravel()` altera el original o que `minlength` elimina códigos extra; el código verifica luego la longitud. |
| `vector[3:35]`, `vector[35:]` | Los *slices* terminan **antes** del índice final: 3–34 son intensidad y 35–52 son LBP. | Incluir el índice 35 en el primer bloque. |
| `np.clip(gris.astype(np.int16) + 20, 0, 255).astype(np.uint8)` | Antes de sumar se amplía a `int16` para evitar desbordamiento de `uint8`; luego se limita al rango válido y se vuelve a `uint8`. | Hacer `gris + 20` directamente y aceptar resultados que den la vuelta por encima de 255. |
| `np.stack(matriz)`, `np.save(vectores, datos)` | `stack` une 150 vectores 53D en una matriz 150×53; `.npy` conserva la estructura numérica. La correspondencia con IDs está en el JSON. | Suponer que la matriz contiene etiquetas o que la fila se puede interpretar sin el orden de IDs. |
| `sha256(ruta.read_bytes()).hexdigest()` | El hash identifica el contenido exacto de un archivo. Se compara antes de extraer y al servir evidencias. | Confundir integridad/reproducibilidad con precisión del método. |

**Para ubicar la carga:** `ejecutar()` llama a `preparar_piloto()`, recorre `indices_train`, busca cada ruta segura y la pasa a `leer_gris()`. El cálculo empieza en `extraer_caracteristicas()`. El bloque `if __name__ == "__main__": main()` solo ejecuta el CLI cuando se invoca `python -m src.semana10_texturas`; importar el módulo no dispara la extracción.

## Downsampling con Lanczos: por qué y cómo funciona

* **Qué es matemáticamente:** `Image.Resampling.LANCZOS` es un filtro de remuestreo basado en la función sinc cardinal ventana (`sinc(x) · sinc(x/a)` con radio de ventana $a=3$, evaluando vecindades de $8 \times 8$). En procesamiento de señales es el filtro pasabajas ideal que aproxima el teorema de Nyquist-Shannon.
* **Por qué se eligió frente a otros:**
  * *Nearest Neighbor (Vecino más cercano):* introduce bordes dentados y efecto escalera (*aliasing*).
  * *Bilineal:* atenúa y difumina micro-contrastes.
  * *Bicúbica:* suaviza texturas sutiles.
  * *Lanczos:* elimina altas frecuencias que generarían patrones falsos de Moiré pero **retiene la máxima nitidez de bordes y micro-textura**.
* **Por qué 480×270 y no 16×16:** En Semana 8, el MLP requería un vector plano pequeño de $16 \times 16$. En Semana 10, **LBP compara píxeles a radio $R=2$**; comprimir a $16 \times 16$ destruiría la rugosidad del cartón corrugado y los bordes finos. Reducir a la mitad ($480 \times 270$) con Lanczos preserva la textura local minimizando costo computacional.

## Lectura correcta de los histogramas en el Dashboard (Órbita)

En la vista de Semana 10 (`Semana10Charts.jsx`), los histogramas interactivos de Nivo comparan los dos casos auditados (🔴 Dañado / 🟢 Intacto):

1. **Histograma de intensidad (Curvas continuas de 32 bins):**
   * **Eje X (0 a 256):** Tonalidades agrupadas en 32 intervalos de ancho 8. La izquierda ($0-64$) representa zonas oscuras/sombras; el centro ($64-192$) representa el cartón y la banda; la derecha ($192-256$) representa reflejos y etiquetas.
   * **Eje Y:** Probabilidad (proporción de píxeles en ese intervalo). **Cada curva individual suma exactamente 1.0**.
   * **Interpretación rigurosa:** Un ligero desplazamiento horizontal entre curvas refleja ligeras variaciones de iluminación o encuadre de la toma sintética, **no la presencia o ausencia de un daño físico**.
2. **Patrones locales LBP (Barras de 18 categorías):**
   * **Eje X (0 a 17):** Categorías de micro-textura. Los índices $0$ a $16$ son los patrones uniformes ordenados por número de transiciones y densidad de unos; el índice $17$ es la categoría general de **patrones no uniformes (ruido / micro-rugosidad irregular)**.
   * **Eje Y:** Probabilidad. El conjunto de 18 barras de cada clase suma **exactamente 1.0**.
   * **Interpretación rigurosa:** La similitud de alturas entre las barras rojas y verdes evidencia visualmente por qué el descriptor global no separa clases: el cartón y la banda transportadora cubren más del 90% de los píxeles en ambas imágenes, enmascarando cualquier rasgadura puntual.

## Tarjeta de bolsillo: Respuestas ejecutivas y trampas de sustentación

Para presentar ante directores, stakeholders o evaluadores técnicos con alta síntesis y rigor metodológico:

| Pregunta de sustentación | Trampa común | Respuesta ejecutiva rigurosa |
|---|---|---|
| **¿Por qué 150 y no las 200 imágenes?** | Decir que las 50 de prueba «se procesaron igual» o se ignoraron. | **Gobierno y rigor metodológico:** Las 50 imágenes son el 25% de prueba reservada. Se auditan para certificar integridad, pero se guardan en «caja fuerte» sin extraer descriptores para evitar **fuga de datos (data leakage)**. Solo usamos las 150 de entrenamiento para explorar métricas. |
| **¿Una región válida equivale a un daño o rasgadura?** | Responder que sí (llevaría al absurdo de que los intactos tienen 34 «daños»). | **Rotundamente no:** Es cualquier mancha de píxeles claros $>50\text{ px}$ que supera el umbral Otsu. La mayoría son rodillos metálicos de la banda y etiquetas. Otsu no tiene semántica de avería. |
| **¿Por qué 8 vecinos (`connectivity=2`)?** | Confundirlo con el radio $R=2$ de LBP. | **Continuidad morfológica:** 8 vecinos evalúa los 4 lados y las 4 diagonales. Con 4 vecinos, cualquier trazo o rasgadura diagonal se fragmentaría artificialmente en micro-pedazos inconexos. Con 8 se preserva la unidad natural del componente. |
| **¿Por qué dividir entre `gris.size` y no usar `density=True`?** | Decir que `density=True` daba error. | **Probabilidades discretas que sumen 1.0:** `density=True` normaliza el área geométrica continua; con bins de ancho 8, las barras habrían sumado $1/8 = 0.125$. Dividir los conteos entre el total de píxeles produce probabilidades puras y comparables. |
| **¿Qué diferencias hubo entre clases y cómo impacta el despacho?** | Vender falsas diferencias o asegurar que el sistema detecta daños. | **Cero automatización en despacho:** Las medianas son casi idénticas (33 vs 34 regiones; 1.51% vs 1.47% de área) porque la banda contamina la escena. La inspección humana sigue siendo obligatoria. El paso técnico indispensable es aislar el paquete (ROI) antes de entrenar un clasificador. |
| **¿Por qué 480×270 y no 16×16? ¿Superaron la precisión de Semana 8?** | Decir que aumentó la precisión o accuracy. | **Resolución para textura y honestidad de alcance:** LBP requiere vecindad local a radio 2; a $16 \times 16$ se destruiría la rugosidad del cartón. Además, **no medimos precisión porque no hay clasificador entrenado**; Semana 10 es ingeniería de características explicables, no un modelo predictivo. |

## Preguntas de práctica para responder puntual

1. **¿Cuál es el resultado real de Semana 10?** Un descriptor explicable 53D por cada una de 150 imágenes de entrenamiento, evidencia visual y resumen descriptivo; no un detector.
2. **¿De dónde salen las imágenes y dónde se cargan?** Del piloto sintético auditado de 200 originales indicado en el manifiesto; `preparar_piloto()` fija la partición y `leer_gris()` abre cada PNG seleccionado para entrenamiento.
3. **¿Se procesan los 50 casos de prueba?** Se auditan al reconstruir la partición, pero no reciben descriptores de Semana 10 ni entran en resúmenes o ejemplos.
4. **¿Por qué no usamos los mismos `16×16` del MLP?** Reducir tanto la imagen destruiría detalle local útil para textura; Semana 10 usa 480×270 con Lanczos.
5. **¿Qué entrega Otsu exactamente?** Un umbral global de intensidad; al aplicar `gris > umbral` se obtiene una máscara de píxeles claros, no una máscara semántica de daño.
6. **¿Qué significan ocho vecinos?** Al etiquetar en 2D, se consideran los cuatro vecinos ortogonales y los cuatro diagonales para decidir continuidad de una región.
7. **¿Una región válida es un paquete o una rasgadura?** No. Es un componente conectado de la máscara con área mayor de 50 píxeles; puede provenir de cartón, etiqueta, banda o fondo.
8. **¿Por qué dividir las áreas por `gris.size`?** Para expresarlas como fracción de la superficie de análisis y reducir la dependencia directa del número de píxeles.
9. **¿Por qué intensidad y LBP se calculan sobre toda la imagen?** No hay una ROI de paquete fiable anotada; recortar con Otsu fingiría una segmentación semántica que no tenemos.
10. **¿Qué significa `53D` y dónde están las clases?** Son 3 valores de regiones + 32 de intensidad + 18 de LBP. Las clases están en el manifiesto/JSON para comparar; no en el vector.
11. **¿Qué diferencia hay entre `density=True` y nuestra normalización?** `density=True` hace que el área bajo el histograma sea 1; dividir conteos por píxeles hace que las 32 alturas sumen 1.
12. **¿Qué pasaría si se elimina el filtro de área o se cambia `P=16`?** Cambiarían las regiones válidas; al cambiar `P` cambia el número de categorías LBP y el esquema 53D, por lo que habría que versionar/recalcular contrato, artefactos y consumidores.
13. **¿Qué indican las medianas 33 y 34?** Que este conteo luce muy parecido entre clases; por sí solo no justifica clasificación de daños.
14. **¿La estabilidad de LBP ante `+20` demuestra robustez?** No; es una prueba controlada en dos ejemplos, insuficiente para afirmar comportamiento ante variaciones reales.
15. **¿Para qué sirven el JSON, `.npy`, PNG y hashes?** El JSON documenta configuración, IDs y métricas; `.npy` guarda la matriz; PNG permite inspección visual; los hashes comprueban integridad, no validez predictiva.
16. **¿Qué responder si preguntan si el sistema ya decide despacho?** No. Primero necesitamos segmentar el paquete de forma fiable y validar un clasificador en datos reservados y, posteriormente, representativos de operación real.
