"""Pipeline reproducible del proyecto: empleo e inteligencia artificial (2010-2025).

Ejecuta desde la raíz del repositorio:
    python src/analysis_pipeline.py

Genera una versión limpia revisada, tablas y métricas en outputs/.
"""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

INPUT = Path("data/raw/ai_impact_jobs_2010_2025.csv")
OUT = Path("outputs")
TABLES = OUT / "tables"

NUMERIC_COLUMNS = [
    "posting_year",
    "ai_intensity_score",
    "salary_usd",
    "salary_change_vs_prev_year_percent",
    "automation_risk_score",
    "job_description_embedding_cluster",
]


def prepare_dirs() -> None:
    OUT.mkdir(exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)


def clean_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    report: dict = {"raw_rows": int(len(df))}
    df = df.drop_duplicates().copy()
    report["duplicated_removed"] = int(report["raw_rows"] - len(df))

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    missing_before = df.isna().sum().astype(int).to_dict()

    # Imputación por mediana de industria y, si falta, mediana global.
    for col in ["salary_usd", "automation_risk_score"]:
        if col in df.columns:
            med_industry = df.groupby("industry")[col].transform("median")
            df[col] = df[col].fillna(med_industry).fillna(df[col].median())

    if "ai_skills" in df.columns:
        df["ai_skills"] = df["ai_skills"].fillna("Not Specified")
    if "ai_keywords" in df.columns:
        df["ai_keywords"] = df["ai_keywords"].fillna("")

    # Eliminación de outliers salariales por IQR.
    q1 = df["salary_usd"].quantile(0.25)
    q3 = df["salary_usd"].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    before_iqr = len(df)
    df = df[df["salary_usd"].between(lower, upper, inclusive="both")].copy()

    if "automation_risk_score" in df.columns:
        before_risk = len(df)
        df = df[df["automation_risk_score"].between(0, 1, inclusive="both")].copy()
        risk_removed = before_risk - len(df)
    else:
        risk_removed = 0

    report.update({
        "clean_rows": int(len(df)),
        "missing_before": missing_before,
        "missing_after": df.isna().sum().astype(int).to_dict(),
        "salary_iqr": {
            "q1": float(q1),
            "q3": float(q3),
            "iqr": float(iqr),
            "lower_bound": float(lower),
            "upper_bound": float(upper),
            "removed_rows": int(before_iqr - len(df) - risk_removed),
        },
        "automation_risk_out_of_range_removed": int(risk_removed),
    })
    return df.reset_index(drop=True), report


def split_ai_skills(df: pd.DataFrame) -> pd.Series:
    return (
        df.loc[df["ai_skills"].ne("Not Specified"), "ai_skills"]
        .dropna().astype(str).str.split(r",\s*", regex=True).explode().str.strip()
    ).loc[lambda s: s.ne("")]


def build_outputs(df: pd.DataFrame, report: dict) -> None:
    clean_path = OUT / "ai_impact_jobs_2010_2025_GOLD_REVISED.csv"
    df.to_csv(clean_path, index=False)

    salary_by_year = df.groupby("posting_year", as_index=False)["salary_usd"].mean().sort_values("posting_year")
    salary_by_year.to_csv(TABLES / "salary_mean_by_year.csv", index=False)

    industry_risk = df.groupby("industry", as_index=False).agg(
        mean_automation_risk=("automation_risk_score", "mean"),
        jobs=("job_id", "count"),
    ).sort_values("mean_automation_risk", ascending=False)
    industry_risk.to_csv(TABLES / "industry_automation_risk.csv", index=False)
    industry_risk.head(5).to_csv(TABLES / "top5_industries_by_risk.csv", index=False)

    skill_counts = split_ai_skills(df).value_counts().rename_axis("skill").reset_index(name="count")
    skill_counts.to_csv(TABLES / "ai_skills_count.csv", index=False)

    seniority = pd.crosstab(df["seniority_level"], df["ai_job_displacement_risk"], normalize="index").mul(100).round(2)
    seniority.to_csv(TABLES / "displacement_risk_by_seniority_percent.csv")

    year_stats = df.groupby("posting_year", as_index=False).agg(
        mean_ai_intensity=("ai_intensity_score", "mean"),
        ai_share=("ai_mentioned", "mean"),
        reskilling_share=("reskilling_required", "mean"),
        jobs=("job_id", "count"),
    ).sort_values("posting_year")
    year_stats["ai_share"] = (year_stats["ai_share"] * 100).round(2)
    year_stats["reskilling_share"] = (year_stats["reskilling_share"] * 100).round(2)
    year_stats.to_csv(TABLES / "year_stats.csv", index=False)

    corr = df["ai_intensity_score"].corr(df["salary_usd"], method="pearson")
    salary_by_ai = df.groupby("ai_mentioned")["salary_usd"].mean().round(2).rename(index={False: "without_ai", True: "with_ai"}).to_dict()

    summary = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "year_min": int(df["posting_year"].min()),
        "year_max": int(df["posting_year"].max()),
        "salary_mean": float(round(df["salary_usd"].mean(), 2)),
        "automation_risk_mean": float(round(df["automation_risk_score"].mean(), 4)),
        "ai_intensity_salary_pearson_correlation": float(round(corr, 4)),
        "reskilling_required_percent": df["reskilling_required"].value_counts(normalize=True).mul(100).round(2).astype(float).to_dict(),
        "salary_mean_by_ai_mentioned": {str(k): float(v) for k, v in salary_by_ai.items()},
        "cleaning_report": report,
    }
    (OUT / "summary_metrics.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    (OUT / "informe_tecnico.md").write_text(
        "# Informe técnico generado\n\n"
        f"- Registros limpios: {summary['rows']}\n"
        f"- Periodo: {summary['year_min']}-{summary['year_max']}\n"
        f"- Correlación Pearson IA-salario: {summary['ai_intensity_salary_pearson_correlation']}\n"
        "\nNota: la correlación mide asociación estadística, no causalidad.\n",
        encoding="utf-8",
    )


def main() -> None:
    prepare_dirs()
    raw = pd.read_csv(INPUT)
    clean, report = clean_dataset(raw)
    build_outputs(clean, report)
    print("Pipeline ejecutado correctamente. Resultados en outputs/.")


if __name__ == "__main__":
    main()
