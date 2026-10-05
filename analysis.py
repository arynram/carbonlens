"""
analysis.py
-----------
Core analysis and calculation engine for Carbon-Aware Electricity
Production Analysis.

Implements:
- Centralized representative source-level lifecycle GHG emission factors (gCO2e/kWh)
- Hourly estimation: CO2e_kg = Production_MWh * Factor_g_per_kWh
  (1 MWh = 1,000 kWh, 1,000 g = 1 kg => Production_MWh * gCO2e/kWh = kgCO2e)
- Single-year and multi-year CO2e & production aggregations
- Year-over-year comparison with CO2e intensity metrics (kgCO2e/MWh)
- Deterministic historical-baseline low-carbon scenario modeling
- Descriptive statistics and EDA metrics
"""

import pandas as pd
import numpy as np

# ==============================================================================
# 1. CENTRALIZED EMISSION FACTORS (gCO2e / kWh == kgCO2e / MWh)
# Reference: Published lifecycle electricity-generation assessment literature
# (IPCC / NREL lifecycle estimates).
# Combined "Oil and Gas" uses 650 gCO2e/kWh as a simplified project assumption
# because the dataset combines oil and natural gas into one column.
# ==============================================================================
EMISSION_FACTORS = {
    "Coal": 820.0,           # Pulverized coal lifecycle median (IPCC)
    "Oil and Gas": 650.0,     # Combined Oil & Gas category project assumption
    "Biomass": 230.0,         # Direct & supply chain lifecycle emissions (IPCC)
    "Solar": 48.0,            # Utility-scale solar PV lifecycle median (IPCC/NREL)
    "Hydroelectric": 24.0,    # Hydropower reservoir / run-of-river median (IPCC)
    "Nuclear": 12.0,          # Nuclear lifecycle median (IPCC)
    "Wind": 11.0,             # Onshore wind lifecycle median (IPCC)
}

ENERGY_SOURCES = [
    "Nuclear",
    "Wind",
    "Hydroelectric",
    "Oil and Gas",
    "Coal",
    "Solar",
    "Biomass",
]

RENEWABLE_SOURCES = ["Wind", "Hydroelectric", "Solar", "Biomass"]
NON_RENEWABLE_SOURCES = ["Coal", "Oil and Gas", "Nuclear"]


def get_emission_factors_table() -> pd.DataFrame:
    """Returns a transparent reference table of lifecycle emission factors and methodology notes."""
    notes = {
        "Coal": "IPCC lifecycle assessment median (pulverized coal)",
        "Oil and Gas": "Project assumption for combined category (Gas CCGT ~490 + Oil peaker ~750-800)",
        "Biomass": "IPCC lifecycle median (direct & supply chain emissions)",
        "Solar": "IPCC/NREL lifecycle median (utility-scale solar PV)",
        "Hydroelectric": "IPCC lifecycle median (reservoir & run-of-river)",
        "Nuclear": "IPCC lifecycle median (light water reactors)",
        "Wind": "IPCC lifecycle median (utility onshore wind)",
    }
    data = []
    for src in ENERGY_SOURCES:
        cat = "Renewable" if src in RENEWABLE_SOURCES else "Non-Renewable"
        ef = EMISSION_FACTORS[src]
        data.append({
            "Energy Source": src,
            "Category": cat,
            "Factor (gCO2e/kWh)": ef,
            "Equivalent (kgCO2e/MWh)": ef,
            "Methodology Basis": notes.get(src, "IPCC lifecycle estimate"),
        })
    return pd.DataFrame(data)


