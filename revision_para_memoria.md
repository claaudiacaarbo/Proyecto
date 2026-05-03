# Revision del proyecto para la memoria

## 1. Vision general del proyecto

El proyecto analiza la evolucion del empleo ante la inteligencia artificial entre 2010 y 2025 a partir de una base de datos de ofertas laborales. El flujo de trabajo tiene dos fases principales:

1. Limpieza y preparacion de datos: se parte de `ai_impact_jobs_2010_2025.csv` y se genera una version limpia llamada `ai_impact_jobs_2010_2025_GOLD.csv`.
2. Analisis exploratorio: se estudian la presencia de IA en las ofertas, la intensidad de IA, las habilidades mas demandadas, el reskilling y el riesgo de automatizacion.

Archivos principales:

- `ai_impact_jobs_2010_2025.csv`: base original, con 5000 registros y 22 columnas.
- `ai_impact_jobs_2010_2025_GOLD.csv`: base limpia, con 2830 registros y las mismas 22 columnas.
- `Aaron_Data_Cleaning_Prototype.ipynb`: notebook de limpieza de datos.
- `Claudia Proyecto.ipynb`: analisis de habilidades de IA, evolucion de skills y reskilling.
- `Codigo Pau.ipynb`: evolucion temporal de la intensidad de IA y del porcentaje de ofertas que mencionan IA.
- `Codigos graficas rstudio IÑAKI (1).Rmd`: graficos de riesgo alto de automatizacion por empresa, puesto e industria.
- `Codigo Roger`: analisis regional de intensidad de IA, salario y correlaciones.

## 2. Base de datos

La base original contiene 5000 filas. Las columnas mas relevantes para la memoria son:

- `posting_year`: año de la oferta.
- `country`, `region`, `city`: localizacion.
- `company_size`, `industry`, `job_title`, `seniority_level`: caracteristicas de la oferta.
- `ai_mentioned`: indica si la oferta menciona IA.
- `ai_keywords`, `ai_skills`: terminos y habilidades relacionadas con IA.
- `ai_intensity_score`: intensidad de IA de la oferta.
- `salary_usd`: salario en dolares.
- `automation_risk_score`: puntuacion de riesgo de automatizacion.
- `reskilling_required`: necesidad de reciclaje profesional.
- `ai_job_displacement_risk`: categoria de riesgo de desplazamiento laboral.
- `industry_ai_adoption_stage`: fase de adopcion de IA del sector.

En la base original se detectan 3377 valores vacios en `ai_keywords` y 3377 valores vacios en `ai_skills`. En la base limpia, `ai_skills` se rellena con `Not Specified`, pero `ai_keywords` conserva 1945 vacios. Esto es coherente si esos registros corresponden a ofertas donde no se menciona IA.

La base limpia no contiene duplicados por `job_id`.

## 3. Limpieza realizada

El notebook de Aaron realiza las siguientes operaciones:

- Elimina duplicados.
- Imputa salarios faltantes usando la mediana por industria y, si todavia quedan nulos, la mediana global.
- Sustituye valores vacios de `ai_skills` por `Not Specified`.
- Elimina outliers salariales mediante el metodo IQR.
- Conserva solamente las cinco industrias mas frecuentes.
- Exporta el resultado como `ai_impact_jobs_2010_2025_GOLD.csv`.

Punto importante para la memoria: al conservar solo las cinco industrias mas frecuentes, se excluyen sectores como Finance, Government, Education y Energy. Esto debe mencionarse como decision metodologica y limitacion, porque los resultados finales se interpretan sobre Tech, Manufacturing, Agriculture, Retail y Healthcare.

## 4. Resultados descriptivos principales

En la base limpia:

- Filas: 2830.
- Columnas: 22.
- Periodo cubierto: 2010-2025.
- Salario medio: 62 344,58 USD.
- Rango salarial: 15 321-148 141 USD.
- Intensidad media de IA: 0,280.
- Riesgo medio de automatizacion: 0,593.

Distribucion por industria:

- Tech: 573 registros.
- Manufacturing: 569 registros.
- Agriculture: 567 registros.
- Retail: 564 registros.
- Healthcare: 557 registros.

Distribucion por tamaño de empresa:

- Small: 578.
- Enterprise: 570.
- Startup: 562.
- Medium: 561.
- Large: 559.

## 5. Evolucion temporal de la IA en las ofertas

El notebook de Pau muestra una tendencia creciente clara:

- En 2010, el 9,8% de las ofertas mencionaban IA.
- En 2018, el porcentaje sube al 38,0%.
- En 2022, alcanza el 59,4%.
- En 2024, llega al maximo observado: 70,3%.
- En 2025, baja ligeramente al 62,6%.

La intensidad media de IA tambien aumenta:

- 2010: 0,154.
- 2014: 0,192.
- 2018: 0,321.
- 2022: 0,440.
- 2024: 0,509.
- 2025: 0,444.

Interpretacion para la memoria: los datos apoyan que la IA gana peso progresivamente en el mercado laboral, especialmente a partir de 2018 y con un salto notable desde 2022.

## 6. Habilidades de IA mas demandadas

El notebook de Claudia identifica el ranking de habilidades de IA:

- reinforcement learning: 325.
- NLP: 323.
- MLOps: 318.
- deep learning: 307.
- computer vision: 302.
- machine learning: 287.
- generative AI: 188.
- LLMs: 164.

Comparacion temporal:

Top 5 en 2010:

- reinforcement learning: 8.
- computer vision: 7.
- NLP: 7.
- MLOps: 6.
- deep learning: 6.

Top 5 en 2025:

- NLP: 40.
- computer vision: 33.
- reinforcement learning: 33.
- deep learning: 32.
- LLMs: 32.

Interpretacion para la memoria: se observa continuidad en habilidades clasicas como NLP, computer vision y deep learning, pero en 2025 aparece con fuerza `LLMs`, lo que refleja el impacto reciente de los modelos de lenguaje.

## 7. Reskilling

El analisis de Claudia obtiene:

- 31,3% de ofertas con `reskilling_required = True`.
- 68,7% de ofertas con `reskilling_required = False`.

Advertencia metodologica importante: en la base limpia, `reskilling_required` coincide exactamente con `ai_mentioned`. Hay 885 ofertas con ambas variables en True y 1945 con ambas en False. Por tanto, no conviene presentar el reskilling como una variable totalmente independiente, sino como un indicador asociado directamente a la presencia de IA en la oferta.

## 8. Salarios e IA

Se observa una diferencia salarial clara:

- Ofertas sin mencion de IA: salario medio de 53 250,22 USD.
- Ofertas con mencion de IA: salario medio de 82 331,61 USD.

La correlacion global entre `ai_intensity_score` y `salary_usd` es positiva:

- Correlacion global: 0,4024.

Por region, la correlacion entre intensidad de IA y salario es alta en todas las regiones:

- Southeast Asia: 0,8085.
- South America: 0,8033.
- Africa: 0,7973.
- North America: 0,7949.
- Europe: 0,7942.
- East Asia: 0,7896.
- South Asia: 0,7864.
- Middle East: 0,7812.
- Oceania: 0,7683.

Interpretacion para la memoria: los datos sugieren una prima salarial asociada a la presencia e intensidad de IA. Es recomendable formularlo como asociacion estadistica, no como causalidad.

## 9. Riesgo de automatizacion

El codigo de Iñaki filtra los casos con `automation_risk_score > 0.7` y plantea graficos por:

- tamaño de empresa,
- puesto de trabajo,
- industria.

En la base limpia, los casos con riesgo superior a 0,7 se distribuyen asi por industria:

- Agriculture: 287.
- Retail: 264.
- Manufacturing: 254.
- Healthcare: 252.
- Tech: 197.

Interpretacion para la memoria: los sectores no tecnologicos, especialmente Agriculture y Retail, concentran mas casos de alto riesgo de automatizacion dentro de la base limpia.

Advertencia: la variable categorica `ai_job_displacement_risk` no parece estar alineada con `automation_risk_score`, ya que las categorias Low, Medium y High tienen medias de riesgo muy parecidas. Por eso, para hablar de riesgo de automatizacion es mejor usar `automation_risk_score`.

## 10. Revision del codigo

### Aaron

El pipeline de limpieza es claro y util para documentar la construccion de la base GOLD. La principal mejora seria explicar por que se conservan solo las cinco industrias mas frecuentes, ya que esta decision reduce la muestra de 5000 a 2830 registros y limita el alcance del analisis.

### Claudia

El analisis de skills esta bien enfocado para la memoria. Es especialmente aprovechable el ranking de habilidades y la comparacion 2010 vs 2025. Mejoras recomendadas:

- Añadir titulos, ejes y tamaños de figura a todos los graficos.
- Guardar los graficos como imagenes si van a insertarse en la memoria.
- Explicar que `Not Specified` se excluye para no contaminar el ranking de habilidades.

### Pau

El analisis temporal es uno de los mas solidos del proyecto. Muestra claramente el incremento de la presencia de IA y de la intensidad de IA. Mejoras recomendadas:

- Añadir una breve interpretacion debajo de cada grafico.
- Marcar visualmente los cambios de 2018 y 2022, porque parecen puntos de salto.
- Evitar quedarse solo en el grafico: incluir una tabla resumen con los años clave.

### Iñaki

El enfoque de riesgo alto es util, pero el Rmd necesita algunos ajustes:

