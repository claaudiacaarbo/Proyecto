"""Pipeline final del proyecto de empleo e inteligencia artificial.

Este script limpia la base original, calcula los indicadores pedidos en la
memoria y genera tablas/graficos reproducibles para GitHub.
"""

from __future__ import annotations

import argparse
import json
import math
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd


NUMERIC_COLUMNS = [
    "posting_year",
    "ai_intensity_score",
    "salary_usd",
    "salary_change_vs_prev_year_percent",
    "automation_risk_score",
    "job_description_embedding_cluster",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Limpieza, analisis y visualizacion del dataset de empleo e IA."
    )
    parser.add_argument(
        "--input",
        default="ai_impact_jobs_2010_2025.csv",
        help="Ruta del CSV original.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Carpeta donde se guardan la base limpia, tablas y figuras.",
    )
    parser.add_argument(
        "--clean-name",
        default="ai_impact_jobs_2010_2025_GOLD_REVISED.csv",
        help="Nombre del CSV limpio generado.",
    )
    parser.add_argument(
        "--top-industries",
        type=int,
        default=0,
        help=(
            "Si es mayor que 0, conserva solo las N industrias mas frecuentes. "
            "Por defecto se mantienen todas para no perder representatividad."
        ),
    )
    return parser.parse_args()


