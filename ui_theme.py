# -*- coding: utf-8 -*-
"""
ui_theme.py
-----------
Minecraft Boxy Retro Design System, CSS styling, and HTML components
for the CarbonLens web platform.
"""

import streamlit as st
import io
import matplotlib.pyplot as plt

MINECRAFT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap');

/* Completely hide left sidebar and collapsed control */
[data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="collapsedControl"] {
  display: none !important;
  width: 0 !important;
  visibility: hidden !important;
}

/* ══════════════════════════════════════════════
   GLOBAL 0PX BORDER-RADIUS (MINECRAFT PIXEL STYLE)
══════════════════════════════════════════════ */
*, html, body, div, button, span, input, select, table, tr, td, th, iframe {
  border-radius: 0px !important;
  image-rendering: pixelated !important;
}

/* Background wallpaper — Minecraft dark bedrock/dirt aesthetic */
.stApp {
  background-color: #2b2725 !important;
  background-image: radial-gradient(#1b1816 2px, transparent 2px) !important;
  background-size: 16px 16px !important;
  color: #111111;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; height: 0; }
.stDeployButton { display: none !important; }

/* Minecraft GUI Window Container */
.block-container {
  background: #c6c6c6 !important;
  border: 5px solid #000000 !important;
  box-shadow: inset -4px -4px 0px 0px #555555, inset 4px 4px 0px 0px #ffffff, 8px 8px 0px 0px rgba(0,0,0,0.6) !important;
  padding: 1.5rem 2rem 2.5rem !important;
  max-width: 1200px !important;
  margin: 1rem auto !important;
}

/* ══════════════════════════════════════════════
   PIXEL TYPOGRAPHY & READABILITY
══════════════════════════════════════════════ */
html, body, .stApp, .stApp *, div[data-testid*="st"], [class*="css"], p, span, div, label, input {
  font-family: 'VT323', monospace !important;
  font-size: 21px !important;
  letter-spacing: 0.02em;
  line-height: 1.35;
  -webkit-font-smoothing: none;
}

/* Page Headings */
h1, h2, h3, .page-title {
  font-family: 'Press Start 2P', monospace !important;
  font-size: clamp(1rem, 1.8vw, 1.35rem) !important;
  line-height: 1.5 !important;
  letter-spacing: -0.01em !important;
  color: #111111 !important;
  text-shadow: 2px 2px 0px #ffffff !important;
  margin: 0 0 0.4rem 0 !important;
}

.page-desc {
  font-family: 'VT323', monospace !important;
  font-size: 22px !important;
  color: #333333 !important;
  margin: 0 !important;
  line-height: 1.3 !important;
}

.page-eyebrow, .sec-label, .card-label, .chart-card-title,
div[data-testid="stSelectbox"] label, div[data-testid="stSlider"] label {
  font-family: 'Press Start 2P', monospace !important;
  font-size: 0.65rem !important;
  line-height: 1.4 !important;
  letter-spacing: 0.03em !important;
  color: #1c1c1c !important;
  text-transform: uppercase !important;
  text-shadow: 1px 1px 0px #ffffff;
}

/* Simulation Big Percentage */
.scenario-pct {
  font-family: 'VT323', monospace !important;
  font-size: 4.8rem !important;
  color: #55ff55 !important;
  text-shadow: 3px 3px 0px #000000;
  line-height: 0.95 !important;
  margin: 0.3rem 0;
  font-weight: 700;
}

/* KPI Card & Metric Values - strictly responsive & contained */
.card-value {
  font-family: 'VT323', monospace !important;
  font-size: clamp(1.7rem, 2.3vw, 2.3rem) !important;
  line-height: 1.0 !important;
  letter-spacing: 0.01em !important;
  font-weight: 700 !important;
  color: #111111 !important;
  margin: 0.2rem 0 0.25rem 0 !important;
  display: flex !important;
  align-items: baseline !important;
  flex-wrap: wrap !important;
  gap: 3px !important;
  text-shadow: 1px 1px 0px rgba(255,255,255,0.8);
  word-break: break-word !important;
  overflow: hidden !important;
}

.card-value span {
  font-family: 'Press Start 2P', monospace !important;
  font-size: 0.52rem !important;
  color: #555555 !important;
  font-weight: normal !important;
  margin-left: 2px;
  vertical-align: baseline;
}

.card-label {
  margin-bottom: 0.25rem !important;
  font-size: 0.62rem !important;
  word-break: break-word !important;
}

.card-sub {
  font-family: 'VT323', monospace !important;
  font-size: 18px !important;
  color: #444444 !important;
  line-height: 1.2 !important;
  margin-top: 0.15rem !important;
}

/* ══════════════════════════════════════════════
   MINECRAFT BUTTON BEVELS
══════════════════════════════════════════════ */
button, .stButton > button {
  font-family: 'Press Start 2P', monospace !important;
  font-size: 0.65rem !important;
  padding: 10px 14px !important;
  border-radius: 0px !important;
  border: 3px solid #000000 !important;
  background: #757375 !important;
  box-shadow: inset -3px -3px 0px 0px #373737, inset 3px 3px 0px 0px #b8b8b8, 2px 2px 0px 0px #000000 !important;
  color: #ffffff !important;
  text-shadow: 2px 2px 0px #000000 !important;
  transition: transform 0.05s ease, background 0.05s ease !important;
  cursor: pointer !important;
}

button:hover, .stButton > button:hover {
  background: #4e7828 !important;
  box-shadow: inset -3px -3px 0px 0px #223c10, inset 3px 3px 0px 0px #79b03e, 2px 2px 0px 0px #000000 !important;
  color: #ffffff !important;
}

button:active, .stButton > button:active {
  transform: translate(2px, 2px) !important;
  box-shadow: inset 3px 3px 0px 0px #182b0b, inset -3px -3px 0px 0px #5c912e !important;
}

/* Active / Primary Minecraft Button (Emerald XP Green) */
.stButton > button[kind="primary"] {
  background: #2a4c14 !important;
  box-shadow: inset 3px 3px 0px 0px #152709, inset -3px -3px 0px 0px #55ff55, 2px 2px 0px 0px #000000 !important;
  color: #55ff55 !important;
  border: 3px solid #000000 !important;
  text-shadow: 2px 2px 0px #000000 !important;
}

/* ══════════════════════════════════════════════
   MINECRAFT CARDS & CONTAINERS
══════════════════════════════════════════════ */
.card, .feat-card, .chart-card {
  background: #d4d4d4 !important;
  border: 3px solid #000000 !important;
  box-shadow: inset -3px -3px 0px 0px #888888, inset 3px 3px 0px 0px #ffffff, 4px 4px 0px 0px #1e1e1e !important;
  border-radius: 0px !important;
  padding: 14px 14px !important;
  margin-bottom: 0.85rem !important;
  overflow: hidden !important;
  word-wrap: break-word !important;
}

.card:hover, .feat-card:hover {
  transform: translateY(-1px) !important;
  box-shadow: inset -3px -3px 0px 0px #888888, inset 3px 3px 0px 0px #ffffff, 5px 5px 0px 0px #000000 !important;
}

.card-lime  { border-left: 5px solid #2e8b20 !important; }
.card-red   { border-left: 5px solid #d92626 !important; }
.card-blue  { border-left: 5px solid #1c75b8 !important; }
.card-amber { border-left: 5px solid #cc7a00 !important; }

/* Minecraft Obsidian Nether Hero Box */
.scenario-hero {
  background: #171224 !important;
  border: 4px solid #000000 !important;
  box-shadow: inset -3px -3px 0px 0px #352054, inset 3px 3px 0px 0px #794bb7, 5px 5px 0px 0px #000000 !important;
  border-radius: 0px !important;
  padding: 20px 24px !important;
  margin: 1rem 0 1.2rem !important;
}

/* Minecraft Selectbox */
div[data-baseweb="select"] > div {
  background: #ffffff !important;
  border: 3px solid #000000 !important;
  box-shadow: inset 2px 2px 0px 0px #aaaaaa, inset -2px -2px 0px 0px #ffffff !important;
  border-radius: 0px !important;
  min-height: 42px !important;
}
div[data-baseweb="select"] * {
  font-family: 'VT323', monospace !important;
  font-size: 23px !important;
  color: #000000 !important;
}
ul[data-baseweb="menu"], div[data-baseweb="popover"] {
  border-radius: 0px !important;
  border: 3px solid #000000 !important;
  background: #c6c6c6 !important;
  box-shadow: 5px 5px 0px #000000 !important;
}
li[data-baseweb="menu-item"] {
  font-family: 'VT323', monospace !important;
  font-size: 22px !important;
}
li[data-baseweb="menu-item"]:hover {
  background: #4e7828 !important;
  color: #ffffff !important;
}

/* Minecraft Slider (Pixel Block Thumb) */
div[data-testid="stSlider"] {
  padding-top: 0.2rem !important;
  padding-bottom: 0.5rem !important;
}
div[data-testid="stSlider"] [role="slider"] {
  background: #55ff55 !important;
  border: 3px solid #000000 !important;
  box-shadow: inset -2px -2px 0px 0px #2a4c14, inset 2px 2px 0px 0px #ffffff !important;
  border-radius: 0px !important;
  width: 22px !important;
  height: 22px !important;
}
div[data-testid="stSlider"] [data-testid="stThumbValue"] {
  font-family: 'Press Start 2P', monospace !important;
  font-size: 0.68rem !important;
  color: #000000 !important;
}

/* Notice box (Minecraft wooden/quest signboard) */
.notice {
  border-radius: 0px !important;
  border: 3px solid #000000 !important;
  box-shadow: 3px 3px 0px #000000 !important;
  font-family: 'VT323', monospace !important;
  font-size: 21px !important;
  padding: 10px 14px !important;
  margin: 0.8rem 0 !important;
  line-height: 1.35 !important;
}
.notice-blue  { background: #b8d4e3; color: #082b42; }
.notice-amber { background: #e3d2b8; color: #422908; }
.notice-green { background: #b8e3bd; color: #084212; }
.notice-lime  { background: #cfe3b8; color: #1e4208; }
.notice-red   { background: #e8b6b6; color: #4a0a0a; }

/* Minecraft Section divider */
.sec-label {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 1.3rem 0 0.8rem !important;
}
.sec-label::after {
  content: '';
  flex: 1;
  height: 3px;
  background: #000000;
  box-shadow: 0 1px 0 #ffffff;
}

/* Chart Container header */
.chart-card-title {
  margin-bottom: 0.6rem !important;
  color: #1a1a1a !important;
}

/* Emission table */
.etable {
  width: 100%;
  border-collapse: collapse;
  font-family: 'VT323', monospace !important;
  font-size: 21px !important;
}
.etable th {
  font-family: 'Press Start 2P', monospace !important;
  font-size: 0.6rem !important;
  background: #2b2b2b !important;
  color: #ffffff !important;
  padding: 8px 12px;
  border: 2px solid #000000;
  text-align: left;
}
.etable td {
  padding: 6px 12px;
  border: 2px solid #999999;
  color: #111111;
}
.etable tr:hover td {
  background: #d6e2c2;
}
.bar-bg {
  background: #000000;
  border: 2px solid #444444;
  height: 10px;
  width: 120px;
  display: inline-block;
  border-radius: 0px !important;
  vertical-align: middle;
}
.bar-fill {
  height: 10px;
  display: inline-block;
  border-radius: 0px !important;
}

.pill {
  font-family: 'Press Start 2P', monospace !important;
  font-size: 0.55rem !important;
  padding: 3px 6px;
  border: 2px solid #000000;
  border-radius: 0px !important;
  display: inline-block;
}
.pill-green { background: #45b535; color: #ffffff; text-shadow: 1px 1px 0 #000; }
.pill-red   { background: #d92626; color: #ffffff; text-shadow: 1px 1px 0 #000; }
</style>
"""


def apply_theme():
    """Injects global Minecraft styling and resets Matplotlib theme."""
    st.markdown(MINECRAFT_CSS, unsafe_allow_html=True)
    plt.rcParams.update({
        'figure.facecolor':  '#ffffff',
        'axes.facecolor':    '#ffffff',
        'axes.edgecolor':    '#000000',
        'axes.linewidth':    2.5,
        'axes.spines.top':   True,
        'axes.spines.right': True,
        'axes.spines.left':  True,
        'axes.spines.bottom': True,
        'text.color':        '#000000',
        'axes.labelcolor':   '#000000',
        'axes.titlecolor':   '#000000',
        'xtick.color':       '#000000',
        'ytick.color':       '#000000',
        'grid.color':        '#cccccc',
        'grid.linewidth':    1.5,
        'grid.alpha':        0.9,
        'font.family':       ['Courier New', 'monospace', 'sans-serif'],
        'font.weight':       'bold',
        'font.size':         11,
        'axes.titlesize':    13,
        'axes.titleweight':  'bold',
        'axes.labelsize':    11,
        'axes.labelweight':  'bold',
        'xtick.labelsize':   10.5,
        'ytick.labelsize':   10.5,
        'legend.fontsize':   10,
        'legend.framealpha': 1.0,
        'legend.edgecolor':  '#000000',
    })


def sec(label):
    st.markdown(f'<div class="sec-label">{label}</div>', unsafe_allow_html=True)


def notice(icon, text, kind="blue"):
    st.markdown(f'<div class="notice notice-{kind}">{icon} <span>{text}</span></div>', unsafe_allow_html=True)


def kpi_card(label, value, unit, sub, accent="lime"):
    return f"""<div class="card card-{accent}">
        <div class="card-label">{label}</div>
        <div class="card-value">{value}<span>{unit}</span></div>
        <div class="card-sub">{sub}</div>
    </div>"""


def chart_card_start(title):
    st.markdown(f'<div class="chart-card"><div class="chart-card-title">{title}</div>', unsafe_allow_html=True)


def chart_card_end():
    st.markdown('</div>', unsafe_allow_html=True)


def render_fig(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight", transparent=False, facecolor="#ffffff")
    buf.seek(0)
    st.image(buf, use_container_width=True)
    plt.close(fig)
