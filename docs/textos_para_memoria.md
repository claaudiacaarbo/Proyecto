# Textos listos para pegar en la memoria

## 5.3 Limpieza y transformacion de datos

Para preparar la base de datos, partimos del archivo `ai_impact_jobs_2010_2025.csv`. Primero cargamos el conjunto de datos en Python mediante la libreria Pandas. Despues eliminamos posibles registros duplicados para evitar que una misma oferta tuviera mas peso dentro del analisis.

Tambien revisamos los valores nulos de las variables principales. En el caso de `salary_usd`, imputamos los valores faltantes utilizando la mediana salarial de cada industria. Elegimos la mediana porque es una medida robusta ante valores extremos. Si una industria no tenia suficientes datos para calcular esa mediana, aplicamos la mediana general del conjunto de datos. Aplicamos el mismo criterio a `automation_risk_score`, ya que esta variable era necesaria para el analisis del riesgo de automatizacion.

Para la variable `ai_skills`, sustituimos los valores vacios por la etiqueta `Not Specified`. De esta forma diferenciamos entre una oferta que no declara habilidades de IA y una oferta con datos perdidos. Despues, para analizar las competencias individuales, separamos el texto de `ai_skills` mediante `split`. A continuacion usamos `explode` para convertir cada habilidad en una fila independiente. Esto nos permitio contar competencias como Machine Learning, NLP, MLOps, Deep Learning o LLMs de forma separada.

Por ultimo, eliminamos los valores atipicos de `salary_usd` mediante el metodo del rango intercuartilico. Calculamos el primer cuartil, el tercer cuartil y el IQR. Despues conservamos solo los registros situados dentro del intervalo valido. Con este proceso evitamos que salarios anormalmente altos o bajos distorsionaran las medias y las correlaciones.

## 6.1 Metodologia

Nuestra metodologia combina limpieza estadistica, segmentacion y analisis exploratorio. Primero calculamos indicadores descriptivos. Despues agrupamos los datos por año, industria, nivel profesional y tamaño de empresa. Finalmente, generamos tablas y graficos para interpretar los resultados.

Para eliminar outliers usamos la siguiente formula:

`IQR = Q3 - Q1`

`limite inferior = Q1 - 1,5 * IQR`

`limite superior = Q3 + 1,5 * IQR`

Solo mantuvimos los registros cuyo salario estaba dentro de ese intervalo.

Para estudiar la relacion entre intensidad de IA y salario aplicamos la correlacion de Pearson. La formula utilizada fue:

`r = cov(X,Y) / (desv(X) * desv(Y))`

En nuestro caso, `X` representa `ai_intensity_score` e `Y` representa `salary_usd`. El resultado obtenido fue positivo. Esto indica que, dentro del dataset, las ofertas con mayor intensidad de IA tienden a asociarse con salarios mas altos. Aun asi, interpretamos este resultado como una asociacion estadistica, no como una prueba de causalidad.

Tambien calculamos el salario medio por año mediante una agrupacion por `posting_year`. Para identificar las industrias con mayor riesgo, agrupamos por `industry` y calculamos la media de `automation_risk_score`. Despues ordenamos los resultados de mayor a menor y seleccionamos el Top 5.

Ademas, comparamos el riesgo de desplazamiento laboral cruzando `ai_job_displacement_risk` con `seniority_level`. Esto nos permitio observar si los perfiles junior, mid, senior, lead o executive presentaban distribuciones diferentes de riesgo. Finalmente, calculamos el porcentaje de registros con `reskilling_required = True` para medir la necesidad de reciclaje profesional.

## 6.2 Herramientas

Todo el procesamiento tecnico se realizo con Python. Usamos Pandas para cargar, limpiar, transformar y agrupar los datos. Usamos NumPy para apoyar los calculos numericos. Tambien preparamos el proyecto para generar graficos con Matplotlib y WordCloud.

El codigo final esta organizado en el script `src/analysis_pipeline.py`. Este archivo permite reproducir el proceso completo desde la base original hasta los resultados finales. El script genera una base limpia revisada, tablas CSV, graficos y un resumen tecnico.

El entorno de desarrollo utilizado fue Jupyter Notebook durante la fase exploratoria y un script Python estructurado durante la fase final. Esta combinacion nos permitio experimentar primero con los datos y despues dejar una version ordenada para GitHub.

## 7.1 Uso de otro conjunto de datos. Encuestas.

En esta version del proyecto no hemos incorporado encuestas propias. El alcance del trabajo es teorico y analitico. Por tanto, no realizamos trabajo de campo con usuarios.

Para reforzar la fiabilidad del analisis, validamos los resultados comparando la base original `ai_impact_jobs_2010_2025.csv` con la base limpia generada por nuestro pipeline, `outputs/ai_impact_jobs_2010_2025_GOLD_REVISED.csv`. Esta comparacion nos permitio comprobar que las tendencias principales se mantenian despues de limpiar nulos y eliminar outliers.

Tambien conservamos todas las industrias en la version revisada de la base limpia. Esta decision mejora la representatividad respecto a la primera version GOLD, que solo mantenia las cinco industrias mas frecuentes.

Importante: si el tribunal exige obligatoriamente un segundo dataset externo, este apartado deberia completarse con una fuente adicional real. En ese caso, no conviene presentar la base original y la base limpia como si fueran dos datasets independientes.

## 7.2 Aplicacion desarrollada

El despliegue del proyecto no consiste en una aplicacion movil ni en una pagina web comercial. Nuestro producto final es un repositorio publico con codigo reproducible en Python.

En el repositorio hemos organizado los scripts necesarios para limpiar la base de datos, calcular los indicadores principales y generar las visualizaciones. El archivo principal es `src/analysis_pipeline.py`. Este script parte del dataset original `ai_impact_jobs_2010_2025.csv` y genera automaticamente la base limpia revisada, las tablas de resultados y los graficos finales.

El repositorio permite que el profesor y el tribunal auditen el proceso completo. Tambien permite ejecutar de nuevo el analisis en otro ordenador siguiendo las instrucciones del archivo `README.md`.

Enlace al repositorio:

https://github.com/claaudiacaarbo/Proyecto

## Cambios recomendados en la memoria actual

- Sustituir las notas internas de Claudia y Aaron por los textos anteriores.
- Evitar afirmar que se ha usado un segundo dataset externo si todavia no existe.
- Cambiar "aplicacion desarrollada" por "repositorio reproducible" o "pipeline de analisis", porque el producto real es codigo, no una app.
- Indicar que la correlacion no implica causalidad.
- Revisar la conclusion que dice que hemos comprobado la vulnerabilidad de los perfiles junior. Esa afirmacion solo debe mantenerse si la tabla por `seniority_level` lo demuestra claramente.