def ensure_dirs(output_dir: Path) -> dict[str, Path]:
    paths = {
        "root": output_dir,
        "tables": output_dir / "tables",
        "figures": output_dir / "figures",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def impute_by_industry_median(df: pd.DataFrame, column: str) -> pd.DataFrame:
    df = df.copy()
    if column not in df.columns:
        return df

    industry_median = df.groupby("industry")[column].transform("median")
    df[column] = df[column].fillna(industry_median)
    df[column] = df[column].fillna(df[column].median())
    return df


def remove_iqr_outliers(df: pd.DataFrame, column: str) -> tuple[pd.DataFrame, dict[str, float]]:
    """Elimina outliers usando Q1 - 1.5*IQR y Q3 + 1.5*IQR."""
    if column not in df.columns:
        return df, {}

    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    before = len(df)
    filtered = df[df[column].between(lower, upper, inclusive="both")].copy()
    return filtered, {
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "lower_bound": float(lower),
        "upper_bound": float(upper),
        "removed_rows": int(before - len(filtered)),
    }


def clean_dataset(raw: pd.DataFrame, top_industries: int = 0) -> tuple[pd.DataFrame, dict[str, object]]:
    before_rows = len(raw)
    df = raw.drop_duplicates().copy()
    duplicated_removed = before_rows - len(df)

    df = coerce_numeric(df)
    missing_before = df.isna().sum().to_dict()

    df = impute_by_industry_median(df, "salary_usd")
    df = impute_by_industry_median(df, "automation_risk_score")

    if "ai_skills" in df.columns:
        df["ai_skills"] = df["ai_skills"].fillna("Not Specified")
    if "ai_keywords" in df.columns:
        df["ai_keywords"] = df["ai_keywords"].fillna("")

    df, salary_iqr = remove_iqr_outliers(df, "salary_usd")

    # automation_risk_score ya esta acotada entre 0 y 1. Si aparecen valores fuera
    # de rango, los tratamos como atipicos de calidad de datos.
    if "automation_risk_score" in df.columns:
        before_risk = len(df)
        df = df[df["automation_risk_score"].between(0, 1, inclusive="both")].copy()
        risk_removed = before_risk - len(df)
    else:
        risk_removed = 0

    selected_industries: list[str] = []
    if top_industries > 0 and "industry" in df.columns:
        selected_industries = (
            df["industry"].value_counts().head(top_industries).index.tolist()
        )
        df = df[df["industry"].isin(selected_industries)].copy()

    missing_after = df.isna().sum().to_dict()
    report = {
        "raw_rows": int(before_rows),
        "clean_rows": int(len(df)),
        "duplicated_removed": int(duplicated_removed),
        "missing_before": {k: int(v) for k, v in missing_before.items()},
        "missing_after": {k: int(v) for k, v in missing_after.items()},
        "salary_iqr": salary_iqr,
        "automation_risk_out_of_range_removed": int(risk_removed),
        "selected_industries": selected_industries,
    }
    return df.reset_index(drop=True), report


def split_ai_skills(df: pd.DataFrame) -> pd.Series:
    if "ai_skills" not in df.columns:
        return pd.Series(dtype="object")

    skills = (
        df.loc[df["ai_skills"].ne("Not Specified"), "ai_skills"]
        .dropna()
        .astype(str)
        .str.split(r",\s*", regex=True)
        .explode()
        .str.strip()
    )
    return skills[skills.ne("")]


def build_tables(df: pd.DataFrame, tables_dir: Path) -> dict[str, object]:
    tables: dict[str, object] = {}

    salary_by_year = (
        df.groupby("posting_year", as_index=False)["salary_usd"]
        .mean()
        .sort_values("posting_year")
    )
    salary_by_year["salary_usd"] = salary_by_year["salary_usd"].round(2)
    salary_by_year.to_csv(tables_dir / "salary_mean_by_year.csv", index=False)
    tables["salary_by_year"] = salary_by_year

    industry_risk = (
        df.groupby("industry", as_index=False)
        .agg(
            mean_automation_risk=("automation_risk_score", "mean"),
            jobs=("job_id", "count"),
        )
        .sort_values("mean_automation_risk", ascending=False)
    )
    industry_risk["mean_automation_risk"] = industry_risk["mean_automation_risk"].round(4)
    industry_risk.to_csv(tables_dir / "industry_automation_risk.csv", index=False)
    industry_risk.head(5).to_csv(tables_dir / "top5_industries_by_risk.csv", index=False)
    tables["industry_risk"] = industry_risk

    skills_count = split_ai_skills(df).value_counts().rename_axis("skill").reset_index(name="count")
    skills_count.to_csv(tables_dir / "ai_skills_count.csv", index=False)
    tables["skills_count"] = skills_count

    displacement_by_seniority = pd.crosstab(
        df["seniority_level"],
        df["ai_job_displacement_risk"],
        normalize="index",
    ).mul(100).round(2)
    displacement_by_seniority.to_csv(tables_dir / "displacement_risk_by_seniority_percent.csv")
    tables["displacement_by_seniority"] = displacement_by_seniority

    risk_by_company_size = (
        df.groupby("company_size", as_index=False)
        .agg(
            mean_automation_risk=("automation_risk_score", "mean"),
            jobs=("job_id", "count"),
        )
        .sort_values("mean_automation_risk", ascending=False)
    )
    risk_by_company_size["mean_automation_risk"] = risk_by_company_size[
        "mean_automation_risk"
    ].round(4)
    risk_by_company_size.to_csv(tables_dir / "automation_risk_by_company_size.csv", index=False)
    tables["risk_by_company_size"] = risk_by_company_size

    year_stats = (
        df.groupby("posting_year", as_index=False)
        .agg(
            mean_ai_intensity=("ai_intensity_score", "mean"),
            ai_share=("ai_mentioned", "mean"),
            reskilling_share=("reskilling_required", "mean"),
            jobs=("job_id", "count"),
        )
        .sort_values("posting_year")
    )
    year_stats["mean_ai_intensity"] = year_stats["mean_ai_intensity"].round(4)
    year_stats["ai_share"] = (year_stats["ai_share"] * 100).round(2)
    year_stats["reskilling_share"] = (year_stats["reskilling_share"] * 100).round(2)
    year_stats.to_csv(tables_dir / "year_stats.csv", index=False)
    tables["year_stats"] = year_stats

    correlation_by_region = (
        df.groupby("region")
        .apply(
            lambda group: pd.Series(
                {
                    "pearson_corr_ai_salary": group["ai_intensity_score"].corr(
                        group["salary_usd"], method="pearson"
                    ),
                    "jobs": len(group),
                }
            )
        )
        .reset_index()
        .sort_values("pearson_corr_ai_salary", ascending=False)
    )
    correlation_by_region["pearson_corr_ai_salary"] = correlation_by_region[
        "pearson_corr_ai_salary"
    ].round(4)
    correlation_by_region["jobs"] = correlation_by_region["jobs"].astype(int)
    correlation_by_region.to_csv(tables_dir / "correlation_ai_salary_by_region.csv", index=False)
    tables["correlation_by_region"] = correlation_by_region

    region_map = {
        "East Asia": "Asia",
        "South Asia": "Asia",
        "Southeast Asia": "Asia",
        "North America": "North America",
        "Europe": "Europe",
    }
    regional_df = df.assign(region_group=df["region"].map(region_map)).dropna(
        subset=["region_group"]
    )
    correlation_by_region_group = (
        regional_df.groupby("region_group")
        .apply(
            lambda group: pd.Series(
                {
                    "pearson_corr_ai_salary": group["ai_intensity_score"].corr(
                        group["salary_usd"], method="pearson"
                    ),
                    "jobs": len(group),
                }
            )
        )
        .reset_index()
        .sort_values("pearson_corr_ai_salary", ascending=False)
    )
    correlation_by_region_group["pearson_corr_ai_salary"] = correlation_by_region_group[
        "pearson_corr_ai_salary"
    ].round(4)
    correlation_by_region_group["jobs"] = correlation_by_region_group["jobs"].astype(int)
    correlation_by_region_group.to_csv(
        tables_dir / "correlation_ai_salary_by_region_group.csv", index=False
    )
    tables["correlation_by_region_group"] = correlation_by_region_group

    return tables


def calculate_summary(df: pd.DataFrame, cleaning_report: dict[str, object]) -> dict[str, object]:
    correlation = df["ai_intensity_score"].corr(df["salary_usd"], method="pearson")

    reskilling_percent = (
        df["reskilling_required"].value_counts(normalize=True).mul(100).round(2).to_dict()
    )

    salary_by_ai = (
        df.groupby("ai_mentioned")["salary_usd"]
        .mean()
        .round(2)
        .rename(index={False: "without_ai", True: "with_ai"})
        .to_dict()
    )

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "year_min": int(df["posting_year"].min()),
        "year_max": int(df["posting_year"].max()),
        "salary_mean": float(round(df["salary_usd"].mean(), 2)),
        "automation_risk_mean": float(round(df["automation_risk_score"].mean(), 4)),
        "ai_intensity_salary_pearson_correlation": float(round(correlation, 4)),
        "reskilling_required_percent": {
            str(k): float(v) for k, v in reskilling_percent.items()
        },
        "salary_mean_by_ai_mentioned": {str(k): float(v) for k, v in salary_by_ai.items()},
        "cleaning_report": cleaning_report,
    }


