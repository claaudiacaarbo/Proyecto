"""
Código para generar las tablas y figuras del apartado 6.3.
Proyecto: Evolución del Empleo ante la Inteligencia Artificial (2010-2025)
Dataset esperado: data/processed/ai_impact_jobs_2010_2025_GOLD.csv

Qué genera este script:
- Tabla 1: Salario medio ofertado según mención de IA.
- Figura 1: Salario medio ofertado según mención de IA.
- Tabla 2: Correlación entre intensidad de IA y salario ofertado.
- Tabla 3: Riesgo de automatización por industria.
- Figura 2: Media de riesgo de automatización por industria.
- Figura 3: Porcentaje de ofertas con riesgo de automatización superior a 0,7.
- Tabla 4: Distribución del riesgo de desplazamiento por IA según nivel de experiencia.
- Figura 4: Distribución porcentual del riesgo de desplazamiento por IA según nivel de experiencia.
- Tabla 5: Tabla cruzada entre ai_mentioned y reskilling_required.
- Figura 5: Relación entre mención de IA y necesidad de reskilling.

Uso recomendado:
1. Ejecuta en terminal desde la raíz del repositorio:
       python src/codigo_figuras_tablas_6_3.py
2. Los resultados se guardarán en la carpeta outputs/salidas_6_3/.

También puedes importarlo en Jupyter y ejecutar main().
"""

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from scipy.stats import pearsonr, spearmanr
except ImportError as exc:
    raise ImportError("Falta scipy. Instálalo con: pip install scipy") from exc


# -----------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------------------------------------------------------
DATASET_PATH = Path("data/processed/ai_impact_jobs_2010_2025_GOLD.csv")
OUTPUT_DIR = Path("outputs/salidas_6_3")
TABLES_DIR = OUTPUT_DIR / "tablas"
FIGURES_DIR = OUTPUT_DIR / "figuras"
TABLE_IMAGES_DIR = OUTPUT_DIR / "tablas_png"

# Cambia a False si no quieres imágenes PNG de las tablas.
SAVE_TABLE_IMAGES = True

# Umbral usado en el proyecto para considerar alto riesgo de automatización.
AUTOMATION_HIGH_RISK_THRESHOLD = 0.7


# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------------------------------------------------
def find_dataset() -> Path:
    """Busca el dataset GOLD en la ruta organizada del repositorio."""
    if DATASET_PATH.exists():
        return DATASET_PATH
    raise FileNotFoundError(
        f"No se encontró {DATASET_PATH}. Ejecuta el script desde la raíz del repositorio."
    )


