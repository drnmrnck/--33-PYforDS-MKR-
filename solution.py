"""МКР з Python for Data Science — наскрізний кейс «Метеослужба».

ШАБЛОН ДЛЯ СТУДЕНТА. Заповніть кожен пункт у блоках 1–4 та допишіть
ВИСНОВКИ у docstring наприкінці файлу.

Перед запуском скрипта підніміть СВІЙ Docker-контейнер з MySQL:

    docker pull <DOCKER_USER>/pfds-mkr-g<N>-<NN>
    docker run -d -p 3306:3306 --name mkr <DOCKER_USER>/pfds-mkr-g<N>-<NN>

(g<N>-<NN> — ваші група і номер у журналі, видається викладачем)

Потім чекайте ~30 секунд на ініціалізацію MySQL і запускайте:

    python solution.py

Графіки зберігаються в підпапку `plots/` поряд зі скриптом.
"""

# ====================================================================
# Прізвище, ім'я, по батькові: ____________________________________
# Група:                       ____________________________________
# Дата виконання:              ____________________________________
# ====================================================================

import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

DB_USER = "student"
DB_PASSWORD = "student"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "meteo"

PLOTS_DIR = Path("plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def section(title: str) -> None:
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


def load_observations(retries: int = 12, delay: float = 2.5) -> pd.DataFrame:
    """Підключитися до MySQL і завантажити таблицю observations.

    MySQL-контейнер на старті виконує LOAD DATA INFILE, що займає
    ~20–30 секунд. Тому робимо retry-цикл — перші спроби очікувано
    падають з OperationalError (server not ready).
    """
    url = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    engine = create_engine(url)
    for attempt in range(1, retries + 1):
        try:
            df = pd.read_sql("SELECT * FROM observations", engine)
            print(f"Підключено до MySQL з {attempt}-ї спроби. Рядків: {len(df)}")
            return df
        except OperationalError:
            if attempt == retries:
                raise
            print(f"  MySQL ще не готова (спроба {attempt}/{retries})...")
            time.sleep(delay)
    raise RuntimeError("Unreachable")


# ====================================================================
# БЛОК 1. NumPy (15 балів)
# ====================================================================
# Працюємо з СИРИМИ даними (до очищення в Pandas). Використовуємо
# тільки numpy-арифметику, без pandas-арифметики.

def block_1_numpy(df_raw: pd.DataFrame) -> None:
    section("БЛОК 1. NumPy")

    # 1) Побудувати np.array apparent temperature за формулою:
    #    T_app = T - (100 - RH) / 5
    #    Працюйте з temperature_c і humidity_pct як з np.array.
    # TODO:
    apparent = ...
    print(f"1) T_app: len={...}, min={...:.2f}, max={...:.2f}")

    # 2) Замінити викидні значення:
    #    - temperature_c > 60 або < -60   -> np.nan
    #    - wind_speed_ms > 100            -> np.nan
    #    Використати np.where.
    # TODO:
    temperature_clean = ...
    wind_clean = ...
    print(f"2) Викидів температури замінено: {...}")
    print(f"   Викидів вітру замінено:       {...}")

    # 3) Порахувати mean / median / std температури ВРУЧНУ
    #    (без pandas .describe(), ігноруючи NaN). Дозволені np.nansum,
    #    np.nanmedian, np.sqrt, маски тощо.
    # TODO:
    mean_t = ...
    median_t = ...
    std_t = ...
    print(f"3) mean={mean_t:.3f}  median={median_t:.3f}  std={std_t:.3f}")

    # 4) Маска: скільки спостережень "морозних" (T<0) і "жарких" (T>30).
    # TODO:
    n_frost = ...
    n_hot = ...
    print(f"4) морозних: {n_frost}    жарких: {n_hot}")

    # 5) argmax / argmin температури -> повернути obs_id і datetime
    #    цих рядків. Підказка: np.nanargmax / np.nanargmin.
    # TODO:
    pass


# ====================================================================
# БЛОК 2. Pandas — очищення (20 балів)
"""МКР з Python for Data Science — кейс «Метеослужба»."""

import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


DB_USER = "student"
DB_PASSWORD = "student"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "meteo"

PLOTS_DIR = Path("plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def section(title: str) -> None:
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


def load_observations(retries: int = 12, delay: float = 2.5) -> pd.DataFrame:
    url = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    engine = create_engine(url)

    for attempt in range(1, retries + 1):
        try:
            df = pd.read_sql("SELECT * FROM observations", engine)
            print(f"Підключено до MySQL з {attempt}-ї спроби. Рядків: {len(df)}")
            return df
        except OperationalError:
            if attempt == retries:
                raise
            print(f"MySQL ще не готова: спроба {attempt}/{retries}")
            time.sleep(delay)

    raise RuntimeError("Не вдалося підключитися до MySQL")


def block_1_numpy(df_raw: pd.DataFrame) -> None:
    section("БЛОК 1. NumPy")

    temperature = df_raw["temperature_c"].to_numpy(dtype=float)
    humidity = df_raw["humidity_pct"].to_numpy(dtype=float)
    wind = df_raw["wind_speed_ms"].to_numpy(dtype=float)

    apparent = temperature - (100 - humidity) / 5

    print(
        f"1) T_app: len={len(apparent)}, "
        f"min={np.nanmin(apparent):.2f}, "
        f"max={np.nanmax(apparent):.2f}"
    )

    temp_outlier_mask = (temperature > 60) | (temperature < -60)
    wind_outlier_mask = wind > 100

    temperature_clean = np.where(temp_outlier_mask, np.nan, temperature)
    wind_clean = np.where(wind_outlier_mask, np.nan, wind)

    print(f"2) Викидів температури замінено: {np.sum(temp_outlier_mask)}")
    print(f"   Викидів вітру замінено:       {np.sum(wind_outlier_mask)}")

    valid_temp = temperature_clean[~np.isnan(temperature_clean)]
    count_valid = valid_temp.size

    mean_t = np.nansum(temperature_clean) / count_valid
    median_t = np.nanmedian(temperature_clean)
    std_t = np.sqrt(np.nansum((temperature_clean - mean_t) ** 2) / count_valid)

    print(f"3) mean={mean_t:.3f}  median={median_t:.3f}  std={std_t:.3f}")

    n_frost = int(np.sum(temperature_clean < 0))
    n_hot = int(np.sum(temperature_clean > 30))

    print(f"4) морозних: {n_frost}    жарких: {n_hot}")

    max_idx = int(np.nanargmax(temperature_clean))
    min_idx = int(np.nanargmin(temperature_clean))

    max_row = df_raw.iloc[max_idx]
    min_row = df_raw.iloc[min_idx]

    print(
        "5) Максимальна температура: "
        f"obs_id={max_row['obs_id']}, datetime={max_row['datetime']}, "
        f"T={temperature_clean[max_idx]:.2f}"
    )
    print(
        "   Мінімальна температура: "
        f"obs_id={min_row['obs_id']}, datetime={min_row['datetime']}, "
        f"T={temperature_clean[min_idx]:.2f}"
    )


def block_2_cleaning(df_raw: pd.DataFrame) -> pd.DataFrame:
    section("БЛОК 2. Pandas — очищення")

    rows_before = len(df_raw)
    df = df_raw.copy()

    print("1) Типи колонок:")
    print(df.info())

    print("\nОпис числових колонок:")
    print(df.describe().round(2).to_string())

    df["datetime"] = pd.to_datetime(df["datetime"])

    before_duplicates = len(df)
    df = df.drop_duplicates()
    n_dups = before_duplicates - len(df)

    df = df.set_index("datetime").sort_index()

    before_fill = int(df["humidity_pct"].isna().sum())

    df["month"] = df.index.month
    df["humidity_pct"] = (
        df.groupby(["city", "month"])["humidity_pct"]
        .transform(lambda s: s.fillna(s.median()))
    )

    after_fill = int(df["humidity_pct"].isna().sum())
    n_filled = before_fill - after_fill

    before_outliers = len(df)

    temperature_mask = df["temperature_c"].between(-60, 60, inclusive="both")
    wind_mask = df["wind_speed_ms"].isna() | df["wind_speed_ms"].between(0, 60, inclusive="both")

    df = df[temperature_mask & wind_mask].copy()

    n_outliers = before_outliers - len(df)

    df = df.drop(columns=["month"])

    print(f"2) drop_duplicates: видалено {n_dups}")
    print(f"3) Заповнено NaN humidity_pct: {n_filled}")
    print(f"4) Видалено фізичних викидів: {n_outliers}")

    print(f"\n   Звіт очищення: {rows_before} → {len(df)} рядків")
    print(f"   Видалено дублів: {n_dups}")
    print(f"   Заповнено NaN humidity_pct: {n_filled}")
    print(f"   Видалено фізичних викидів: {n_outliers}")

    return df


def block_3_analytics(df: pd.DataFrame) -> dict:
    section("БЛОК 3. Pandas — аналітика")

    by_city_temp = df.groupby("city")["temperature_c"].mean().sort_values(ascending=False)

    warmest_city = by_city_temp.idxmax()
    coldest_city = by_city_temp.idxmin()

    print("1) Середня T по містах:")
    print(by_city_temp.round(2).to_string())
    print(f"   Найтепліше місто: {warmest_city}")
    print(f"   Найхолодніше місто: {coldest_city}")

    by_city_precip = df.groupby("city")["precipitation_mm"].sum().sort_values(ascending=False)
    wettest_city = by_city_precip.idxmax()

    print("\n2) Сумарні опади по містах:")
    print(by_city_precip.round(1).to_string())
    print(f"   Найвологіше місто: {wettest_city}")

    try:
        monthly_mean = df["temperature_c"].resample("ME").mean()
    except ValueError:
        monthly_mean = df["temperature_c"].resample("M").mean()

    print(f"\n3) Місячна середня T ({len(monthly_mean)} точок):")
    print(monthly_mean.round(2).to_string())

    df_for_pivot = df.copy()
    df_for_pivot["month"] = df_for_pivot.index.month

    pivot = pd.pivot_table(
        df_for_pivot,
        values="temperature_c",
        index="city",
        columns="month",
        aggfunc="mean",
    )

    print("\n4) Pivot місто × місяць:")
    print(pivot.round(1).to_string())

    daily_precip = (
        df.groupby("city")
        .resample("D")["precipitation_mm"]
        .sum()
        .reset_index()
    )

    rainy_days = (
        daily_precip[daily_precip["precipitation_mm"] > 5]
        .groupby("city")
        .size()
        .sort_values(ascending=False)
    )

    print("\n5) Дні з опадами > 5 мм:")
    print(rainy_days.to_string())

    anomaly_df = monthly_mean.reset_index()
    anomaly_df["year"] = anomaly_df["datetime"].dt.year
    anomaly_df["month"] = anomaly_df["datetime"].dt.month
    anomaly_df = anomaly_df.rename(columns={"temperature_c": "monthly_temperature"})

    anomaly_df["norm"] = anomaly_df.groupby("month")["monthly_temperature"].transform("mean")
    anomaly_df["deviation"] = anomaly_df["monthly_temperature"] - anomaly_df["norm"]
    anomaly_df["abs_deviation"] = anomaly_df["deviation"].abs()

    anomaly_row = anomaly_df.loc[anomaly_df["abs_deviation"].idxmax()]
    anomaly_month = f"{int(anomaly_row['year'])}-{int(anomaly_row['month']):02d}"
    anomaly_dev = float(anomaly_row["deviation"])
    anomaly_type = "хвиля спеки" if anomaly_dev > 0 else "холодна хвиля"

    print(
        f"\n6) Аномальний місяць: {anomaly_month}  "
        f"відхилення = {anomaly_dev:+.2f}°C — {anomaly_type}"
    )

    region_std = df.groupby("region")["temperature_c"].std().sort_values()
    most_stable_region = region_std.idxmin()

    print("\nДодатково: стандартне відхилення температури по регіонах:")
    print(region_std.round(2).to_string())
    print(f"Найстабільніший за температурою регіон: {most_stable_region}")

    return {
        "by_city_temp": by_city_temp,
        "by_city_precip": by_city_precip,
        "monthly_mean": monthly_mean,
        "pivot": pivot,
        "rainy_days": rainy_days,
        "anomaly_month": anomaly_month,
        "anomaly_dev": anomaly_dev,
        "anomaly_type": anomaly_type,
        "region_std": region_std,
        "most_stable_region": most_stable_region,
    }


def block_4_plots(df: pd.DataFrame, analytics: dict) -> None:
    section("БЛОК 4. Matplotlib")

    cities = sorted(df["city"].dropna().unique())[:3]

    try:
        monthly_by_city = (
            df[df["city"].isin(cities)]
            .groupby("city")
            .resample("ME")["temperature_c"]
            .mean()
            .reset_index()
        )
    except ValueError:
        monthly_by_city = (
            df[df["city"].isin(cities)]
            .groupby("city")
            .resample("M")["temperature_c"]
            .mean()
            .reset_index()
        )

    fig, ax = plt.subplots(figsize=(11, 5))

    for city in cities:
        city_data = monthly_by_city[monthly_by_city["city"] == city]
        ax.plot(city_data["datetime"], city_data["temperature_c"], marker="o", label=city)

    ax.set_title("Monthly temperature dynamics in selected cities")
    ax.set_xlabel("Month")
    ax.set_ylabel("Average temperature, °C")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.autofmt_xdate()
    fig.savefig(PLOTS_DIR / "01_monthly_temperature_lines.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))

    analytics["by_city_precip"].plot(kind="bar", ax=ax)

    ax.set_title("Total precipitation by city")
    ax.set_xlabel("City")
    ax.set_ylabel("Total precipitation, mm")
    ax.grid(True, axis="y", alpha=0.3)

    fig.savefig(PLOTS_DIR / "02_precipitation_by_city.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

    temperature = df["temperature_c"].dropna()
    mean_t = temperature.mean()
    median_t = temperature.median()

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.hist(temperature, bins=30, edgecolor="black", alpha=0.7)
    ax.axvline(mean_t, linestyle="--", linewidth=2, label=f"Mean: {mean_t:.2f}")
    ax.axvline(median_t, linestyle="-", linewidth=2, label=f"Median: {median_t:.2f}")

    ax.set_title("Temperature distribution")
    ax.set_xlabel("Temperature, °C")
    ax.set_ylabel("Frequency")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)

    fig.savefig(PLOTS_DIR / "03_temperature_histogram.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

    pivot = analytics["pivot"]

    fig, ax = plt.subplots(figsize=(11, 5))

    image = ax.imshow(pivot.values, aspect="auto")
    ax.set_title("Average temperature heatmap: city × month")
    ax.set_xlabel("Month")
    ax.set_ylabel("City")

    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)

    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    colorbar = fig.colorbar(image, ax=ax)
    colorbar.set_label("Average temperature, °C")

    fig.savefig(PLOTS_DIR / "04_city_month_heatmap.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

    print(f"4 графіки збережені в папку {PLOTS_DIR}/")


def main() -> None:
    df_raw = load_observations()
    print(f"Завантажено: shape={df_raw.shape}")

    block_1_numpy(df_raw)
    df_clean = block_2_cleaning(df_raw)
    analytics = block_3_analytics(df_clean)
    block_4_plots(df_clean, analytics)


if __name__ == "__main__":
    main()


"""
ВИСНОВКИ.

У межах роботи було виконано повний цикл аналізу метеорологічних даних:
завантаження з MySQL, первинний NumPy-аналіз, очищення набору даних,
агрегацію показників у Pandas і побудову графіків у Matplotlib.
Найтепліше та найхолодніше місто визначаються за середньою температурою
після очищення даних від дублів і фізично неможливих значень.
Сезонність у наборі даних простежується через місячну динаміку температури:
у теплі місяці середні значення зростають, а в холодні — знижуються.
Аномальний місяць визначається як місяць із найбільшим абсолютним відхиленням
від кліматичної норми для відповідного календарного місяця за два роки.
Якщо відхилення додатне, його можна інтерпретувати як хвилю спеки, якщо
від’ємне — як холодну хвилю.
Найстабільніший регіон визначається за найменшим стандартним відхиленням
температури, оскільки менша варіативність означає рівномірніший температурний режим.
Практично такі результати можна використовувати для підготовки кліматичних
звітів, планування міської інфраструктури й оцінювання ризиків, пов’язаних
із температурними аномаліями та інтенсивними опадами.
"""