def normalize(values: list[float], out_min: float, out_max: float) -> list[float]:
    valid = [v for v in values if not math.isnan(v)]
    if not valid:
        return [out_min for _ in values]
    v_min, v_max = min(valid), max(valid)
    if math.isclose(v_min, v_max):
        return [(out_min + out_max) / 2 for _ in values]
    return [out_min + (v - v_min) * (out_max - out_min) / (v_max - v_min) for v in values]


def write_svg_line_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    path: Path,
    y_suffix: str = "",
) -> None:
    width, height = 920, 520
    left, right, top, bottom = 80, 40, 70, 80
    xs = data[x_col].astype(float).tolist()
    ys = data[y_col].astype(float).tolist()
    px = normalize(xs, left, width - right)
    py = normalize(ys, height - bottom, top)
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(px, py))

    labels = []
    for x, y, year, value in zip(px, py, data[x_col], data[y_col]):
        labels.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#2563eb" />'
            f'<text x="{x:.1f}" y="{height - 45}" text-anchor="middle" '
            f'font-size="12">{int(year)}</text>'
        )
    for tick in np.linspace(min(ys), max(ys), 5):
        y = normalize([float(tick)], height - bottom, top)[0]
        labels.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" '
            f'stroke="#e5e7eb" />'
            f'<text x="{left-10}" y="{y+4:.1f}" text-anchor="end" '
            f'font-size="12">{tick:.1f}{y_suffix}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#ffffff"/>
<text x="{width/2}" y="34" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700">{title}</text>
<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#111827"/>
<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#111827"/>
{''.join(labels)}
<polyline points="{points}" fill="none" stroke="#2563eb" stroke-width="3"/>
</svg>"""
    path.write_text(svg, encoding="utf-8")


def write_svg_bar_chart(
    data: pd.DataFrame,
    label_col: str,
    value_col: str,
    title: str,
    path: Path,
    value_suffix: str = "",
    max_rows: int = 12,
) -> None:
    data = data.head(max_rows).copy()
    width = 980
    row_h = 42
    height = 110 + row_h * len(data)
    left, right, top = 250, 60, 70
    values = data[value_col].astype(float).tolist()
    max_value = max(values) if values else 1
    rows = []
    for i, (_, row) in enumerate(data.iterrows()):
        y = top + i * row_h
        value = float(row[value_col])
        bar_w = 1 if max_value == 0 else value / max_value * (width - left - right)
        label = str(row[label_col])
        label = label[:38] + "..." if len(label) > 41 else label
        rows.append(
            f'<text x="{left-12}" y="{y+24}" text-anchor="end" font-size="14">{label}</text>'
            f'<rect x="{left}" y="{y+6}" width="{bar_w:.1f}" height="24" fill="#0f766e"/>'
            f'<text x="{left+bar_w+8:.1f}" y="{y+24}" font-size="13">{value:.2f}{value_suffix}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#ffffff"/>
<text x="{width/2}" y="34" text-anchor="middle" font-family="Arial" font-size="22" font-weight="700">{title}</text>
{''.join(rows)}
</svg>"""
    path.write_text(svg, encoding="utf-8")


