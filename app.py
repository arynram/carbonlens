# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np

from data_processing import (
    load_and_preprocess_data,
    check_incomplete_year,
    ENERGY_SOURCES,
    RENEWABLE_SOURCES,
    NON_RENEWABLE_SOURCES,
)
from analysis import (
    get_emission_factors_table,
    calculate_single_year_metrics,
    calculate_multi_year_metrics,
    calculate_historical_scenario,
    EMISSION_FACTORS,
)
import visualizations as viz
from ui_theme import (
    apply_theme,
    sec,
    notice,
    kpi_card,
    chart_card_start,
    chart_card_end,
    render_fig,
)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG & THEME
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CarbonLens - Minecraft Edition",
    layout="wide",
    page_icon="⛏️",
    initial_sidebar_state="collapsed",
)

apply_theme()

# ─────────────────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_and_preprocess_data()

try:
    df, metadata = get_data()
    available_years = metadata["available_years"]
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# PAGES & SEAMLESS TOP NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
PAGES = ["⌂  Overview", "◈  Yearly Report", "◉  Clean Energy Plan"]

if "active_page" not in st.session_state:
    st.session_state["active_page"] = PAGES[0]

pill_c1, pill_c2, pill_c3 = st.columns(3)
for col, p in zip([pill_c1, pill_c2, pill_c3], PAGES):
    is_cur = (st.session_state["active_page"] == p)
    if col.button(p, key=f"top_nav_{p}", use_container_width=True, type="primary" if is_cur else "secondary"):
        st.session_state["active_page"] = p
        st.rerun()

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