def ensure_output_dirs() -> None:
    """Crea las carpetas de salida si no existen."""
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def normalize_bool(series: pd.Series) -> pd.Series:
    """Convierte una columna booleana leída como bool, string o número a booleano."""
    if pd.api.types.is_bool_dtype(series):
        return series

    mapping = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "yes": True,
        "no": False,
        "si": True,
        "sí": True,
        "no": False,
    }

    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map(mapping)
        .astype("boolean")
    )


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Asegura tipos correctos y valida columnas necesarias."""
    required_columns = [
        "ai_mentioned",
        "salary_usd",
        "ai_intensity_score",
        "industry",
        "automation_risk_score",
        "seniority_level",
        "ai_job_displacement_risk",
        "reskilling_required",
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas necesarias en el dataset: {missing}")

    df = df.copy()
    df["ai_mentioned"] = normalize_bool(df["ai_mentioned"])
    df["reskilling_required"] = normalize_bool(df["reskilling_required"])

    numeric_cols = ["salary_usd", "ai_intensity_score", "automation_risk_score"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["industry"] = df["industry"].astype(str).str.strip()
    df["seniority_level"] = df["seniority_level"].astype(str).str.strip()
    df["ai_job_displacement_risk"] = df["ai_job_displacement_risk"].astype(str).str.strip()

    return df


def format_number_es(value, decimals: int = 2) -> str:
    """Formato español: punto de miles y coma decimal."""
    if pd.isna(value):
        return ""
    text = f"{float(value):,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def format_integer_es(value) -> str:
    """Formato español para enteros con punto de miles."""
    if pd.isna(value):
        return ""
    return f"{int(round(float(value))):,}".replace(",", ".")


def format_percent_es(value, decimals: int = 1) -> str:
    """Formato español de porcentaje."""
    return f"{format_number_es(value, decimals)} %"


def pvalue_label(pvalue: float) -> str:
    """Devuelve una etiqueta de significación compacta."""
    if pd.isna(pvalue):
        return ""
    if pvalue < 0.001:
        return "p < 0,001"
    return f"p = {format_number_es(pvalue, 3)}"


def correlation_interpretation(value: float) -> str:
    """Interpreta de forma descriptiva el tamaño de una correlación."""
    sign = "positiva" if value >= 0 else "negativa"
    abs_value = abs(value)

    if abs_value < 0.10:
        strength = "muy débil"
    elif abs_value < 0.30:
        strength = "débil"
    elif abs_value < 0.40:
        strength = "débil-moderada"
    elif abs_value < 0.60:
        strength = "moderada"
    else:
        strength = "fuerte"

    return f"Asociación {sign} {strength}"


def df_to_markdown(df: pd.DataFrame) -> str:
    """Convierte un DataFrame a tabla Markdown sin depender de tabulate."""
    df = df.astype(str)
    header = "| " + " | ".join(df.columns) + " |"
    separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in df.to_numpy()]
    return "\n".join([header, separator] + rows)


def save_table_csv(df: pd.DataFrame, filename: str) -> None:
    """Guarda una tabla en CSV con separador ;, cómodo para Excel en español."""
    df.to_csv(TABLES_DIR / filename, sep=";", index=False, encoding="utf-8-sig")


def save_table_image(df: pd.DataFrame, filename: str, title: str) -> None:
    """Guarda una tabla como imagen PNG para poder insertarla fácilmente en la memoria."""
    if not SAVE_TABLE_IMAGES:
        return

    # Tamaño adaptado al número de filas y columnas.
    width = max(9, min(22, 2.2 * len(df.columns)))
    height = max(2.5, 0.55 * (len(df) + 2))

    fig, ax = plt.subplots(figsize=(width, height))
    ax.axis("off")
    ax.set_title(title, pad=12, fontsize=11)

    table = ax.table(
        cellText=df.astype(str).values,
        colLabels=df.columns,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1, 1.35)

    fig.tight_layout()
    fig.savefig(TABLE_IMAGES_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def annotate_bars(ax, decimals: int = 0, suffix: str = "") -> None:
    """Añade etiquetas encima de las barras verticales."""
    for patch in ax.patches:
        height = patch.get_height()
        label = format_number_es(height, decimals) + suffix
        ax.text(
            patch.get_x() + patch.get_width() / 2,
            height,
            label,
            ha="center",
            va="bottom",
            fontsize=9,
        )


# -----------------------------------------------------------------------------
# TABLAS
# -----------------------------------------------------------------------------
def build_table_1(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tabla 1. Salario medio ofertado según mención de IA."""
    raw = (
        df.dropna(subset=["ai_mentioned", "salary_usd"])
        .groupby("ai_mentioned", dropna=False)["salary_usd"]
        .agg(n_ofertas="count", salario_medio="mean", mediana_salarial="median")
        .reset_index()
        .sort_values("ai_mentioned")
    )

    formatted = pd.DataFrame(
        {
            "Mención de IA (ai_mentioned)": raw["ai_mentioned"].astype(bool).astype(str),
            "Nº de ofertas": raw["n_ofertas"].apply(format_integer_es),
            "Salario medio (salary_usd)": raw["salario_medio"].apply(lambda x: format_number_es(x, 2)),
            "Mediana salarial": raw["mediana_salarial"].apply(format_integer_es),
        }
    )

    return raw, formatted


