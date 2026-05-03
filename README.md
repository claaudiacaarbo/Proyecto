# Evolucion del empleo ante la inteligencia artificial (2010-2025)

Repositorio del proyecto de analisis de datos sobre el impacto de la inteligencia artificial en el empleo entre 2010 y 2025.

## Contenido

- `ai_impact_jobs_2010_2025.csv`: dataset original.
- `ai_impact_jobs_2010_2025_GOLD.csv`: primera version limpia usada durante el trabajo.
- `src/analysis_pipeline.py`: pipeline final reproducible para limpieza, analisis y visualizaciones.
- `outputs/`: carpeta generada al ejecutar el pipeline con tablas, metricas y figuras.
- Notebooks y scripts originales del equipo: se mantienen para trazabilidad del trabajo.

## Como ejecutar el proyecto

1. Crear un entorno virtual de Python.

```bash
python -m venv .venv
```

2. Activar el entorno e instalar dependencias.

```bash
pip install -r requirements.txt
```

3. Ejecutar el pipeline final.

```bash
python src/analysis_pipeline.py
```

El script genera:

- una base limpia revisada en `outputs/ai_impact_jobs_2010_2025_GOLD_REVISED.csv`;
- tablas de resultados en `outputs/tables/`;
- graficos en `outputs/figures/`;
- un resumen tecnico en `outputs/informe_tecnico.md`;
- metricas principales en `outputs/summary_metrics.json`.

## Analisis incluidos

El pipeline cubre los requisitos tecnicos principales del proyecto:

- limpieza de duplicados, nulos y outliers;
- imputacion de `salary_usd` y `automation_risk_score` con la mediana por industria;
- transformacion de `ai_skills` mediante `split` y `explode`;
- salario medio por anio de publicacion;
- Top 5 de industrias con mayor riesgo medio de automatizacion;
- correlacion de Pearson entre `ai_intensity_score` y `salary_usd`;
- comparacion del riesgo de desplazamiento por nivel de experiencia;
- evolucion temporal de la intensidad de IA y del reskilling;
- comparacion del riesgo de automatizacion por tamano de empresa;
- nube de habilidades tecnicas de IA.

## Nota metodologica

Los resultados muestran asociaciones estadisticas dentro del dataset. No deben interpretarse como relaciones causales directas. La base `GOLD_REVISED` mantiene todas las industrias tras la limpieza para evitar perder representatividad; la primera base `GOLD` se conserva porque fue usada en los notebooks originales.