- Falta cargar explicitamente `ggplot2`.
- Conviene ordenar las barras de mayor a menor frecuencia.
- El limite fijo del eje Y en 325 puede ocultar o distorsionar si cambian los datos.
- Los textos tienen problemas de codificacion, por ejemplo `tamaÃ±o`.

### Roger

La idea de comparar intensidad de IA y salario por regiones es buena para una seccion de resultados. Sin embargo, el archivo contiene codigo repetido y varias versiones de la misma idea. Mejoras recomendadas:

- Dejar una sola version final limpia.
- Evitar `file.choose()` y cargar directamente `ai_impact_jobs_2010_2025_GOLD.csv`.
- Usar los nombres reales de region de la base: `North America`, `Europe`, `East Asia`, `South Asia`, `Southeast Asia`, etc.
- Si se agrupa Asia, explicar que incluye East Asia, South Asia y Southeast Asia.
- Presentar la correlacion como asociacion y no como relacion causal.

## 11. Estructura recomendada para la memoria

Una estructura posible seria:

1. Introduccion.
   - Contexto: impacto de la IA en el empleo.
   - Objetivo del proyecto.
   - Preguntas de investigacion.

2. Datos y metodologia.
   - Descripcion de la base original.
   - Variables principales.
   - Proceso de limpieza.
   - Justificacion de la base GOLD.
   - Limitaciones de la limpieza.

3. Evolucion de la IA en el mercado laboral.
   - Porcentaje de ofertas que mencionan IA por año.
   - Evolucion del `ai_intensity_score`.
   - Interpretacion de los saltos temporales.

4. Habilidades de IA demandadas.
   - Ranking general.
   - Comparacion 2010 vs 2025.
   - Aparicion de LLMs y generative AI.

5. Salarios e intensidad de IA.
   - Comparacion salarial entre ofertas con y sin IA.
   - Correlacion entre intensidad de IA y salario.
   - Analisis por region.

6. Riesgo de automatizacion y reskilling.
   - Casos con riesgo alto.
   - Sectores y puestos mas expuestos.
   - Interpretacion prudente de `reskilling_required`.

7. Conclusiones.
   - La presencia de IA crece claramente desde 2018.
   - Las habilidades de IA se asocian a mejores salarios.
   - Los sectores no tecnologicos tambien presentan riesgo alto de automatizacion.
   - El mercado laboral exige adaptacion y aprendizaje continuo.

8. Limitaciones.
   - Base filtrada a cinco industrias.
   - Variables posiblemente simuladas o construidas.
   - Correlacion no implica causalidad.
   - Algunas variables categoricas no coinciden bien con sus puntuaciones numericas.

## 12. Frases listas para usar en la memoria

La base de datos inicial estaba formada por 5000 ofertas de empleo publicadas entre 2010 y 2025. Tras el proceso de limpieza, se obtuvo una base final de 2830 registros, denominada GOLD, que conserva las variables necesarias para analizar la relacion entre inteligencia artificial, empleo, salarios y riesgo de automatizacion.

El analisis temporal muestra un aumento progresivo de la presencia de la inteligencia artificial en las ofertas laborales. Mientras que en 2010 solo el 9,8% de las ofertas mencionaban IA, en 2024 este porcentaje alcanzo el 70,3%. Este crecimiento sugiere una incorporacion cada vez mayor de competencias relacionadas con IA en el mercado laboral.

Las habilidades de IA mas frecuentes en la base limpia son reinforcement learning, NLP, MLOps, deep learning y computer vision. En 2025 aparece ademas una presencia destacada de LLMs, lo que refleja la importancia reciente de los modelos de lenguaje en las ofertas de empleo.

Las ofertas que mencionan IA presentan un salario medio superior al de las ofertas que no la mencionan. En concreto, las ofertas con IA tienen un salario medio de 82 331,61 USD, frente a 53 250,22 USD en las ofertas sin IA. Esta diferencia apunta a una posible prima salarial asociada a las competencias de inteligencia artificial.

El riesgo de automatizacion no se distribuye de forma exclusiva en el sector tecnologico. En la base limpia, los sectores Agriculture, Retail y Manufacturing concentran un numero elevado de casos con `automation_risk_score` superior a 0,7, lo que indica que la transformacion asociada a la IA afecta tambien a sectores tradicionales.

## 13. Pendientes recomendados antes de entregar

- Unificar todos los codigos en un unico notebook final ordenado.
- Corregir nombres de archivos para evitar espacios, tildes y caracteres especiales.
- Arreglar problemas de codificacion en textos y graficos.
- Guardar los graficos finales en una carpeta `figuras`.
- Añadir una tabla de variables para la memoria.
- Revisar si la base de datos es real, simulada o procedente de una fuente externa y citarla correctamente.
- Explicar claramente que los resultados son asociaciones estadisticas y no pruebas causales.