def compute_hourly_emissions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes source-wise estimated CO2e emissions and total emissions for every hourly record.
    
    Formula:
        CO2e_kg = Production_MWh * Emission_Factor_g_per_kWh
    Mathematical proof:
        1 MWh = 1,000 kWh
        1,000 g = 1 kg
        Therefore: Production_MWh * gCO2e/kWh = kgCO2e.
        No additional multiplication by 1000 is performed.
    """
    df_calc = df.copy()
    co2e_columns = []
    for src in ENERGY_SOURCES:
        if src in df_calc.columns:
            col_name = f"{src}_CO2e"
            df_calc[col_name] = df_calc[src] * EMISSION_FACTORS[src]
            co2e_columns.append(col_name)

    df_calc["Total_CO2e"] = df_calc[co2e_columns].sum(axis=1)
    # Backward compatibility alias
    df_calc["Total_CO2"] = df_calc["Total_CO2e"]
    
    # Total production across all cleaned energy sources
    df_calc["Total_Production"] = df_calc[ENERGY_SOURCES].sum(axis=1)
    
    # Renewable and Non-renewable generation totals
    df_calc["Renewable_Production"] = df_calc[RENEWABLE_SOURCES].sum(axis=1)
    df_calc["NonRenewable_Production"] = df_calc[NON_RENEWABLE_SOURCES].sum(axis=1)

    return df_calc


def calculate_single_year_metrics(df: pd.DataFrame, year: int) -> dict:
    """
    Calculates detailed metrics for a single selected year using source-level lifecycle emission factors.
    
    Returns:
        Dictionary containing summary scalars, source-wise tables, and monthly aggregations.
    """
    df_calc = compute_hourly_emissions(df)
    year_df = df_calc[df_calc["Year"] == year].copy()

    if year_df.empty:
        raise ValueError(f"No records found for year {year}.")

    total_prod = float(year_df["Total_Production"].sum())
    total_co2e = float(year_df["Total_CO2e"].sum())
    total_renew = float(year_df["Renewable_Production"].sum())
    total_non_renew = float(year_df["NonRenewable_Production"].sum())

    # CO2e Intensity: kgCO2e per MWh generated
    co2e_intensity = (total_co2e / total_prod) if total_prod > 0 else 0.0

    # Production mix percentages
    renew_pct = (total_renew / total_prod * 100.0) if total_prod > 0 else 0.0
    non_renew_pct = (total_non_renew / total_prod * 100.0) if total_prod > 0 else 0.0

    # Average hourly CO2e emissions (kgCO2e / hour)
    avg_hourly_co2e = float(year_df["Total_CO2e"].mean())

    # Source-wise breakdown table:
    # | Energy Source | Production MWh | Factor gCO2e/kWh | Estimated CO2e kg |
    source_rows = []
    for src in ENERGY_SOURCES:
        prod_val = float(year_df[src].sum())
        co2e_val = float(year_df[f"{src}_CO2e"].sum())
        prod_pct = (prod_val / total_prod * 100.0) if total_prod > 0 else 0.0
        co2e_pct = (co2e_val / total_co2e * 100.0) if total_co2e > 0 else 0.0
        cat = "Renewable" if src in RENEWABLE_SOURCES else "Non-Renewable"

        source_rows.append({
            "Energy Source": src,
            "Category": cat,
            "Production (MWh)": prod_val,
            "Factor (gCO2e/kWh)": EMISSION_FACTORS[src],
            "Estimated CO2e (kg)": co2e_val,
            "Estimated CO2e (Tonnes)": co2e_val / 1000.0,
            "Production Share (%)": prod_pct,
            "CO2e Contribution (%)": co2e_pct,
        })
    source_df = pd.DataFrame(source_rows)

    # Monthly aggregation
    monthly_agg = year_df.groupby("Month").agg(
        Production=("Total_Production", "sum"),
        Estimated_CO2e_kg=("Total_CO2e", "sum"),
        Hours=("DateTime", "count"),
    ).reset_index()

    monthly_agg["Estimated_CO2e_Tonnes"] = monthly_agg["Estimated_CO2e_kg"] / 1000.0
    monthly_agg["CO2e_Intensity"] = monthly_agg["Estimated_CO2e_kg"] / monthly_agg["Production"]
    month_names = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }
    monthly_agg["Month_Name"] = monthly_agg["Month"].map(month_names)

    return {
        "year": year,
        "total_production_mwh": total_prod,
        "total_co2e_kg": total_co2e,
        "total_co2e_tonnes": total_co2e / 1000.0,
        "total_co2_kg": total_co2e,               # compatibility alias
        "total_co2_tonnes": total_co2e / 1000.0,  # compatibility alias
        "avg_hourly_co2e_kg": avg_hourly_co2e,
        "co2e_intensity_kg_mwh": co2e_intensity,
        "co2_intensity_kg_mwh": co2e_intensity,    # compatibility alias
        "renewable_prod_mwh": total_renew,
        "renewable_pct": renew_pct,
        "non_renewable_prod_mwh": total_non_renew,
        "non_renewable_pct": non_renew_pct,
        "source_summary": source_df,
        "monthly_summary": monthly_agg,
    }


def calculate_multi_year_metrics(df: pd.DataFrame, years: list[int]) -> pd.DataFrame:
    """
    Computes annual aggregates for all specified years for comparison.
    """
    df_calc = compute_hourly_emissions(df)
    filtered = df_calc[df_calc["Year"].isin(years)]

    rows = []
    for yr in sorted(years):
        sub = filtered[filtered["Year"] == yr]
        if sub.empty:
            continue
        prod = float(sub["Total_Production"].sum())
        co2e = float(sub["Total_CO2e"].sum())
        renew = float(sub["Renewable_Production"].sum())
        non_renew = float(sub["NonRenewable_Production"].sum())
        intensity = (co2e / prod) if prod > 0 else 0.0
        renew_pct = (renew / prod * 100.0) if prod > 0 else 0.0
        non_renew_pct = (non_renew / prod * 100.0) if prod > 0 else 0.0

        is_partial = len(sub["Month"].unique()) < 12
        status = f"Partial ({len(sub['Month'].unique())} mos)" if is_partial else "Complete"

        rows.append({
            "Year": yr,
            "Total Production (MWh)": prod,
            "Total CO2e (kg)": co2e,
            "Total CO2e (Tonnes)": co2e / 1000.0,
            "Total CO2 (Tonnes)": co2e / 1000.0,  # compatibility alias
            "CO2e Intensity (kgCO2e/MWh)": intensity,
            "CO2 Intensity (kg CO2/MWh)": intensity,  # compatibility alias
            "Renewable Production (MWh)": renew,
            "Non-Renewable Production (MWh)": non_renew,
            "Renewable (%)": renew_pct,
            "Non-Renewable (%)": non_renew_pct,
            "Data Status": status,
        })

    return pd.DataFrame(rows)


def compare_years_metrics(multi_year_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates differences and percentage changes between consecutive selected years.
    """
    if len(multi_year_df) < 2:
        return pd.DataFrame()

    df_comp = multi_year_df.copy().sort_values("Year").reset_index(drop=True)
    comp_rows = []

    for i in range(1, len(df_comp)):
        prev = df_comp.iloc[i - 1]
        curr = df_comp.iloc[i]

        prod_diff = curr["Total Production (MWh)"] - prev["Total Production (MWh)"]
        prod_pct_change = (prod_diff / prev["Total Production (MWh)"]) * 100.0 if prev["Total Production (MWh)"] > 0 else 0.0

        co2e_diff = curr["Total CO2e (kg)"] - prev["Total CO2e (kg)"]
        co2e_pct_change = (co2e_diff / prev["Total CO2e (kg)"]) * 100.0 if prev["Total CO2e (kg)"] > 0 else 0.0

        intensity_diff = curr["CO2e Intensity (kgCO2e/MWh)"] - prev["CO2e Intensity (kgCO2e/MWh)"]
        intensity_pct_change = (intensity_diff / prev["CO2e Intensity (kgCO2e/MWh)"]) * 100.0 if prev["CO2e Intensity (kgCO2e/MWh)"] > 0 else 0.0

        renew_pct_diff = curr["Renewable (%)"] - prev["Renewable (%)"]

        comp_rows.append({
            "Comparison": f"{int(curr['Year'])} vs {int(prev['Year'])}",
            "Production Change (MWh)": prod_diff,
            "Production Change (%)": prod_pct_change,
            "CO2e Change (kg)": co2e_diff,
            "CO2e Change (Tonnes)": co2e_diff / 1000.0,
            "CO2e Change (%)": co2e_pct_change,
            "Intensity Change (kg/MWh)": intensity_diff,
            "Intensity Change (%)": intensity_pct_change,
            "Renewable Share Shift (%)": renew_pct_diff,
        })

    return pd.DataFrame(comp_rows)