def write_svg_wordcloud(skills_count: pd.DataFrame, path: Path) -> None:
    width, height = 980, 560
    top = skills_count.head(30)
    if top.empty:
        path.write_text("<svg></svg>", encoding="utf-8")
        return

    counts = top["count"].astype(float).tolist()
    sizes = normalize(counts, 18, 58)
    palette = ["#0f766e", "#2563eb", "#b45309", "#7c3aed", "#be123c"]
    positions = []
    x, y = 80, 110
    for i, ((_, row), size) in enumerate(zip(top.iterrows(), sizes)):
        word = str(row["skill"])
        color = palette[i % len(palette)]
        positions.append(
            f'<text x="{x}" y="{y}" font-size="{size:.0f}" fill="{color}" '
            f'font-family="Arial" font-weight="700">{word}</text>'
        )
        x += int(70 + len(word) * size * 0.42)
        if x > width - 260:
            x = 80 + (i % 3) * 35
            y += 78
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#ffffff"/>
<text x="{width/2}" y="42" text-anchor="middle" font-family="Arial" font-size="24" font-weight="700">Nube de habilidades IA</text>
{''.join(positions)}
</svg>"""
    path.write_text(svg, encoding="utf-8")


def try_write_matplotlib_charts(tables: dict[str, object], figures_dir: Path) -> bool:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return False

    year_stats: pd.DataFrame = tables["year_stats"]  # type: ignore[assignment]
    salary_by_year: pd.DataFrame = tables["salary_by_year"]  # type: ignore[assignment]
    industry_risk: pd.DataFrame = tables["industry_risk"]  # type: ignore[assignment]
    risk_by_company_size: pd.DataFrame = tables["risk_by_company_size"]  # type: ignore[assignment]
    skills_count: pd.DataFrame = tables["skills_count"]  # type: ignore[assignment]

    plt.style.use("default")

    charts = [
        (
            salary_by_year,
            "posting_year",
            "salary_usd",
            "Salario medio por anio",
            "salary_mean_by_year.png",
        ),
        (
            year_stats,
            "posting_year",
            "mean_ai_intensity",
            "Evolucion de la intensidad de IA",
            "ai_intensity_by_year.png",
        ),
        (
            year_stats,
            "posting_year",
            "reskilling_share",
            "Porcentaje de empleos con reskilling",
            "reskilling_by_year.png",
        ),
    ]
    for data, x_col, y_col, title, filename in charts:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(data[x_col], data[y_col], marker="o")
        ax.set_title(title)
        ax.set_xlabel("Anio")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(figures_dir / filename, dpi=160)
        plt.close(fig)

    bar_charts = [
        (
            industry_risk.head(5),
            "industry",
            "mean_automation_risk",
            "Top 5 industrias por riesgo de automatizacion",
            "top5_industries_by_risk.png",
        ),
        (
            risk_by_company_size,
            "company_size",
            "mean_automation_risk",
            "Riesgo medio por tamano de empresa",
            "risk_by_company_size.png",
        ),
        (
            skills_count.head(10),
            "skill",
            "count",
            "Top habilidades de IA",
            "top_ai_skills.png",
        ),
    ]
    for data, label_col, value_col, title, filename in bar_charts:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(data[label_col].astype(str), data[value_col])
        ax.invert_yaxis()
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(figures_dir / filename, dpi=160)
        plt.close(fig)

    try:
        from wordcloud import WordCloud

        frequencies = dict(zip(skills_count["skill"], skills_count["count"]))
        cloud = WordCloud(width=1200, height=700, background_color="white").generate_from_frequencies(
            frequencies
        )
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.imshow(cloud, interpolation="bilinear")
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(figures_dir / "wordcloud_ai_skills.png", dpi=160)
        plt.close(fig)
    except Exception:
        pass

    return True


def write_charts(tables: dict[str, object], figures_dir: Path) -> dict[str, object]:
    matplotlib_used = try_write_matplotlib_charts(tables, figures_dir)

    salary_by_year: pd.DataFrame = tables["salary_by_year"]  # type: ignore[assignment]
    year_stats: pd.DataFrame = tables["year_stats"]  # type: ignore[assignment]
    industry_risk: pd.DataFrame = tables["industry_risk"]  # type: ignore[assignment]
    risk_by_company_size: pd.DataFrame = tables["risk_by_company_size"]  # type: ignore[assignment]
    skills_count: pd.DataFrame = tables["skills_count"]  # type: ignore[assignment]

    write_svg_line_chart(
        salary_by_year,
        "posting_year",
        "salary_usd",
        "Salario medio por anio",
        figures_dir / "salary_mean_by_year.svg",
    )
    write_svg_line_chart(
        year_stats,
        "posting_year",
        "mean_ai_intensity",
        "Evolucion de la intensidad de IA",
        figures_dir / "ai_intensity_by_year.svg",
    )
    write_svg_line_chart(
        year_stats,
        "posting_year",
        "reskilling_share",
        "Porcentaje de empleos con reskilling",
        figures_dir / "reskilling_by_year.svg",
        y_suffix="%",
    )
    write_svg_bar_chart(
        industry_risk,
        "industry",
        "mean_automation_risk",
        "Top 5 industrias por riesgo de automatizacion",
        figures_dir / "top5_industries_by_risk.svg",
        max_rows=5,
    )
    write_svg_bar_chart(
        risk_by_company_size,
        "company_size",
        "mean_automation_risk",
        "Riesgo medio por tamano de empresa",
        figures_dir / "risk_by_company_size.svg",
    )
    write_svg_bar_chart(
        skills_count,
        "skill",
        "count",
        "Top habilidades de IA",
        figures_dir / "top_ai_skills.svg",
        max_rows=10,
    )
    write_svg_wordcloud(skills_count, figures_dir / "wordcloud_ai_skills.svg")

    return {
        "matplotlib_png_created": matplotlib_used,
        "svg_fallback_created": True,
    }


def write_markdown_report(summary: dict[str, object], tables: dict[str, object], path: Path) -> None:
    industry_risk: pd.DataFrame = tables["industry_risk"]  # type: ignore[assignment]
    skills_count: pd.DataFrame = tables["skills_count"]  # type: ignore[assignment]
    year_stats: pd.DataFrame = tables["year_stats"]  # type: ignore[assignment]

    top_industries = "\n".join(
        f"- {row.industry}: {row.mean_automation_risk:.4f}"
        for row in industry_risk.head(5).itertuples()
    )
    top_skills = "\n".join(
        f"- {row.skill}: {row.count}" for row in skills_count.head(10).itertuples()
    )
    correlation_by_region: pd.DataFrame = tables["correlation_by_region"]  # type: ignore[assignment]
    regional_corr = "\n".join(
        f"- {row.region}: {row.pearson_corr_ai_salary:.4f}"
        for row in correlation_by_region.head(5).itertuples()
    )
    latest = year_stats.sort_values("posting_year").tail(1).iloc[0]
    corr = summary["ai_intensity_salary_pearson_correlation"]

    text = f"""# Informe tecnico generado