menu = st.session_state["active_page"]

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
if "Overview" in menu:
    # Header
    st.markdown("""
    <div style="padding:0.3rem 0 1rem;border-bottom:1px solid rgba(0,0,0,0.12);margin-bottom:1.2rem;">
        <h1 style="font-family:'Press Start 2P',monospace !important;font-size:1.6rem !important;margin-bottom:0.6rem !important;color:#000000 !important;text-shadow:2px 2px 0px #ffffff !important;line-height:1.5 !important;">Electricity Pollution Tracker</h1>
        <p style="font-family:'VT323',monospace !important;font-size:26px !important;color:#222222 !important;margin:0 !important;line-height:1.35 !important;">Carbon emission intensity benchmarks and clean energy opportunities.</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick metric counters
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(kpi_card("Validated Records", f"{metadata['total_clean_rows']:,}", "", "Total cleaned hourly data points", "blue"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Years of Data", f"{len(available_years)}", "YRS", f"Spanning {available_years[0]} to {available_years[-1]}", "amber"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Energy Sources", f"{len(ENERGY_SOURCES)}", "TYPES", "Renewables & fossil fuel categories", "lime"), unsafe_allow_html=True)

    # Pollution Scorecard Table
    sec("Pollution Scorecard — scroll down to view full table")
    st.markdown("""
    <p style="font-size:0.88rem;color:#6b7280;margin-bottom:1.2rem;line-height:1.65;max-width:580px;">
        How many grams of CO₂ does each energy source release per kilowatt-hour of electricity?
        <strong style="color:#2d3139">Lower = cleaner.</strong>
    </p>
    """, unsafe_allow_html=True)

    ef = get_emission_factors_table()
    max_f = ef["Factor (gCO2e/kWh)"].max()
    rows_html = ""
    for _, row in ef.iterrows():
        src, cat, fac = row["Energy Source"], row["Category"], row["Factor (gCO2e/kWh)"]
        bar_w = int((fac / max_f) * 110)
        bar_c = "#c8f135" if cat == "Renewable" else ("#ff5b5b" if fac > 400 else "#ffb800")
        pill_cls = "pill-green" if cat == "Renewable" else "pill-red"
        rows_html += f"""<tr>
          <td class="src">{src}</td>
          <td><span class="pill pill-sm {pill_cls}">{cat}</span></td>
          <td class="val">{fac}</td>
          <td><span class="bar-bg"><span class="bar-fill" style="width:{bar_w}px;background:{bar_c};"></span></span></td>
        </tr>"""

    st.markdown(f"""
    <div class="chart-card table-responsive-wrapper" style="animation:slideInUp .55s ease .5s both;">
      <div style="overflow-x:auto; -webkit-overflow-scrolling:touch; width:100%;">
        <table class="etable">
          <thead><tr>
            <th>Energy Source</th><th>Type</th><th>gCO₂/kWh</th><th>Relative Pollution</th>
          </tr></thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
    </div>
    """, unsafe_allow_html=True)
    notice("💡", "<strong>Key takeaway:</strong> Coal (820 g/kWh) produces <strong>75× more CO₂</strong> than Wind (11 g/kWh) for the same amount of electricity. Switching to renewables has a massive impact.", "lime")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: YEARLY REPORT
# ─────────────────────────────────────────────────────────────────────────────
elif "Yearly" in menu:
    st.markdown("""
    <div style="padding:0.3rem 0 1.2rem;border-bottom:1px solid rgba(0,0,0,0.12);margin-bottom:1.5rem;">
        <span class="page-eyebrow" style="font-size:0.75rem !important;">Data Analysis</span>
        <h1 style="font-family:'Press Start 2P',monospace !important;font-size:1.5rem !important;margin:0.3rem 0 0.5rem 0 !important;color:#000000 !important;text-shadow:2px 2px 0px #ffffff !important;line-height:1.5 !important;">Yearly Pollution Report</h1>
        <p style="font-family:'VT323',monospace !important;font-size:25px !important;color:#222222 !important;margin:0 !important;line-height:1.35 !important;">Select a year to see a full breakdown of electricity production and the CO₂ pollution it caused.</p>
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio("", ["Single Year — Full Breakdown", "Multiple Years — Trend Overview"],
                    horizontal=True, label_visibility="collapsed")

    if "Single Year" in mode:
        year = st.selectbox("SELECT YEAR", available_years)
        is_inc, msg = check_incomplete_year(year, metadata)
        if is_inc:
            notice("⚠️", f"<strong>Partial year data:</strong> {msg}", "amber")

        with st.spinner("Calculating…"):
            m = calculate_single_year_metrics(df, year)

        sec("Key Metrics")
        c1, c2, c3, c4 = st.columns(4, gap="medium")
        with c1: st.markdown(kpi_card("⚡ Electricity Generated",
            f"{m['total_production_mwh']:,.0f}", "MWh",
            "Total energy produced from all sources this year.", "blue"), unsafe_allow_html=True)
        with c2: st.markdown(kpi_card("☁️ CO₂ Released",
            f"{m['total_co2e_tonnes']:,.0f}", "Tonnes",
            "Estimated total carbon dioxide from electricity generation.", "red"), unsafe_allow_html=True)
        with c3: st.markdown(kpi_card("🍃 Cleanliness Score",
            f"{m['co2e_intensity_kg_mwh']:,.1f}", "kg/MWh",
            "CO₂ per unit of electricity. Lower = cleaner energy mix.", "lime"), unsafe_allow_html=True)
        with c4: st.markdown(kpi_card("🌱 Renewable Share",
            f"{m['renewable_pct']:,.1f}", "%",
            "Portion of electricity from Wind, Solar, Hydro & Biomass.", "amber"), unsafe_allow_html=True)

        sec("Energy Source Breakdown")
        c1, c2 = st.columns(2, gap="large")
        with c1:
            chart_card_start("Electricity Produced by Source (GWh)")
            render_fig(viz.plot_source_production_bar(m["source_summary"], year))
            chart_card_end()

            chart_card_start("Renewable vs Non-Renewable Share")
            render_fig(viz.plot_renewable_mix_pie(m["renewable_pct"], m["non_renewable_pct"], year))
            chart_card_end()

        with c2:
            chart_card_start("CO₂ Emissions by Source (Kilotonnes)")
            render_fig(viz.plot_source_co2_bar(m["source_summary"], year))
            chart_card_end()

            chart_card_start("Monthly CO₂ Emission Trend")
            render_fig(viz.plot_monthly_co2_line(m["monthly_summary"], year))
            chart_card_end()

    else:
        years = st.multiselect("SELECT YEARS TO COMPARE", available_years,
                               default=available_years[-3:] if len(available_years) > 3 else available_years)
        if not years:
            notice("ℹ️", "Select at least one year above to see results.", "blue")
        else:
            with st.spinner("Calculating…"):
                mdf = calculate_multi_year_metrics(df, years)

            sec("Year-by-Year Summary")
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.dataframe(mdf, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

            sec("Visual Trends")
            c1, c2 = st.columns(2, gap="large")
            with c1:
                chart_card_start("Total CO₂ Emissions per Year")
                render_fig(viz.plot_year_co2_bar(mdf))
                chart_card_end()
            with c2:
                chart_card_start("Carbon Intensity Trend (Lower = Cleaner)")
                render_fig(viz.plot_co2_intensity_line(mdf))
                chart_card_end()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: CLEAN ENERGY PLAN
# ─────────────────────────────────────────────────────────────────────────────
elif "Clean Energy" in menu:
    st.markdown("""
    <div style="padding:0.3rem 0 1.2rem;border-bottom:1px solid rgba(0,0,0,0.12);margin-bottom:1.5rem;">
        <span class="page-eyebrow" style="font-size:0.75rem !important;">Scenario Simulation</span>
        <h1 style="font-family:'Press Start 2P',monospace !important;font-size:1.5rem !important;margin:0.3rem 0 0.5rem 0 !important;color:#000000 !important;text-shadow:2px 2px 0px #ffffff !important;line-height:1.5 !important;">Future Clean Energy Plan</h1>
        <p style="font-family:'VT323',monospace !important;font-size:25px !important;color:#222222 !important;margin:0 !important;line-height:1.35 !important;">
            Simulate what happens when polluting fossil fuels (Coal & Oil) are phased out 
            and replaced with clean renewables (Solar, Wind, Hydro).
        </p>
    </div>
    """, unsafe_allow_html=True)

    sec("Scenario Controls")
    c_yr, c_sl = st.columns([1, 2.5], gap="large")
    with c_yr:
        future_year = st.selectbox("TARGET FUTURE YEAR", [2025, 2030, 2035, 2040, 2050], index=1)
    with c_sl:
        reduction = st.slider(
            "PHASE OUT COAL & OIL — REDUCTION TARGET (%)",
            min_value=5,
            max_value=100,
            value=50,
            step=5,
            format="%d%%",
            help="Drag to simulate how much fossil fuel energy is replaced by renewables"
        )

    # Use June (mid-year baseline) under the hood without confusing month picker
    month = 6

    try:
        with st.spinner("Simulating scenario…"):
            s = calculate_historical_scenario(df, month, future_year, float(reduction))

        red_pct_str = f"{s['co2_reduction_pct']:.1f}"
        hist_co2_str = f"{s['historical_avg_co2_tonnes']:,.0f}"
        scen_co2_str = f"{s['scenario_co2_tonnes']:,.0f}"
        saved_co2_str = f"{s['co2_reduction_tonnes']:,.0f}"

        # Minecraft Nether Scenario Hero Card
        st.markdown(f"""
        <div class="scenario-hero">
            <div style="font-family:'Press Start 2P',monospace;font-size:0.65rem;letter-spacing:0.06em;text-transform:uppercase;color:#55ff55;margin-bottom:6px;">
                PROJECTED EMISSION REDUCTION
            </div>
            <div class="scenario-pct">-{red_pct_str}%</div>
            <div style="font-family:'VT323',monospace;font-size:23px;color:#ffffff;margin-top:8px;line-height:1.35;">
                By phasing out <span style="color:#55ff55;font-weight:700;">{reduction}%</span> of Coal & Oil by <span style="color:#ffffff;font-weight:700;">{future_year}</span>, 
                monthly CO2 drops from <span style="color:#ffffff;font-weight:700;">{hist_co2_str} tonnes</span> 
                down to <span style="color:#55ff55;font-weight:700;">{scen_co2_str} tonnes</span> 
                - avoiding <span style="color:#55ff55;font-weight:700;">{saved_co2_str} metric tonnes</span> of CO2 emissions.
            </div>
        </div>
        """, unsafe_allow_html=True)

        sec("Clear Metric Breakdown")
        m1, m2, m3, m4 = st.columns(4, gap="medium")
        with m1:
            st.markdown(kpi_card("Baseline Emissions", hist_co2_str, "T", "Current emissions before clean energy shift", "red"), unsafe_allow_html=True)
        with m2:
            st.markdown(kpi_card("New Pollution Level", scen_co2_str, "T", "Projected emissions after transition", "lime"), unsafe_allow_html=True)
        with m3:
            st.markdown(kpi_card("CO₂ Prevented", f"-{saved_co2_str}", "T", "Net carbon dioxide kept out of atmosphere", "lime"), unsafe_allow_html=True)
        with m4:
            st.markdown(kpi_card("Clean Transition", f"{reduction}", "%", "Fossil fuel share replaced by Wind & Solar", "blue"), unsafe_allow_html=True)

        sec("Visual Comparisons")
        c1, c2 = st.columns(2, gap="large")
        with c1:
            chart_card_start("Energy Mix Shift: Baseline vs Proposed (%)")
            render_fig(viz.plot_scenario_mix_stacked_bar(s["mix_comparison"], s["month_name"], future_year))
            chart_card_end()
        with c2:
            chart_card_start(f"CO₂ Emissions Avoided by {future_year} (Tonnes)")
            render_fig(viz.plot_scenario_co2_bar(s["historical_avg_co2_kg"], s["scenario_co2_kg"], s["month_name"], future_year))
            chart_card_end()

        sec("Energy Source Shift Table")
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        summary_table = s["mix_comparison"][["Energy Source", "Category", "Historical Average Share (%)", "Estimated Scenario Share (%)", "Shift (%)"]].copy()
        summary_table["Historical Average Share (%)"] = summary_table["Historical Average Share (%)"].map("{:.1f}%".format)
        summary_table["Estimated Scenario Share (%)"] = summary_table["Estimated Scenario Share (%)"].map("{:.1f}%".format)
        summary_table["Shift (%)"] = summary_table["Shift (%)"].map(lambda x: f"+{x:.1f}%" if x > 0 else f"{x:.1f}%")
        st.dataframe(summary_table, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        notice("❌", f"<strong>Error:</strong> {e}", "red")