def calculate_historical_scenario(
    df: pd.DataFrame,
    month: int,
    future_year: int,
    fossil_reduction_pct: float = 25.0
) -> dict:
    """
    Calculates an illustrative low-carbon electricity mix for a future year/month
    based strictly on historical data for that month.

    Methodology:
    1. Filter historical records for the selected month (using only years where data exists).
    2. Compute the historical average monthly electricity production for each energy source.
    3. Calculate historical baseline energy mix shares (%) and historical average CO2e.
    4. Deterministic scenario shift:
       - Reduce high-emission fossil sources (Coal, Oil and Gas) by fossil_reduction_pct.
       - Calculate the exact share freed up.
       - Proportionally redistribute the freed share among renewable sources (Wind, Solar, Hydro, Biomass).
       - Maintain Nuclear baseline to reflect real-world baseload constraints.
       - Total share remains exactly 100.0%.
    5. Calculate scenario estimated CO2e using the SAME representative emission factors.
    6. Calculate CO2e reduction and reduction percentage.
    """
    month_data = df[df["Month"] == month].copy()
    available_years = sorted(month_data["Year"].unique().tolist())

    if not available_years:
        raise ValueError(f"No historical data available for month {month}.")

    # Calculate average generation per source for this month across available historical years
    annual_month_sums = month_data.groupby("Year")[ENERGY_SOURCES].sum()
    hist_avg_sources = annual_month_sums.mean()
    total_avg_gen = float(hist_avg_sources.sum())

    if total_avg_gen <= 0:
        raise ValueError("Historical generation total is zero.")

    # Historical shares (%)
    hist_shares = (hist_avg_sources / total_avg_gen) * 100.0

    # Historical average CO2e (kg)
    # CO2e_kg = Production_MWh * Factor_g_per_kWh
    hist_co2e = sum(hist_avg_sources[s] * EMISSION_FACTORS[s] for s in ENERGY_SOURCES)
    hist_intensity = hist_co2e / total_avg_gen

    # Deterministic Low-Carbon Scenario Construction
    # 1. Reduce fossil sources (Coal, Oil and Gas) by fossil_reduction_pct
    scenario_shares = hist_shares.copy()
    freed_pct = 0.0

    fossil_sources = ["Coal", "Oil and Gas"]
    reduction_factor = fossil_reduction_pct / 100.0

    for src in fossil_sources:
        curr_share = hist_shares[src]
        reduction_amount = curr_share * reduction_factor
        scenario_shares[src] = curr_share - reduction_amount
        freed_pct += reduction_amount

    # 2. Redistribute freed share to renewable sources proportionally
    renew_current_sum = sum(hist_shares[src] for src in RENEWABLE_SOURCES)
    for src in RENEWABLE_SOURCES:
        if renew_current_sum > 0:
            weight = hist_shares[src] / renew_current_sum
            scenario_shares[src] = hist_shares[src] + (freed_pct * weight)
        else:
            scenario_shares[src] = hist_shares[src] + (freed_pct / len(RENEWABLE_SOURCES))

    # Nuclear remains unchanged
    scenario_shares["Nuclear"] = hist_shares["Nuclear"]

    # Re-normalize slightly if float precision causes 99.99999%
    total_scenario_pct = scenario_shares.sum()
    scenario_shares = (scenario_shares / total_scenario_pct) * 100.0

    # Compute scenario generation in MWh
    scenario_gen = (scenario_shares / 100.0) * total_avg_gen

    # Scenario CO2e using SAME emission factors
    scenario_co2e = sum(scenario_gen[s] * EMISSION_FACTORS[s] for s in ENERGY_SOURCES)
    scenario_intensity = scenario_co2e / total_avg_gen

    # CO2e Reduction
    co2e_reduction_kg = hist_co2e - scenario_co2e
    co2e_reduction_pct = (co2e_reduction_kg / hist_co2e) * 100.0 if hist_co2e > 0 else 0.0

    # Comparison DataFrame
    mix_comparison = []
    for src in ENERGY_SOURCES:
        cat = "Renewable" if src in RENEWABLE_SOURCES else "Non-Renewable"
        h_pct = float(hist_shares[src])
        s_pct = float(scenario_shares[src])
        diff_pct = s_pct - h_pct
        mix_comparison.append({
            "Energy Source": src,
            "Category": cat,
            "Factor (gCO2e/kWh)": EMISSION_FACTORS[src],
            "Historical Average Share (%)": h_pct,
            "Estimated Scenario Share (%)": s_pct,
            "Shift (%)": diff_pct,
            "Historical Average Prod (MWh)": float(hist_avg_sources[src]),
            "Scenario Prod (MWh)": float(scenario_gen[src]),
        })
    mix_df = pd.DataFrame(mix_comparison)

    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    return {
        "month": month,
        "month_name": month_names.get(month, f"Month {month}"),
        "future_year": future_year,
        "fossil_reduction_applied_pct": fossil_reduction_pct,
        "historical_years_used": available_years,
        "historical_avg_gen_mwh": total_avg_gen,
        "historical_avg_co2_kg": hist_co2e,
        "historical_avg_co2_tonnes": hist_co2e / 1000.0,
        "historical_intensity_kg_mwh": hist_intensity,
        "scenario_co2_kg": scenario_co2e,
        "scenario_co2_tonnes": scenario_co2e / 1000.0,
        "scenario_intensity_kg_mwh": scenario_intensity,
        "co2_reduction_kg": co2e_reduction_kg,
        "co2_reduction_tonnes": co2e_reduction_kg / 1000.0,
        "co2_reduction_pct": co2e_reduction_pct,
        "mix_comparison": mix_df,
    }


def get_eda_statistics(df: pd.DataFrame) -> dict:
    """
    Computes statistical and exploratory insights for syllabus requirements:
    - Descriptive statistics
    - Consumption vs Production correlation
    - Source variability summary
    """
    cols_to_analyze = ["Consumption", "Production"] + ENERGY_SOURCES
    valid_cols = [c for c in cols_to_analyze if c in df.columns]

    desc_stats = df[valid_cols].describe().T
    desc_stats["IQR"] = desc_stats["75%"] - desc_stats["25%"]

    corr = float(df["Consumption"].corr(df["Production"]))

    return {
        "descriptive_stats": desc_stats,
        "consumption_production_corr": corr,
    }