## Resumen

- Registros limpios: {summary["rows"]}
- Periodo analizado: {summary["year_min"]}-{summary["year_max"]}
- Salario medio: {summary["salary_mean"]} USD
- Riesgo medio de automatizacion: {summary["automation_risk_mean"]}
- Correlacion Pearson entre intensidad de IA y salario: {corr}
- Reskilling en {int(latest["posting_year"])}: {latest["reskilling_share"]}%

## Top 5 industrias con mayor riesgo medio

{top_industries}

## Habilidades de IA mas frecuentes

{top_skills}

## Correlacion IA-salario por region

{regional_corr}

## Nota metodologica

La correlacion mide asociacion estadistica, no causalidad. Los resultados deben
interpretarse como patrones observados dentro del dataset analizado.
"""
    path.write_text(textwrap.dedent(text), encoding="utf-8")


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_paths = ensure_dirs(Path(args.output_dir))

    raw = pd.read_csv(input_path)
    clean, cleaning_report = clean_dataset(raw, top_industries=args.top_industries)

    clean_path = output_paths["root"] / args.clean_name
    clean.to_csv(clean_path, index=False)

    tables = build_tables(clean, output_paths["tables"])
    summary = calculate_summary(clean, cleaning_report)
    chart_report = write_charts(tables, output_paths["figures"])
    summary["chart_report"] = chart_report

    (output_paths["root"] / "summary_metrics.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_markdown_report(summary, tables, output_paths["root"] / "informe_tecnico.md")

    print(f"Base limpia guardada en: {clean_path}")
    print(f"Tablas guardadas en: {output_paths['tables']}")
    print(f"Figuras guardadas en: {output_paths['figures']}")
    print(f"Correlacion IA-salario: {summary['ai_intensity_salary_pearson_correlation']}")


if __name__ == "__main__":
    main()
