# Tablas del apartado 6.3

## Tabla 1. Salario medio ofertado según mención de IA en la versión GOLD del dataset.

| Mención de IA (ai_mentioned) | Nº de ofertas | Salario medio (salary_usd) | Mediana salarial |
| --- | --- | --- | --- |
| False | 1.945 | 53.250,22 | 55.151 |
| True | 885 | 82.331,61 | 85.705 |


## Tabla 2. Correlación entre intensidad de IA y salario ofertado.

| Método de correlación | Coeficiente | Interpretación | Significación |
| --- | --- | --- | --- |
| Pearson | 0,402 | Asociación positiva moderada | p < 0,001 |
| Spearman | 0,306 | Asociación positiva débil-moderada | p < 0,001 |


## Tabla 3. Riesgo de automatización por industria en la versión GOLD del dataset.

| Industria | Nº de ofertas | Media de automation_risk_score | % de ofertas con riesgo > 0,7 |
| --- | --- | --- | --- |
| Agriculture | 567 | 0,620 | 50,6 % |
| Healthcare | 557 | 0,612 | 45,2 % |
| Manufacturing | 569 | 0,608 | 44,6 % |
| Retail | 564 | 0,599 | 46,8 % |
| Tech | 573 | 0,525 | 34,4 % |


## Tabla 4. Distribución del riesgo de desplazamiento por IA según nivel de experiencia.

| Nivel de experiencia | Nº de ofertas | High | Medium | Low | Media de automation_risk_score |
| --- | --- | --- | --- | --- | --- |
| Executive | 490 | 131 (26,7 %) | 188 (38,4 %) | 171 (34,9 %) | 0,601 |
| Intern | 442 | 157 (35,5 %) | 136 (30,8 %) | 149 (33,7 %) | 0,589 |
| Junior | 476 | 155 (32,6 %) | 172 (36,1 %) | 149 (31,3 %) | 0,591 |
| Lead | 463 | 137 (29,6 %) | 161 (34,8 %) | 165 (35,6 %) | 0,611 |
| Mid | 463 | 165 (35,6 %) | 139 (30,0 %) | 159 (34,3 %) | 0,596 |
| Senior | 496 | 153 (30,8 %) | 168 (33,9 %) | 175 (35,3 %) | 0,568 |


## Tabla 5. Tabla cruzada entre ai_mentioned y reskilling_required.

| ai_mentioned | reskilling_required = False | reskilling_required = True | Total |
| --- | --- | --- | --- |
| False | 1.945 | 0 | 1.945 |
| True | 0 | 885 | 885 |
| Total | 1.945 | 885 | 2.830 |

