# Evolución del empleo ante la inteligencia artificial (2010-2025)

Repositorio del proyecto de la asignatura **Proyecto I: Comprensión de datos** del Grado en Ciencia de Datos.

El objetivo del proyecto es analizar la relación entre la expansión de la inteligencia artificial y distintas variables del empleo entre 2010 y 2025: salarios ofertados, riesgo de automatización, nivel de experiencia profesional y necesidad de recapacitación profesional (*reskilling*).

## Estructura del repositorio

```text
Proyecto/
├── data/
│   ├── raw/                         # Dataset original
│   └── processed/                   # Dataset GOLD usado en análisis finales
├── docs/
│   ├── entrega/memoria_final.pdf    # Memoria final del proyecto
│   └── GANTT.png                    # Diagrama de Gantt
├── notebooks/
│   └── Claudia_Proyecto.ipynb       # Notebook de trabajo
├── outputs/
│   ├── salidas_6_3/                 # Tablas y figuras del apartado 6.3
│   └── tables/                      # Tablas generadas por el pipeline reproducible
├── src/
│   ├── analysis_pipeline.py         # Pipeline reproducible principal
│   └── codigo_figuras_tablas_6_3.py # Script de tablas y figuras del apartado 6.3
├── requirements.txt
└── README.md
```

## Cómo ejecutar el proyecto

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python src/analysis_pipeline.py
```

El pipeline genera:

- `outputs/ai_impact_jobs_2010_2025_GOLD_REVISED.csv`
- tablas CSV en `outputs/tables/`
- métricas principales en `outputs/summary_metrics.json`
- resumen técnico en `outputs/informe_tecnico.md`

## Archivos principales

- `data/raw/ai_impact_jobs_2010_2025.csv`: dataset original.
- `data/processed/ai_impact_jobs_2010_2025_GOLD.csv`: dataset procesado usado para parte del análisis.
- `src/analysis_pipeline.py`: limpieza y análisis reproducible.
- `src/codigo_figuras_tablas_6_3.py`: generación de tablas y figuras del apartado 6.3.
- `docs/entrega/memoria_final.pdf`: memoria final del proyecto.

## Nota metodológica

Los resultados muestran asociaciones estadísticas observadas dentro del dataset. No deben interpretarse como relaciones causales directas ni extrapolarse automáticamente a todo el mercado laboral mundial.