def build_table_2(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tabla 2. Correlación entre intensidad de IA y salario ofertado."""
    data = df.dropna(subset=["ai_intensity_score", "salary_usd"])

    pearson_coef, pearson_p = pearsonr(data["ai_intensity_score"], data["salary_usd"])
    spearman_coef, spearman_p = spearmanr(data["ai_intensity_score"], data["salary_usd"])

    raw = pd.DataFrame(
        {
            "metodo_correlacion": ["Pearson", "Spearman"],
            "coeficiente": [pearson_coef, spearman_coef],
            "p_value": [pearson_p, spearman_p],
        }
    )

    formatted = pd.DataFrame(
        {
            "Método de correlación": raw["metodo_correlacion"],
            "Coeficiente": raw["coeficiente"].apply(lambda x: format_number_es(x, 3)),
            "Interpretación": raw["coeficiente"].apply(correlation_interpretation),
            "Significación": raw["p_value"].apply(pvalue_label),
        }
    )

    return raw, formatted


def build_table_3(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tabla 3. Riesgo de automatización por industria."""
    raw = (
        df.dropna(subset=["industry", "automation_risk_score"])
        .groupby("industry")["automation_risk_score"]
        .agg(
            n_ofertas="count",
            media_automation_risk_score="mean",
            pct_riesgo_mayor_07=lambda s: (s > AUTOMATION_HIGH_RISK_THRESHOLD).mean() * 100,
        )
        .reset_index()
        .sort_values("media_automation_risk_score", ascending=False)
    )

    formatted = pd.DataFrame(
        {
            "Industria": raw["industry"],
            "Nº de ofertas": raw["n_ofertas"].apply(format_integer_es),
            "Media de automation_risk_score": raw["media_automation_risk_score"].apply(lambda x: format_number_es(x, 3)),
            "% de ofertas con riesgo > 0,7": raw["pct_riesgo_mayor_07"].apply(lambda x: format_percent_es(x, 1)),
        }
    )

    return raw, formatted


def build_table_4(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tabla 4. Distribución del riesgo de desplazamiento por IA según seniority."""
    risk_order_table = ["High", "Medium", "Low"]

    base = df.dropna(
        subset=["seniority_level", "ai_job_displacement_risk", "automation_risk_score"]
    ).copy()

    counts = pd.crosstab(base["seniority_level"], base["ai_job_displacement_risk"])
    counts = counts.reindex(columns=risk_order_table, fill_value=0)

    totals = counts.sum(axis=1)
    mean_risk = base.groupby("seniority_level")["automation_risk_score"].mean()

    raw = counts.copy()
    raw.insert(0, "n_ofertas", totals)
    raw["media_automation_risk_score"] = mean_risk
    raw = raw.reset_index().sort_values("seniority_level")

    formatted_rows = []
    for _, row in raw.iterrows():
        seniority = row["seniority_level"]
        total = int(row["n_ofertas"])
        item = {
            "Nivel de experiencia": seniority,
            "Nº de ofertas": format_integer_es(total),
        }
        for risk in risk_order_table:
            count = int(row[risk])
            pct = count / total * 100 if total else 0
            item[risk] = f"{format_integer_es(count)} ({format_number_es(pct, 1)} %)"
        item["Media de automation_risk_score"] = format_number_es(
            row["media_automation_risk_score"], 3
        )
        formatted_rows.append(item)

    formatted = pd.DataFrame(formatted_rows)

    return raw, formatted


def build_table_5(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Tabla 5. Tabla cruzada entre ai_mentioned y reskilling_required."""
    raw = pd.crosstab(
        df["ai_mentioned"],
        df["reskilling_required"],
        margins=True,
        margins_name="Total",
    )

    # Asegura columnas False y True aunque alguna no existiera.
    for col in [False, True]:
        if col not in raw.columns:
            raw[col] = 0

    raw = raw[[False, True, "Total"]]
    raw = raw.reset_index()

    # Renombra la columna de índice creada por crosstab.
    first_col = raw.columns[0]
    raw = raw.rename(columns={first_col: "ai_mentioned"})

    formatted = pd.DataFrame(
        {
            "ai_mentioned": raw["ai_mentioned"].astype(str),
            "reskilling_required = False": raw[False].apply(format_integer_es),
            "reskilling_required = True": raw[True].apply(format_integer_es),
            "Total": raw["Total"].apply(format_integer_es),
        }
    )

    return raw, formatted


# -----------------------------------------------------------------------------
# FIGURAS
# -----------------------------------------------------------------------------
def build_figure_1(tabla_1_raw: pd.DataFrame) -> None:
    """Figura 1. Salario medio ofertado según mención de IA."""
    plot_data = tabla_1_raw.copy()
    plot_data["label"] = plot_data["ai_mentioned"].map({False: "No menciona IA", True: "Menciona IA"})

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(plot_data["label"], plot_data["salario_medio"])
    ax.set_title("Salario medio ofertado según mención de IA")
    ax.set_xlabel("Mención de IA en la oferta")
    ax.set_ylabel("Salario medio ofertado (USD)")
    annotate_bars(ax, decimals=0, suffix=" $")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "figura_1_salario_medio_ia.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def build_figure_2(tabla_3_raw: pd.DataFrame) -> None:
    """Figura 2. Media de riesgo de automatización por industria."""
    plot_data = tabla_3_raw.sort_values("media_automation_risk_score", ascending=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(plot_data["industry"], plot_data["media_automation_risk_score"])
    ax.set_title("Media de riesgo de automatización por industria")
    ax.set_xlabel("Industria")
    ax.set_ylabel("Media de automation_risk_score")
    ax.set_ylim(0, max(0.75, plot_data["media_automation_risk_score"].max() * 1.15))
    ax.tick_params(axis="x", rotation=30)
    annotate_bars(ax, decimals=3, suffix="")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "figura_2_media_riesgo_automatizacion_industria.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def build_figure_3(tabla_3_raw: pd.DataFrame) -> None:
    """Figura 3. Porcentaje de ofertas con riesgo de automatización superior a 0,7."""
    plot_data = tabla_3_raw.sort_values("pct_riesgo_mayor_07", ascending=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(plot_data["industry"], plot_data["pct_riesgo_mayor_07"])
    ax.set_title("Ofertas con riesgo de automatización superior a 0,7 por industria")
    ax.set_xlabel("Industria")
    ax.set_ylabel("Porcentaje de ofertas (%)")
    ax.set_ylim(0, max(60, plot_data["pct_riesgo_mayor_07"].max() * 1.20))
    ax.tick_params(axis="x", rotation=30)
    annotate_bars(ax, decimals=1, suffix=" %")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "figura_3_porcentaje_alto_riesgo_industria.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def build_figure_4(df: pd.DataFrame) -> None:
    """Figura 4. Distribución porcentual del riesgo de desplazamiento por IA según seniority."""
    risk_order_plot = ["Low", "Medium", "High"]
    base = df.dropna(subset=["seniority_level", "ai_job_displacement_risk"]).copy()

    counts = pd.crosstab(base["seniority_level"], base["ai_job_displacement_risk"])
    counts = counts.reindex(columns=risk_order_plot, fill_value=0)
    counts = counts.sort_index()
    percentages = counts.div(counts.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bottom = np.zeros(len(percentages))

    for risk in risk_order_plot:
        values = percentages[risk].values
        ax.bar(percentages.index, values, bottom=bottom, label=risk)

        # Etiquetas dentro de cada segmento si hay espacio suficiente.
        for i, value in enumerate(values):
            if value >= 7:
                ax.text(
                    i,
                    bottom[i] + value / 2,
                    f"{format_number_es(value, 1)} %",
                    ha="center",
                    va="center",
                    fontsize=8,
                )
        bottom += values

    ax.set_title("Distribución del riesgo de desplazamiento por IA según nivel de experiencia")
    ax.set_xlabel("Nivel de experiencia")
    ax.set_ylabel("Porcentaje de ofertas (%)")
    ax.set_ylim(0, 100)
    ax.legend(title="Riesgo")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "figura_4_riesgo_desplazamiento_seniority.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def build_figure_5(tabla_5_raw: pd.DataFrame) -> None:
    """Figura 5. Relación entre mención de IA y necesidad de reskilling."""
    plot_data = tabla_5_raw[tabla_5_raw["ai_mentioned"].astype(str) != "Total"].copy()
    plot_data["label"] = plot_data["ai_mentioned"].astype(bool).map(
        {False: "ai_mentioned = False", True: "ai_mentioned = True"}
    )

    values_false = plot_data[False].astype(int).values
    values_true = plot_data[True].astype(int).values
    x = np.arange(len(plot_data))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x, values_false, label="reskilling_required = False")
    ax.bar(x, values_true, bottom=values_false, label="reskilling_required = True")

    totals = values_false + values_true
    for i, total in enumerate(totals):
        if values_false[i] > 0:
            ax.text(i, values_false[i] / 2, format_integer_es(values_false[i]), ha="center", va="center", fontsize=9)
        if values_true[i] > 0:
            ax.text(i, values_false[i] + values_true[i] / 2, format_integer_es(values_true[i]), ha="center", va="center", fontsize=9)
        ax.text(i, total, format_integer_es(total), ha="center", va="bottom", fontsize=9)

    ax.set_title("Relación entre mención de IA y necesidad de reskilling")
    ax.set_xlabel("Mención de IA")
    ax.set_ylabel("Número de ofertas")
    ax.set_xticks(x)
    ax.set_xticklabels(plot_data["label"])
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "figura_5_ai_mentioned_reskilling.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# -----------------------------------------------------------------------------
# GUARDADO DE RESULTADOS
# -----------------------------------------------------------------------------
def save_all_tables_to_excel(tables: dict[str, pd.DataFrame]) -> None:
    """Guarda todas las tablas formateadas en un único Excel."""
    try:
        with pd.ExcelWriter(TABLES_DIR / "tablas_6_3.xlsx") as writer:
            for sheet_name, table in tables.items():
                table.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    except Exception as exc:
        warnings.warn(
            "No se pudo crear el Excel. Se guardarán igualmente los CSV y Markdown. "
            f"Detalle: {exc}"
        )


def save_markdown_file(tables: dict[str, pd.DataFrame]) -> None:
    """Guarda todas las tablas en un archivo Markdown para copiar en la memoria."""
    titles = {
        "Tabla_1": "Tabla 1. Salario medio ofertado según mención de IA en la versión GOLD del dataset.",
        "Tabla_2": "Tabla 2. Correlación entre intensidad de IA y salario ofertado.",
        "Tabla_3": "Tabla 3. Riesgo de automatización por industria en la versión GOLD del dataset.",
        "Tabla_4": "Tabla 4. Distribución del riesgo de desplazamiento por IA según nivel de experiencia.",
        "Tabla_5": "Tabla 5. Tabla cruzada entre ai_mentioned y reskilling_required.",
    }

    parts = ["# Tablas del apartado 6.3\n"]
    for key, table in tables.items():
        parts.append(f"## {titles.get(key, key)}\n")
        parts.append(df_to_markdown(table))
        parts.append("\n")

    (TABLES_DIR / "tablas_6_3.md").write_text("\n".join(parts), encoding="utf-8")


def save_summary_text(
    df: pd.DataFrame,
    tabla_1_raw: pd.DataFrame,
    tabla_2_raw: pd.DataFrame,
) -> None:
    """Guarda un pequeño resumen numérico para comprobar los resultados."""
    figures_path = FIGURES_DIR.as_posix()
    tables_path = TABLES_DIR.as_posix()
    table_images_path = TABLE_IMAGES_DIR.as_posix()

    salary_false = tabla_1_raw.loc[tabla_1_raw["ai_mentioned"] == False, "salario_medio"].iloc[0]
    salary_true = tabla_1_raw.loc[tabla_1_raw["ai_mentioned"] == True, "salario_medio"].iloc[0]
    difference = salary_true - salary_false
    percentage = difference / salary_false * 100

    text = f"""Resumen de comprobación del apartado 6.3

Número de registros de la versión GOLD: {format_integer_es(len(df))}

Diferencia de salario medio entre ofertas con IA y sin IA:
- Salario medio sin mención de IA: {format_number_es(salary_false, 2)} USD
- Salario medio con mención de IA: {format_number_es(salary_true, 2)} USD
- Diferencia: {format_number_es(difference, 2)} USD
- Incremento relativo: {format_number_es(percentage, 1)} %

Correlaciones:
- Pearson: {format_number_es(tabla_2_raw.loc[0, 'coeficiente'], 3)} ({pvalue_label(tabla_2_raw.loc[0, 'p_value'])})
- Spearman: {format_number_es(tabla_2_raw.loc[1, 'coeficiente'], 3)} ({pvalue_label(tabla_2_raw.loc[1, 'p_value'])})

Carpetas generadas:
- Figuras: {figures_path}
- Tablas CSV/Excel/Markdown: {tables_path}
- Tablas en PNG: {table_images_path}
"""
    (OUTPUT_DIR / "resumen_comprobacion.txt").write_text(text, encoding="utf-8")


# -----------------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# -----------------------------------------------------------------------------
def main() -> None:
    ensure_output_dirs()

    dataset_path = find_dataset()
    print(f"Cargando dataset: {dataset_path}")

    df = pd.read_csv(dataset_path)
    df = prepare_data(df)

    # Construcción de tablas.
    tabla_1_raw, tabla_1 = build_table_1(df)
    tabla_2_raw, tabla_2 = build_table_2(df)
    tabla_3_raw, tabla_3 = build_table_3(df)
    tabla_4_raw, tabla_4 = build_table_4(df)
    tabla_5_raw, tabla_5 = build_table_5(df)

    formatted_tables = {
        "Tabla_1": tabla_1,
        "Tabla_2": tabla_2,
        "Tabla_3": tabla_3,
        "Tabla_4": tabla_4,
        "Tabla_5": tabla_5,
    }

    # Guardado de tablas.
    save_table_csv(tabla_1, "tabla_1_salario_mencion_ia.csv")
    save_table_csv(tabla_2, "tabla_2_correlacion_intensidad_ia_salario.csv")
    save_table_csv(tabla_3, "tabla_3_riesgo_automatizacion_industria.csv")
    save_table_csv(tabla_4, "tabla_4_riesgo_desplazamiento_seniority.csv")
    save_table_csv(tabla_5, "tabla_5_ai_mentioned_reskilling.csv")

    save_all_tables_to_excel(formatted_tables)
    save_markdown_file(formatted_tables)

    # Guardado opcional de imágenes de las tablas.
    save_table_image(tabla_1, "tabla_1_salario_mencion_ia.png", "Tabla 1. Salario medio ofertado según mención de IA")
    save_table_image(tabla_2, "tabla_2_correlacion.png", "Tabla 2. Correlación entre intensidad de IA y salario ofertado")
    save_table_image(tabla_3, "tabla_3_riesgo_industria.png", "Tabla 3. Riesgo de automatización por industria")
    save_table_image(tabla_4, "tabla_4_riesgo_seniority.png", "Tabla 4. Riesgo de desplazamiento por nivel de experiencia")
    save_table_image(tabla_5, "tabla_5_reskilling.png", "Tabla 5. Tabla cruzada entre ai_mentioned y reskilling_required")

    # Construcción de figuras.
    build_figure_1(tabla_1_raw)
    build_figure_2(tabla_3_raw)
    build_figure_3(tabla_3_raw)
    build_figure_4(df)
    build_figure_5(tabla_5_raw)

    # Resumen de comprobación.
    save_summary_text(df, tabla_1_raw, tabla_2_raw)

    print("\nProceso completado correctamente.")
    print(f"Tablas guardadas en: {TABLES_DIR.resolve()}")
    print(f"Figuras guardadas en: {FIGURES_DIR.resolve()}")
    if SAVE_TABLE_IMAGES:
        print(f"Tablas en PNG guardadas en: {TABLE_IMAGES_DIR.resolve()}")
    print(f"Resumen: {(OUTPUT_DIR / 'resumen_comprobacion.txt').resolve()}")


if __name__ == "__main__":
    main()
