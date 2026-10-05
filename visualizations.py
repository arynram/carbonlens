"""
visualizations.py
-----------------
Matplotlib visualization module for the Carbon-Aware Electricity Production Analysis.

Contains functions for the 11 designated project visualizations:
1. Energy Source Production — Bar Chart
2. Monthly CO2e Production — Line Chart
3. Source-wise CO2e Contribution — Bar Chart
4. Renewable vs Non-renewable Mix — Pie Chart
5. Year-wise CO2e Comparison — Bar Chart
6. CO2e Intensity by Year — Line Chart
7. Historical vs Low-Carbon Energy Mix — Stacked Bar Chart
8. Historical Average CO2e vs Low-Carbon Scenario — Bar Chart
9. Histogram — EDA (Distribution of Production)
10. Boxplot — EDA (Variability & Outliers across Energy Sources)
11. Scatterplot — EDA (Electricity Consumption vs Production)
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

# Standard styling defaults for clean academic charts
plt.rcParams.update({
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 13,
})

# Harmonious, intuitive color palette by energy source
SOURCE_COLORS = {
    "Coal": "#495057",          # Dark Slate Gray
    "Oil and Gas": "#e67e22",   # Combustion Amber
    "Biomass": "#27ae60",       # Bio Green
    "Solar": "#f1c40f",         # Solar Gold
    "Hydroelectric": "#2980b9", # Water Blue
    "Nuclear": "#8e44ad",       # Nuclear Violet
    "Wind": "#1abc9c",          # Wind Teal
}

CATEGORY_COLORS = {
    "Renewable": "#2ecc71",     # Vibrant Green
    "Non-Renewable": "#e74c3c", # Crimson Red
}


# ==============================================================================
# 1. Energy Source Production — Bar Chart
# ==============================================================================
def plot_source_production_bar(source_df: pd.DataFrame, year: int) -> plt.Figure:
    """Graph 1: Bar chart showing electricity production per energy source."""
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=100)
    
    df_sorted = source_df.sort_values("Production (MWh)", ascending=True)
    sources = df_sorted["Energy Source"]
    prod_gwh = df_sorted["Production (MWh)"] / 1000.0  # Convert to GWh for readable labels
    colors = [SOURCE_COLORS.get(s, "#34495e") for s in sources]

    bars = ax.barh(sources, prod_gwh, color=colors, edgecolor="black", linewidth=0.6, alpha=0.9)
    
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width * 1.01,
            bar.get_y() + bar.get_height() / 2,
            f"{width:,.0f} GWh",
            va="center",
            ha="left",
            fontsize=8.5,
            color="#2c3e50",
            fontweight="bold",
        )

    ax.set_title(f"Electricity Production by Energy Source — Year {year}", pad=12, fontweight="bold")
    ax.set_xlabel("Total Generation (GWh = 1,000 MWh)")
    ax.set_ylabel("Energy Source")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    
    max_val = prod_gwh.max() if not prod_gwh.empty else 100
    ax.set_xlim(0, max_val * 1.18)
    
    fig.tight_layout()
    return fig


# ==============================================================================
# 2. Monthly CO2e Production — Line Chart
# ==============================================================================
def plot_monthly_co2_line(monthly_df: pd.DataFrame, year: int) -> plt.Figure:
    """Graph 2: Line chart showing estimated monthly CO2e emissions across the year."""
    fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=100)

    x = monthly_df["Month_Name"]
    co2_col = "Estimated_CO2e_Tonnes" if "Estimated_CO2e_Tonnes" in monthly_df.columns else "Estimated_CO2_Tonnes"
    y_kt = monthly_df[co2_col] / 1000.0  # Kilotonnes (kt)

    ax.plot(x, y_kt, marker="o", color="#c0392b", linewidth=2.2, markersize=6, label="Estimated CO2e (kt)")
    ax.fill_between(x, y_kt, color="#e74c3c", alpha=0.15)

    for i, val in enumerate(y_kt):
        ax.annotate(
            f"{val:,.0f}",
            (x.iloc[i], val),
            textcoords="offset points",
            xytext=(0, 7),
            ha="center",
            fontsize=8,
            color="#962d22",
            fontweight="bold",
        )

    ax.set_title(f"Monthly Estimated CO2e Emissions Trend — Year {year}", pad=12, fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Estimated CO2e Emissions (Kilotonnes / kt)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    
    y_max = y_kt.max() if not y_kt.empty else 10
    ax.set_ylim(0, y_max * 1.18)

    fig.tight_layout()
    return fig


# ==============================================================================
# 3. Source-wise CO2e Contribution — Bar Chart
# ==============================================================================
def plot_source_co2_bar(source_df: pd.DataFrame, year: int) -> plt.Figure:
    """Graph 3: Bar chart showing estimated CO2e contribution by energy source."""
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=100)

    co2_col = "Estimated CO2e (Tonnes)" if "Estimated CO2e (Tonnes)" in source_df.columns else "Estimated CO2 (Tonnes)"
    df_sorted = source_df.sort_values(co2_col, ascending=True)
    sources = df_sorted["Energy Source"]
    co2_kt = df_sorted[co2_col] / 1000.0  # Kilotonnes (kt)
    colors = [SOURCE_COLORS.get(s, "#7f8c8d") for s in sources]

    bars = ax.barh(sources, co2_kt, color=colors, edgecolor="black", linewidth=0.6, alpha=0.9)

    for bar in bars:
        width = bar.get_width()
        ax.text(
            width * 1.01,
            bar.get_y() + bar.get_height() / 2,
            f"{width:,.1f} kt",
            va="center",
            ha="left",
            fontsize=8.5,
            color="#2c3e50",
            fontweight="bold",
        )

    ax.set_title(f"Source-Wise Estimated CO2e Contribution — Year {year}", pad=12, fontweight="bold")
    ax.set_xlabel("Estimated Emissions (Kilotonnes CO2e)")
    ax.set_ylabel("Energy Source")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    max_val = co2_kt.max() if not co2_kt.empty else 10
    ax.set_xlim(0, max_val * 1.20)

    fig.tight_layout()
    return fig


# ==============================================================================
# 4. Renewable vs Non-renewable Production — Pie Chart
# ==============================================================================
def plot_renewable_mix_pie(renew_pct: float, non_renew_pct: float, year: int) -> plt.Figure:
    """Graph 4: Pie chart displaying the renewable vs non-renewable generation mix."""
    fig, ax = plt.subplots(figsize=(6, 4.2), dpi=100)

    labels = ["Renewable", "Non-Renewable"]
    sizes = [renew_pct, non_renew_pct]
    colors = [CATEGORY_COLORS["Renewable"], CATEGORY_COLORS["Non-Renewable"]]
    explode = (0.05, 0.0)

    wedges, texts, autotexts = ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        wedgeprops=dict(edgecolor="black", linewidth=0.8),
        textprops=dict(color="#2c3e50", fontsize=10, fontweight="bold"),
    )

    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(11)
        at.set_weight("bold")

    ax.set_title(f"Electricity Production Mix ({year})\nRenewable vs Non-Renewable", pad=10, fontweight="bold")
    fig.tight_layout()
    return fig


# ==============================================================================
# 5. Year-wise Total CO2e — Bar Chart
# ==============================================================================
def plot_year_co2_bar(multi_year_df: pd.DataFrame) -> plt.Figure:
    """Graph 5: Bar chart comparing total estimated CO2e emissions across years."""
    fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=100)

    years = [str(int(y)) for y in multi_year_df["Year"]]
    co2_col = "Total CO2e (Tonnes)" if "Total CO2e (Tonnes)" in multi_year_df.columns else "Total CO2 (Tonnes)"
    co2_mt = multi_year_df[co2_col] / 1_000_000.0  # Megatonnes (Mt)

    colors = ["#e74c3c" if "Partial" not in s else "#f39c12" for s in multi_year_df["Data Status"]]
    bars = ax.bar(years, co2_mt, color=colors, edgecolor="black", linewidth=0.7, width=0.55, alpha=0.88)

    for bar, status in zip(bars, multi_year_df["Data Status"]):
        height = bar.get_height()
        label_text = f"{height:.2f} Mt"
        if "Partial" in status:
            label_text += " *"
            bar.set_hatch("//")

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + (co2_mt.max() * 0.02),
            label_text,
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
            color="#2c3e50",
        )

    ax.set_title("Annual Estimated CO2e Emissions Comparison (* = Partial Year)", pad=12, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Estimated CO2e (Megatonnes / Mt)")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    max_val = co2_mt.max() if not co2_mt.empty else 10
    ax.set_ylim(0, max_val * 1.18)

    fig.tight_layout()
    return fig


# ==============================================================================
# 6. CO2e Intensity by Year — Line Chart
# ==============================================================================
def plot_co2_intensity_line(multi_year_df: pd.DataFrame) -> plt.Figure:
    """Graph 6: Line chart comparing CO2e intensity (kgCO2e / MWh) across years."""
    fig, ax = plt.subplots(figsize=(8.5, 4.3), dpi=100)

    years = [str(int(y)) for y in multi_year_df["Year"]]
    intensity_col = "CO2e Intensity (kgCO2e/MWh)" if "CO2e Intensity (kgCO2e/MWh)" in multi_year_df.columns else "CO2 Intensity (kg CO2/MWh)"
    intensity = multi_year_df[intensity_col]

    ax.plot(years, intensity, marker="s", color="#2980b9", linewidth=2.2, markersize=7, label="CO2e Intensity")
    ax.fill_between(years, intensity, color="#3498db", alpha=0.15)

    for i, val in enumerate(intensity):
        status = multi_year_df["Data Status"].iloc[i]
        note = " *" if "Partial" in status else ""
        ax.annotate(
            f"{val:.1f} kg/MWh{note}",
            (years[i], val),
            textcoords="offset points",
            xytext=(0, 8),
            ha="center",
            fontsize=8.5,
            fontweight="bold",
            color="#1b4f72",
        )

    ax.set_title("Carbon Intensity of Electricity Production (kgCO2e / MWh)", pad=12, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("CO2e Intensity (kgCO2e / MWh = gCO2e / kWh)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    y_max = intensity.max() if not intensity.empty else 300
    ax.set_ylim(0, y_max * 1.25)

    fig.tight_layout()
    return fig


# ==============================================================================
# Multi-Year Renewable vs Non-Renewable Comparison Bar Chart
# ==============================================================================
def plot_renewable_comparison_bar(multi_year_df: pd.DataFrame) -> plt.Figure:
    """Stacked bar chart showing renewable vs non-renewable share percentages across years."""
    fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=100)

    years = [str(int(y)) for y in multi_year_df["Year"]]
    renew_pct = multi_year_df["Renewable (%)"]
    non_renew_pct = multi_year_df["Non-Renewable (%)"]

    width = 0.55
    ax.bar(years, renew_pct, width=width, label="Renewable (%)", color=CATEGORY_COLORS["Renewable"], edgecolor="black", linewidth=0.6)
    ax.bar(years, non_renew_pct, width=width, bottom=renew_pct, label="Non-Renewable (%)", color=CATEGORY_COLORS["Non-Renewable"], edgecolor="black", linewidth=0.6)

    for i in range(len(years)):
        r = renew_pct.iloc[i]
        nr = non_renew_pct.iloc[i]
        if r > 10:
            ax.text(i, r / 2, f"{r:.1f}%", ha="center", va="center", color="white", fontweight="bold", fontsize=8.5)
        if nr > 10:
            ax.text(i, r + (nr / 2), f"{nr:.1f}%", ha="center", va="center", color="white", fontweight="bold", fontsize=8.5)

    ax.set_title("Renewable vs Non-Renewable Electricity Share by Year", pad=12, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Share of Electricity Production (%)")
    ax.set_ylim(0, 100)
    ax.legend(loc="upper right", framealpha=0.9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    fig.tight_layout()
    return fig


# ==============================================================================
# 7. Historical vs Low-Carbon Energy Mix — Stacked Bar Chart
# ==============================================================================
def plot_scenario_mix_stacked_bar(mix_df: pd.DataFrame, month_name: str, future_year: int) -> plt.Figure:
    """Graph 7: 100% stacked bar chart comparing historical average mix vs proposed scenario mix."""
    fig, ax = plt.subplots(figsize=(7.5, 5), dpi=100)

    scenarios = [f"Historical Avg\n({month_name})", f"Low-Carbon Scenario\n({month_name} {future_year})"]

    hist_bottom = 0.0
    scen_bottom = 0.0

    for _, row in mix_df.iterrows():
        src = row["Energy Source"]
        h_val = row["Historical Average Share (%)"]
        s_val = row["Estimated Scenario Share (%)"]
        color = SOURCE_COLORS.get(src, "#7f8c8d")

        ax.bar(scenarios[0], h_val, bottom=hist_bottom, width=0.45, color=color, edgecolor="black", linewidth=0.5, label=src)
        if h_val > 4.5:
            ax.text(0, hist_bottom + h_val / 2, f"{src}\n{h_val:.1f}%", ha="center", va="center", color="white", fontsize=7.5, fontweight="bold")

        ax.bar(scenarios[1], s_val, bottom=scen_bottom, width=0.45, color=color, edgecolor="black", linewidth=0.5)
        if s_val > 4.5:
            ax.text(1, scen_bottom + s_val / 2, f"{src}\n{s_val:.1f}%", ha="center", va="center", color="white", fontsize=7.5, fontweight="bold")

        hist_bottom += h_val
        scen_bottom += s_val

    ax.set_title(f"Historical vs Proposed Energy Mix ({month_name} {future_year})", pad=12, fontweight="bold")
    ax.set_ylabel("Electricity Production Mix Share (%)")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    ax.legend(title="Energy Source", bbox_to_anchor=(1.02, 1), loc="upper left", framealpha=0.9)

    fig.tight_layout()
    return fig


# ==============================================================================
# 8. Historical Average CO2e vs Low-Carbon Scenario — Bar Chart
# ==============================================================================
def plot_scenario_co2_bar(hist_co2_kg: float, scenario_co2_kg: float, month_name: str, future_year: int) -> plt.Figure:
    """Graph 8: Bar chart contrasting historical average CO2e with the low-carbon scenario."""
    fig, ax = plt.subplots(figsize=(6.5, 4.5), dpi=100)

    labels = [f"Historical Baseline\n({month_name} Avg)", f"Low-Carbon Scenario\n({month_name} {future_year})"]
    co2_kt = [hist_co2_kg / 1000.0, scenario_co2_kg / 1000.0]  # Tonnes
    colors = ["#e74c3c", "#27ae60"]

    bars = ax.bar(labels, co2_kt, color=colors, edgecolor="black", linewidth=0.8, width=0.48, alpha=0.9)

    reduction_kt = (hist_co2_kg - scenario_co2_kg) / 1000.0
    reduction_pct = ((hist_co2_kg - scenario_co2_kg) / hist_co2_kg) * 100.0 if hist_co2_kg > 0 else 0.0

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height * 0.5,
            f"{height:,.0f} Tonnes",
            ha="center",
            va="center",
            color="white",
            fontsize=10,
            fontweight="bold",
        )

    ax.text(
        0.5,
        max(co2_kt) * 1.05,
        f"Avoided: {reduction_kt:,.0f} Tonnes (-{reduction_pct:.1f}%)",
        ha="center",
        va="bottom",
        fontsize=9.5,
        fontweight="bold",
        color="#27ae60",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#e8f8f5", edgecolor="#27ae60", alpha=0.9),
    )

    ax.set_title(f"Estimated CO2e Reduction Potential: {month_name} {future_year}", pad=14, fontweight="bold")
    ax.set_ylabel("Estimated CO2e Emissions (Metric Tonnes)")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    ax.set_ylim(0, max(co2_kt) * 1.22)
    fig.tight_layout()
    return fig


# ==============================================================================
# 9. Histogram — EDA
# ==============================================================================
def plot_eda_histogram(df: pd.DataFrame) -> plt.Figure:
    """Graph 9: Histogram showing the distribution of hourly electricity production values."""
    fig, ax = plt.subplots(figsize=(8, 4.3), dpi=100)

    data = df["Production"].dropna()
    n, bins, patches = ax.hist(data, bins=35, color="#3498db", edgecolor="black", linewidth=0.6, alpha=0.85)

    mean_val = float(data.mean())
    median_val = float(data.median())

    ax.axvline(mean_val, color="#e74c3c", linestyle="--", linewidth=1.8, label=f"Mean: {mean_val:,.0f} MWh")
    ax.axvline(median_val, color="#2ecc71", linestyle="-.", linewidth=1.8, label=f"Median: {median_val:,.0f} MWh")

    ax.set_title("EDA: Distribution of Hourly Electricity Production (MWh)", pad=12, fontweight="bold")
    ax.set_xlabel("Hourly Production (MWh)")
    ax.set_ylabel("Frequency (Hours)")
    ax.legend(loc="upper right", framealpha=0.9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    fig.tight_layout()
    return fig


# ==============================================================================
# 10. Boxplot — EDA
# ==============================================================================
def plot_eda_boxplot(df: pd.DataFrame, sources: list[str]) -> plt.Figure:
    """Graph 10: Boxplot showing production variability and outliers across energy sources."""
    fig, ax = plt.subplots(figsize=(9, 4.6), dpi=100)

    valid_sources = [s for s in sources if s in df.columns]
    data_list = [df[s].dropna() for s in valid_sources]

    box = ax.boxplot(
        data_list,
        tick_labels=valid_sources,
        patch_artist=True,
        showmeans=True,
        meanline=True,
        flierprops=dict(marker="o", markersize=3, alpha=0.25, markeredgecolor="#7f8c8d"),
    )

    for patch, src in zip(box["boxes"], valid_sources):
        patch.set_facecolor(SOURCE_COLORS.get(src, "#bdc3c7"))
        patch.set_alpha(0.8)
        patch.set_edgecolor("black")

    for median in box["medians"]:
        median.set(color="black", linewidth=1.2)

    for mean in box["means"]:
        mean.set(color="#c0392b", linewidth=1.4, linestyle="--")

    ax.set_title("EDA: Energy Source Production Variability & Outliers (Boxplot)", pad=12, fontweight="bold")
    ax.set_xlabel("Energy Source")
    ax.set_ylabel("Hourly Production (MWh)")
    ax.tick_params(axis="x", rotation=18)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    fig.tight_layout()
    return fig


# ==============================================================================
# 11. Scatterplot — EDA
# ==============================================================================
def plot_eda_scatterplot(df: pd.DataFrame) -> plt.Figure:
    """Graph 11: Scatterplot showing electricity consumption vs production relationship."""
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=100)

    plot_data = df[["Consumption", "Production"]].dropna()
    if len(plot_data) > 2500:
        plot_sample = plot_data.sample(n=2500, random_state=42)
    else:
        plot_sample = plot_data

    ax.scatter(
        plot_sample["Consumption"],
        plot_sample["Production"],
        alpha=0.35,
        s=14,
        color="#2980b9",
        edgecolors="none",
        label="Hourly Observations",
    )

    min_val = min(plot_sample["Consumption"].min(), plot_sample["Production"].min())
    max_val = max(plot_sample["Consumption"].max(), plot_sample["Production"].max())
    ax.plot(
        [min_val, max_val],
        [min_val, max_val],
        color="#e74c3c",
        linestyle="--",
        linewidth=1.6,
        label="1:1 Parity Line (Prod = Cons)",
    )

    corr = float(plot_data["Consumption"].corr(plot_data["Production"]))
    ax.text(
        0.05,
        0.90,
        f"Pearson r = {corr:.3f}",
        transform=ax.transAxes,
        fontsize=9.5,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#bdc3c7", alpha=0.85),
    )

    ax.set_title("EDA: Electricity Consumption vs Production (Hourly MWh)", pad=12, fontweight="bold")
    ax.set_xlabel("Hourly Electricity Consumption (MWh)")
    ax.set_ylabel("Hourly Electricity Production (MWh)")
    ax.legend(loc="lower right", framealpha=0.9)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    fig.tight_layout()
    return fig
