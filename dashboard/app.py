import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import time
import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import time
import sys
import os

# ── Add project root to path so data/ and intelligence/ are importable ──
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

API_BASE = "http://localhost:8000"
API_KEY = "procureiq-secret-2026"
HEADERS = {"x-api-key": API_KEY}



st.set_page_config(
    page_title="ProcureIQ",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── MASTER CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Bebas+Neue&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

/* Palette: red #FF0000, crimson #C00000, black #000000, gray #707070, white #FFFFFF */
:root {
    --piq-red: #FF0000;
    --piq-crimson: #C00000;
    --piq-black: #000000;
    --piq-gray: #707070;
    --piq-white: #FFFFFF;
    --piq-surface: #0a0a0a;
    --piq-border: rgba(112, 112, 112, 0.4);
    --piq-border-subtle: rgba(112, 112, 112, 0.2);
}

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: var(--piq-black) !important;
    color: var(--piq-white) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    letter-spacing: 0.01em;
}

.block-container {
    padding: 2rem 2.5rem 2rem 2rem !important;
    max-width: 100% !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer { visibility: hidden !important; }
.stDeployButton { display: none !important; }
header[data-testid="stHeader"] { background-color: #000000 !important; }

/* ── Animated background grid ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,0,0,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(112,112,112,0.06) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
    animation: gridPulse 8s ease-in-out infinite;
}

@keyframes gridPulse {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 1; }
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--piq-black) !important;
    border-right: 1px solid var(--piq-border) !important;
    padding: 0 !important;
}

[data-testid="stSidebar"] > div {
    padding: 2rem 1.4rem !important;
}

/* ── Logo area ── */
.logo-block {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--piq-border-subtle);
}

.logo-hex {
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, var(--piq-red), var(--piq-crimson));
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    display: flex;
    align-items: center;
    justify-content: center;
    animation: hexPulse 3s ease-in-out infinite;
    flex-shrink: 0;
}

@keyframes hexPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255,0,0,0); }
    50% { box-shadow: 0 0 20px 6px rgba(255,0,0,0.25); }
}

.logo-text {
    font-family: 'Archivo Black', sans-serif !important;
    font-size: 1.4rem !important;
    font-weight: 400 !important;
    color: var(--piq-white) !important;
    letter-spacing: 0.02em;
    line-height: 1;
}

.logo-sub {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.6rem !important;
    color: var(--piq-red) !important;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 2px;
}

/* ── Sidebar section labels ── */
.sidebar-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.62rem !important;
    font-weight: 500 !important;
    color: var(--piq-crimson) !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    margin-bottom: 0.8rem !important;
    margin-top: 1.6rem !important;
    display: block;
}

/* ── Streamlit inputs override ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input {
    background: var(--piq-surface) !important;
    border: 1px solid var(--piq-border-subtle) !important;
    border-radius: 0 !important;
    color: var(--piq-white) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.88rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--piq-red) !important;
    box-shadow: 0 0 0 2px rgba(255,0,0,0.2) !important;
    outline: none !important;
}

[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stDateInput"] label {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: var(--piq-gray) !important;
    letter-spacing: 0.03em !important;
}

/* ── Primary button (Space Grotesk — refined CTA) ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--piq-crimson), var(--piq-red)) !important;
    border: none !important;
    border-radius: 0 !important;
    color: var(--piq-white) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    padding: 0.7rem 1.5rem !important;
    width: 100% !important;
    transition: all 0.25s !important;
    position: relative !important;
    overflow: hidden !important;
}

.stButton > button[kind="primary"]::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.1), transparent);
    opacity: 0;
    transition: opacity 0.2s;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(192,0,0,0.45) !important;
}

/* ── Secondary button ── */
.stButton > button:not([kind="primary"]) {
    background: transparent !important;
    border: 1px solid var(--piq-border) !important;
    border-radius: 0 !important;
    color: var(--piq-gray) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}

.stButton > button:not([kind="primary"]):hover {
    border-color: var(--piq-red) !important;
    color: var(--piq-red) !important;
    background: rgba(255,0,0,0.06) !important;
}

/* ── KPI cards (display font: Bebas Neue ≈ bold poster / WOSKER-style impact) ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}

.kpi-card {
    background: var(--piq-surface);
    border: 1px solid var(--piq-border-subtle);
    border-radius: 0;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.35s ease, box-shadow 0.35s ease, transform 0.25s ease;
    animation: kpiCardEnter 0.75s cubic-bezier(0.22, 1, 0.36, 1) both;
    cursor: help;
    box-shadow: 0 0 20px rgba(255, 0, 0, 0.15), inset 0 0 20px rgba(255, 0, 0, 0.08);
}

.kpi-card:hover {
    border-color: rgba(255, 0, 0, 0.5) !important;
    box-shadow: 0 0 40px rgba(255, 0, 0, 0.35), 0 0 80px rgba(255, 0, 0, 0.2), inset 0 0 30px rgba(255, 0, 0, 0.12);
    transform: translateY(-4px) scale(1.02);
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255,0,0,0.45), transparent);
    opacity: 0.85;
}

/* One-time light sweep (premium "flash") */
.kpi-card::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(
        100deg,
        transparent 0%,
        transparent 42%,
        rgba(255, 255, 255, 0.06) 50%,
        transparent 58%,
        transparent 100%
    );
    transform: translateX(-120%);
    pointer-events: none;
    animation: kpiShimmerSweep 1.1s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.kpi-card:nth-child(1) { animation-delay: 0s; }
.kpi-card:nth-child(2) { animation-delay: 0.08s; }
.kpi-card:nth-child(3) { animation-delay: 0.16s; }
.kpi-card:nth-child(4) { animation-delay: 0.24s; }

.kpi-card:nth-child(1)::after { animation-delay: 0.25s; }
.kpi-card:nth-child(2)::after { animation-delay: 0.38s; }
.kpi-card:nth-child(3)::after { animation-delay: 0.51s; }
.kpi-card:nth-child(4)::after { animation-delay: 0.64s; }

@keyframes kpiCardEnter {
    from {
        opacity: 0;
        transform: translateY(22px) scale(0.97);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes kpiShimmerSweep {
    to { transform: translateX(120%); }
}

@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── KPI Tooltip ── */
.kpi-tooltip {
    position: relative;
}

.kpi-tooltip .tooltip-text {
    visibility: hidden;
    width: 200px;
    background-color: rgba(255, 0, 0, 0.15);
    color: #FFFFFF;
    text-align: center;
    border: 1px solid rgba(255, 0, 0, 0.35);
    border-radius: 0;
    padding: 8px 12px;
    position: absolute;
    z-index: 1000;
    bottom: 125%;
    left: 50%;
    margin-left: -100px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    line-height: 1.4;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
}

.kpi-card:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}

.kpi-tooltip .tooltip-text::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: rgba(255, 0, 0, 0.15) transparent transparent transparent;
}

.kpi-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;  /* ← Slightly larger */
    font-weight: 700 !important;  /* ← Heavier */
    color: #FF0000 !important;  /* ← Pure red */
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.9rem;
    text-shadow: 0 0 10px rgba(255, 0, 0, 0.4);  /* ← Red glow */
}

.kpi-value {
    font-family: 'Bebas Neue', 'Archivo Black', sans-serif;
    font-size: 3.2rem !important;  /* ← Increased from 2.85rem */
    font-weight: 900 !important;  /* ← Heavier weight */
    color: var(--piq-white);
    line-height: 0.95;
    letter-spacing: 0.08em;  /* ← More spacing */
    display: inline-block;
    animation: kpiNumberPop 0.85s cubic-bezier(0.34, 1.2, 0.64, 1) both;
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.3), 0 0 40px rgba(255, 255, 255, 0.1);
}

.kpi-card:nth-child(1) .kpi-value { animation-delay: 0.2s; }
.kpi-card:nth-child(2) .kpi-value { animation-delay: 0.32s; }
.kpi-card:nth-child(3) .kpi-value { animation-delay: 0.44s; }
.kpi-card:nth-child(4) .kpi-value { animation-delay: 0.56s; }

@keyframes kpiNumberPop {
    from {
        opacity: 0;
        transform: translateY(14px) scale(0.82);
        filter: blur(4px);
    }
    70% {
        opacity: 1;
        transform: translateY(0) scale(1.04);
        filter: blur(0);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
        filter: blur(0);
    }
}

.kpi-value.green { color: #48bb78; text-shadow: 0 0 20px rgba(72, 187, 120, 0.5), 0 0 40px rgba(72, 187, 120, 0.3); }
.kpi-value.amber { color: #ffb347; text-shadow: 0 0 20px rgba(255, 179, 71, 0.5), 0 0 40px rgba(255, 179, 71, 0.3); }
.kpi-value.accent { color: #FF0000; text-shadow: 0 0 20px rgba(255, 0, 0, 0.6), 0 0 40px rgba(255, 0, 0, 0.4); }
.kpi-value.online { color: #48bb78; text-shadow: 0 0 20px rgba(72, 187, 120, 0.5), 0 0 40px rgba(72, 187, 120, 0.3); }
.kpi-value.offline { color: #ff6b6b; text-shadow: 0 0 20px rgba(255, 107, 107, 0.5), 0 0 40px rgba(255, 107, 107, 0.3); }

.kpi-sub {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    color: var(--piq-gray);
    margin-top: 0.4rem;
    font-weight: 500;
}

/* ── Section header ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1.2rem;
}

.section-title {
    font-family: 'Archivo Black', sans-serif !important;
    font-size: 1.3rem !important;  /* ← Increased from 1.15rem */
    font-weight: 800 !important;  /* ← Heavier (from 600) */
    color: #FFFFFF !important;
    letter-spacing: 0.08em !important;  /* ← More spacing */
    text-transform: uppercase;
    text-shadow: 0 0 15px rgba(255, 255, 255, 0.2);  /* ← Subtle glow */
}

.section-line {
    flex: 1;
    height: 2px;  /* ← Slightly thicker */
    background: linear-gradient(90deg, rgba(255, 0, 0, 0.6), transparent);
    box-shadow: 0 0 10px rgba(255, 0, 0, 0.5), 0 0 20px rgba(255, 0, 0, 0.3);  /* ← Luminous glow */
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    background: var(--piq-surface) !important;
    border: 1px solid var(--piq-border-subtle) !important;
    border-radius: 0 !important;
    padding: 4px !important;
    gap: 2px !important;
}

[data-testid="stTabs"] [role="tab"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: var(--piq-gray) !important;
    border-radius: 0 !important;
    padding: 0.5rem 1.2rem !important;
    border: none !important;
    transition: all 0.2s !important;
}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: rgba(192,0,0,0.25) !important;
    color: var(--piq-red) !important;
}

[data-testid="stTabs"] [role="tabpanel"] {
    padding-top: 1.5rem !important;
}

/* ── Audit line ── */
.audit-line {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 6px 0;
    border-bottom: 1px solid var(--piq-border-subtle);
    animation: fadeIn 0.3s ease both;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateX(-6px); }
    to   { opacity: 1; transform: translateX(0); }
}

.audit-dot {
    width: 6px;
    height: 6px;
    border-radius: 0;
    background: var(--piq-red);
    margin-top: 6px;
    flex-shrink: 0;
    box-shadow: 0 0 6px rgba(255,0,0,0.5);
}

.audit-dot.warn { background: #ed8936; box-shadow: 0 0 6px rgba(237,137,54,0.6); }
.audit-dot.ok   { background: #48bb78; box-shadow: 0 0 6px rgba(72,187,120,0.6); }
.audit-dot.note { background: #a78bfa; box-shadow: 0 0 6px rgba(167,139,250,0.6); }

.audit-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--piq-gray);
    white-space: nowrap;
    margin-top: 3px;
    min-width: 80px;
}

.audit-text {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.78rem;
    color: var(--piq-gray);
    line-height: 1.5;
}

.audit-text strong { color: var(--piq-white); }

/* ── Supplier card ── */
.supplier-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    align-items: center;
    gap: 12px;
    padding: 1rem 1.2rem;
    background: var(--piq-surface);
    border: 1px solid var(--piq-border-subtle);
    border-radius: 0;
    margin-bottom: 8px;
    transition: border-color 0.2s, background 0.2s;
    animation: fadeSlideUp 0.5s ease both;
}

.supplier-row:hover {
    border-color: var(--piq-border);
    background: #141414;
}

.supplier-name {
    font-family: 'Archivo Black', sans-serif;
    font-size: 0.88rem;
    font-weight: 400;
    color: var(--piq-white);
    letter-spacing: 0.01em;
}

.supplier-url {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--piq-red);
    margin-top: 2px;
}

.supplier-price {
    font-family: 'Archivo Black', sans-serif;
    font-size: 1rem;
    font-weight: 400;
    color: var(--piq-white);
}

.supplier-price-sub {
    font-size: 0.62rem;
    color: var(--piq-gray);
    font-family: 'JetBrains Mono', monospace;
}

.risk-bar-wrap {
    background: #141414;
    border-radius: 0;
    height: 6px;
    overflow: hidden;
    margin-top: 4px;
}

.risk-bar {
    height: 100%;
    border-radius: 0;
    transition: width 1s ease;
}

.risk-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    font-weight: 500;
    margin-bottom: 3px;
}

.risk-low  { color: #48bb78; }
.risk-med  { color: #ed8936; }
.risk-high { color: #fc8181; }

/* ── Status badge ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.badge-pending {
    background: rgba(237,137,54,0.1);
    border: 1px solid rgba(237,137,54,0.25);
    color: #ed8936;
}

.badge-done {
    background: rgba(72,187,120,0.1);
    border: 1px solid rgba(72,187,120,0.25);
    color: #48bb78;
}

.badge-dot {
    width: 5px; height: 5px;
    border-radius: 0;
    background: currentColor;
    animation: blink 1.4s ease infinite;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ── PO / ref block ── */
.ref-block {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 1.2rem 0;
}

.ref-card {
    background: var(--piq-surface);
    border: 1px solid var(--piq-border-subtle);
    border-radius: 0;
    padding: 1rem 1.2rem;
    animation: fadeSlideUp 0.5s ease both;
}

.ref-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: var(--piq-crimson);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.ref-value {
    font-family: 'Archivo Black', sans-serif;
    font-size: 1.1rem;
    font-weight: 400;
    color: var(--piq-white);
    letter-spacing: 0.01em;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: var(--piq-surface) !important;
    border: 1px solid var(--piq-border-subtle) !important;
    border-radius: 0 !important;
    margin-bottom: 8px !important;
}

[data-testid="stExpander"] summary {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    color: var(--piq-white) !important;
    padding: 1rem 1.2rem !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--piq-border-subtle) !important;
    margin: 1.5rem 0 !important;
}

/* ── Success / error ── */
[data-testid="stAlert"] {
    border-radius: 0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.82rem !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    color: var(--piq-red) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--piq-black); }
::-webkit-scrollbar-thumb { background: var(--piq-gray); border-radius: 0; }
::-webkit-scrollbar-thumb:hover { background: var(--piq-red); }

/* Streamlit extras — match sharp / black theme */
[data-testid="stVerticalBlockBorderWrapper"] > div,
[data-testid="stForm"] {
    border-radius: 0 !important;
}

/* ── Page Title Styling (BIGGEST & HEAVIEST & BRIGHTEST) ── */
.page-title {
    font-family: 'Archivo Black', sans-serif;
    font-size: 4.8rem !important;  /* ← Even larger for max impact */
    font-weight: 900 !important;  /* ← MAXIMUM weight (ultra-heavy like WOSKER) */
    color: #FFFFFF !important;  /* ← Pure bright white */
    letter-spacing: -0.03em;  /* ← Tighter spacing for impact */
    line-height: 1.25;
    margin-bottom: 0.8rem;
    text-transform: uppercase;
    padding: 0.8rem 0;
    font-stretch: expanded;  /* ← Extra visual weight */
}

.page-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #FF0000;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────
if "requests_log" not in st.session_state:
    st.session_state.requests_log = []
if "current_result" not in st.session_state:
    st.session_state.current_result = None
if "current_request_id" not in st.session_state:
    st.session_state.current_request_id = None
if "sidebar_expanded" not in st.session_state:
    st.session_state.sidebar_expanded = True


# ── Helper: parse audit line ───────────────────────────────
def parse_audit(line: str):
    dot_class = "accent"
    if "NOTE" in line or "note" in line.lower():
        dot_class = "note"
    elif "WAIT" in line or "falling" in line or "ESCALATE" in line:
        dot_class = "warn"
    elif "completed" in line.lower() or "generated" in line.lower() or "approved" in line.lower():
        dot_class = "ok"

    time_part = ""
    text_part = line
    if line.startswith("["):
        try:
            end = line.index("]")
            raw_time = line[1:end]
            dt = datetime.fromisoformat(raw_time)
            time_part = dt.strftime("%H:%M:%S")
            text_part = line[end+2:]
        except:
            pass

    return dot_class, time_part, text_part


def render_audit_log(log: list):
    for i, line in enumerate(log):
        dot_class, time_part, text_part = parse_audit(line)
        st.markdown(f"""
        <div class="audit-line" style="animation-delay:{i*0.04}s">
            <div class="audit-dot {dot_class}"></div>
            <div class="audit-time">{time_part}</div>
            <div class="audit-text">{text_part}</div>
        </div>""", unsafe_allow_html=True)


def risk_color(score: float) -> str:
    if score < 0.4:   return "#48bb78"
    elif score < 0.7: return "#ed8936"
    else:             return "#fc8181"

def risk_class(score: float) -> str:
    if score < 0.4:   return "risk-low"
    elif score < 0.7: return "risk-med"
    else:             return "risk-high"


# ── SIDEBAR ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="logo-block">
        <div class="logo-hex"></div>
        <div>
            <div class="logo-text">ProcureIQ</div>
            <div class="logo-sub">Autonomous Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown('<span class="sidebar-label">New Request</span>', unsafe_allow_html=True)
    item = st.text_input("Item", placeholder="e.g. industrial sensors", label_visibility="visible")
    quantity = st.number_input("Quantity", min_value=1, max_value=100000, value=500)
    budget = st.number_input("Budget (₹)", min_value=1000.0, value=250000.0, step=1000.0)
    min_deadline = (datetime.now() + timedelta(days=1)).date()
    deadline = st.date_input("Deadline", min_value=min_deadline, value=min_deadline)

    submit = st.button("⬡ Run Procurement", use_container_width=True, type="primary")

    if submit:
        if not item.strip():
            st.error("Enter an item name.")
        else:
            with st.spinner("Agents running — 20–30 sec..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/procure",
                        json={"item": item.strip(), "quantity": int(quantity),
                              "budget": float(budget), "deadline": str(deadline)},
                        headers=HEADERS, timeout=150
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.current_request_id = data["request_id"]
                        st.session_state.current_result = data
                        st.session_state.requests_log.append({
                            "request_id": data["request_id"],
                            "item": item.strip(),
                            "quantity": quantity,
                            "budget": budget,
                            "status": "awaiting_approval",
                            "audit_log": data.get("audit_log", []),
                            "po_number": ""
                        })
                        st.success("Done. Awaiting approval.")
                    else:
                        st.error(f"{resp.status_code}: {resp.text}")
                except Exception as e:
                    st.error(str(e))

    st.markdown('<span class="sidebar-label">Approve Request</span>', unsafe_allow_html=True)
    approve_id = st.text_input("Request ID", placeholder="paste request_id", key="approve_id_input")
    approve_notes = st.text_input("Notes", placeholder="optional", key="approve_notes_input")
    approve_btn = st.button("✓ Approve & Generate Docs", use_container_width=True)

    if approve_btn and approve_id:
        with st.spinner("Resuming workflow..."):
            try:
                resp = requests.post(
                    f"{API_BASE}/approve/{approve_id}",
                    params={"notes": approve_notes},
                    headers=HEADERS, timeout=150
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.current_result = data
                    st.session_state.current_request_id = approve_id
                    for r in st.session_state.requests_log:
                        if r["request_id"] == approve_id:
                            r["status"] = "completed"
                            r["po_number"] = data.get("po_number", "")
                            r["audit_log"] = data.get("audit_log", [])
                    st.success(f"PO: {data.get('po_number')}")
                else:
                    st.error(f"{resp.status_code}: {resp.text}")
            except Exception as e:
                st.error(str(e))

    # API health
    st.markdown('<span class="sidebar-label">System</span>', unsafe_allow_html=True)
    try:
        h = requests.get(f"{API_BASE}/health", timeout=3)
        online = h.status_code == 200
    except:
        online = False

    status_color = "#48bb78" if online else "#fc8181"
    status_text = "API ONLINE" if online else "API OFFLINE"
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;padding:10px 12px;
                background:#0a0a0a;border:1px solid rgba(112,112,112,0.35);
                border-radius:0;margin-top:4px;">
        <div style="width:7px;height:7px;border-radius:0;background:{status_color};
                    box-shadow:0 0 8px {status_color};animation:blink 1.4s infinite;"></div>
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                     color:{status_color};letter-spacing:0.12em;">{status_text}</span>
    </div>""", unsafe_allow_html=True)


# ── MAIN AREA ──────────────────────────────────────────────

# Page title
total = len(st.session_state.requests_log)
completed = sum(1 for r in st.session_state.requests_log if r["status"] == "completed")
pending = total - completed

st.markdown("""
<div style="margin-bottom:1.8rem;">
    <div class="page-title">Procurement Intelligence</div>
    <div class="page-subtitle">
        Autonomous · Multi-Agent · Real-Time
    </div>
</div>
""", unsafe_allow_html=True)

# KPI cards with tooltips
st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card kpi-tooltip">
        <div class="tooltip-text">Total procurement requests submitted to the system since launch</div>
        <div class="kpi-tag">Total Requests</div>
        <div class="kpi-value accent">{total}</div>
        <div class="kpi-sub">All time submissions</div>
    </div>
    <div class="kpi-card kpi-tooltip">
        <div class="tooltip-text">Requests that have successfully completed and generated purchase orders</div>
        <div class="kpi-tag">Completed</div>
        <div class="kpi-value green">{completed}</div>
        <div class="kpi-sub">PO generated</div>
    </div>
    <div class="kpi-card kpi-tooltip">
        <div class="tooltip-text">Requests pending human approval before document generation</div>
        <div class="kpi-tag">Awaiting Approval</div>
        <div class="kpi-value amber">{pending}</div>
        <div class="kpi-sub">Human review needed</div>
    </div>
    <div class="kpi-card kpi-tooltip">
        <div class="tooltip-text">Backend API server connection status and availability</div>
        <div class="kpi-tag">API Status</div>
        <div class="kpi-value {'online' if online else 'offline'}">{'Online' if online else 'Offline'}</div>
        <div class="kpi-sub">localhost:8000</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["⬡  Current Run", "≡  All Requests", "⬖  Documents", "◈  Analytics"])


# ── TAB 1 ──────────────────────────────────────────────────
with tab1:
    result = st.session_state.current_result
    if not result:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;opacity:0.4;">
            <div style="font-family:'Archivo Black',sans-serif;font-size:3rem;margin-bottom:1rem;">⬡</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:0.9rem;color:#707070;">
                Submit a procurement request from the sidebar
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        request_id = st.session_state.current_request_id
        status = result.get("status", "awaiting_approval")
        is_done = status == "completed"

        badge_html = f'<span class="badge badge-{"done" if is_done else "pending"}"><div class="badge-dot"></div>{"COMPLETED" if is_done else "AWAITING APPROVAL"}</span>'

        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.4rem;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;
                        color:#707070;letter-spacing:0.1em;">REQUEST ID</div>
            {badge_html}
        </div>""", unsafe_allow_html=True)
        st.code(request_id, language=None)
        st.markdown("""
        <style>
        [data-testid="stCode"] {
            background: #000000 !important;
            border-radius: 0 !important;
            border: 1px solid rgba(112,112,112,0.3) !important;
            padding: 4px 8px !important;
        }
        [data-testid="stCode"] code {
            font-size: 0.72rem !important;
            color: #FF0000 !important;
            background: transparent !important;
        }
        [data-testid="stCode"] pre {
            background: transparent !important;
            padding: 2px 0 !important;
            margin: 0 !important;
        }
        [data-testid="stCode"] button {
            background: transparent !important;
            border: 1px solid rgba(112,112,112,0.4) !important;
            border-radius: 0 !important;
            color: #707070 !important;
            padding: 2px 6px !important;
        }
        [data-testid="stCode"] button:hover {
            border-color: #FF0000 !important;
            color: #FF0000 !important;
        }
        [data-testid="stCode"] button svg {
            fill: #707070 !important;
            width: 12px !important;
            height: 12px !important;
        }
        [data-testid="stCode"] button:hover svg {
            fill: #FF0000 !important;
        }
        </style>""", unsafe_allow_html=True)

        if is_done:
            po = result.get("po_number", "—")
            rfq = result.get("rfq_reference", f"RFQ-{request_id[:8].upper()}")
            con = result.get("contract_reference", f"CON-{request_id[:8].upper()}")
            st.markdown(f"""
            <div class="ref-block">
                <div class="ref-card">
                    <div class="ref-tag">Purchase Order</div>
                    <div class="ref-value">{po}</div>
                </div>
                <div class="ref-card">
                    <div class="ref-tag">RFQ Reference</div>
                    <div class="ref-value">{rfq}</div>
                </div>
                <div class="ref-card">
                    <div class="ref-tag">Contract Reference</div>
                    <div class="ref-value">{con}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        # Audit log
        st.markdown("""
        <div class="section-header">
            <span class="section-title">Audit Trail</span>
            <div class="section-line"></div>
        </div>""", unsafe_allow_html=True)

        audit = result.get("audit_log", [])
        if audit:
            render_audit_log(audit)
        else:
            st.markdown("<div style='color:#707070;font-size:0.8rem;'>No log yet.</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("↻  Refresh Status", key="refresh_btn"):
            try:
                resp = requests.get(f"{API_BASE}/status/{request_id}", timeout=10)
                if resp.status_code == 200:
                    fresh = resp.json()
                    st.session_state.current_result = {
                        **result,
                        "audit_log": fresh.get("audit_log", []),
                        "status": "completed" if fresh.get("po_number") else "awaiting_approval",
                        "po_number": fresh.get("po_number", ""),
                    }
                    st.rerun()
            except Exception as e:
                st.error(str(e))


# ── TAB 2 ──────────────────────────────────────────────────
with tab2:
    if not st.session_state.requests_log:
        st.markdown("""
        <div style="text-align:center;padding:3rem;opacity:0.35;">
            <div style="font-family:'Space Grotesk',sans-serif;font-size:0.85rem;color:#707070;">
                No requests submitted yet.
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        for r in reversed(st.session_state.requests_log):
            is_done = r["status"] == "completed"
            badge = f'<span class="badge badge-{"done" if is_done else "pending"}"><div class="badge-dot"></div>{"DONE" if is_done else "PENDING"}</span>'
            po_display = r.get("po_number") or "—"

            with st.expander(f"  {r['item'].upper()}  ·  ×{r['quantity']:,}  ·  ₹{r['budget']:,.0f}"):
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#FF0000;">
                        {r['request_id']}
                    </div>
                    {badge}
                </div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:1rem;">
                    <div style="background:#0a0a0a;border:1px solid rgba(112,112,112,0.25);border-radius:0;padding:0.8rem;">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#C00000;letter-spacing:0.15em;margin-bottom:4px;">QUANTITY</div>
                        <div style="font-family:'Archivo Black',sans-serif;font-size:1.1rem;font-weight:400;color:#FFFFFF;">{r['quantity']:,}</div>
                    </div>
                    <div style="background:#0a0a0a;border:1px solid rgba(112,112,112,0.25);border-radius:0;padding:0.8rem;">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#C00000;letter-spacing:0.15em;margin-bottom:4px;">BUDGET</div>
                        <div style="font-family:'Archivo Black',sans-serif;font-size:1.1rem;font-weight:400;color:#FFFFFF;">₹{r['budget']:,.0f}</div>
                    </div>
                    <div style="background:#0a0a0a;border:1px solid rgba(112,112,112,0.25);border-radius:0;padding:0.8rem;">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#C00000;letter-spacing:0.15em;margin-bottom:4px;">PO NUMBER</div>
                        <div style="font-family:'Archivo Black',sans-serif;font-size:1.1rem;font-weight:400;color:#FFFFFF;">{po_display}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

                st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;
                            color:#C00000;letter-spacing:0.15em;text-transform:uppercase;
                            margin-bottom:8px;">Audit Log</div>""", unsafe_allow_html=True)
                render_audit_log(r.get("audit_log", []))


# ── TAB 3 ──────────────────────────────────────────────────
with tab3:
    st.markdown("""
    <div class="section-header">
        <span class="section-title">Document Viewer</span>
        <div class="section-line"></div>
    </div>""", unsafe_allow_html=True)

    rid = st.text_input("Request ID", placeholder="paste completed request_id", key="doc_rid")
    fetch = st.button("Fetch Documents", key="fetch_docs")

    if fetch and rid:
        try:
            resp = requests.get(f"{API_BASE}/status/{rid}", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("po_number"):
                    supplier = data.get("selected_supplier") or {}

                    st.markdown(f"""
                    <div class="ref-block" style="margin-top:0;">
                        <div class="ref-card">
                            <div class="ref-tag">Purchase Order</div>
                            <div class="ref-value">{data['po_number']}</div>
                        </div>
                        <div class="ref-card">
                            <div class="ref-tag">Selected Vendor</div>
                            <div class="ref-value">{supplier.get('name','—')}</div>
                        </div>
                        <div class="ref-card">
                            <div class="ref-tag">Price Per Unit</div>
                            <div class="ref-value">₹{supplier.get('price',0):,.0f}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)

                    if supplier:
                        risk = supplier.get("risk_score", 0)
                        rc = risk_color(risk)
                        rcls = risk_class(risk)
                        st.markdown(f"""
                        <div class="supplier-row" style="margin-top:1rem;">
                            <div>
                                <div class="supplier-name">{supplier.get('name','—')}</div>
                                <div class="supplier-url">{supplier.get('url','—')}</div>
                            </div>
                            <div>
                                <div class="supplier-price">₹{supplier.get('price',0):,.0f}</div>
                                <div class="supplier-price-sub">per unit</div>
                            </div>
                            <div>
                                <div class="risk-label {rcls}">{risk:.3f} risk</div>
                                <div class="risk-bar-wrap">
                                    <div class="risk-bar" style="width:{risk*100:.1f}%;background:{rc};"></div>
                                </div>
                            </div>
                            <div style="font-family:'Space Grotesk',sans-serif;font-size:0.75rem;color:#707070;">
                                {supplier.get('notes','—')}
                            </div>
                        </div>""", unsafe_allow_html=True)

                    st.markdown("""
                    <div class="section-header" style="margin-top:1.5rem;">
                        <span class="section-title">Full Audit Trail</span>
                        <div class="section-line"></div>
                    </div>""", unsafe_allow_html=True)
                    render_audit_log(data.get("audit_log", []))

                else:
                    st.warning("This request is not yet completed. Approve it first.")
            else:
                st.error("Request ID not found.")
        except Exception as e:
            st.error(str(e))

# ── TAB 4 — Analytics ──────────────────────────────────────
with tab4:
    st.markdown("""
    <div class="section-header">
        <span class="section-title">Spend Analytics</span>
        <div class="section-line"></div>
    </div>""", unsafe_allow_html=True)

    try:
        from data.db_ops import get_all_procurements, get_all_spend_records
        from intelligence.spend_analytics import summarize_spend

        spend_records = get_all_spend_records()
        summary = summarize_spend(spend_records)

        # KPI row
        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-tag">Total Requests</div>
                <div class="kpi-value">{summary['total_requests']}</div>
                <div class="kpi-sub">All time</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-tag">Total Spend</div>
                <div class="kpi-value">&#8377;{summary['total_spend']:,.0f}</div>
                <div class="kpi-sub">Across all POs</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-tag">Total Savings</div>
                <div class="kpi-value" style="color:#00c853;">&#8377;{summary['total_savings']:,.0f}</div>
                <div class="kpi-sub">vs market average</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-tag">Avg Savings</div>
                <div class="kpi-value" style="color:#FF0000;">{summary['avg_savings_pct']}%</div>
                <div class="kpi-sub">Per procurement</div>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Decision breakdown
        decisions = summary.get("decisions", {})
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="section-header">
                <span class="section-title">Decision Breakdown</span>
                <div class="section-line"></div>
            </div>""", unsafe_allow_html=True)
            for decision, count in decisions.items():
                color = {"buy": "#00c853", "wait": "#ff6d00", "escalate": "#ff0000"}.get(decision, "#707070")
                pct = round((count / summary['total_requests'] * 100), 1) if summary['total_requests'] > 0 else 0
                st.markdown(f"""
                <div style="display:flex;align-items:center;justify-content:space-between;
                            padding:10px 14px;background:#0a0a0a;border-left:3px solid {color};
                            margin-bottom:6px;">
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                                 color:{color};letter-spacing:0.1em;text-transform:uppercase;">
                        {decision}</span>
                    <span style="font-family:'Archivo Black',sans-serif;font-size:1.1rem;
                                 color:#ffffff;">{count}
                        <span style="font-size:0.65rem;color:#707070;font-family:'JetBrains Mono',monospace;">
                            ({pct}%)</span>
                    </span>
                </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="section-header">
                <span class="section-title">Top Suppliers by Spend</span>
                <div class="section-line"></div>
            </div>""", unsafe_allow_html=True)
            top = summary.get("top_suppliers", [])
            if top:
                max_spend = top[0][1] if top else 1
                for name, spend in top:
                    bar_pct = int((spend / max_spend) * 100)
                    st.markdown(f"""
                    <div style="margin-bottom:10px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                            <span style="font-family:'Space Grotesk',sans-serif;font-size:0.78rem;
                                         color:#ffffff;">{name}</span>
                            <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                                         color:#C00000;">&#8377;{spend:,.0f}</span>
                        </div>
                        <div style="background:#1a1a1a;height:4px;">
                            <div style="width:{bar_pct}%;height:100%;
                                        background:linear-gradient(90deg,#C00000,#FF0000);"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:#707070;font-size:0.8rem;'>No data yet.</div>",
                           unsafe_allow_html=True)

        # Spend records table
        if spend_records:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div class="section-header">
                <span class="section-title">All Procurement Records</span>
                <div class="section-line"></div>
            </div>""", unsafe_allow_html=True)

            for r in reversed(spend_records):
                savings_color = "#00c853" if r['total_savings'] > 0 else "#ff6d00" if r['total_savings'] < 0 else "#707070"
                st.markdown(f"""
                <div class="supplier-row">
                    <div>
                        <div class="supplier-name">{r['item'].title()}</div>
                        <div class="supplier-url">{r['supplier_name']} · {r.get('po_number','—')}</div>
                    </div>
                    <div>
                        <div class="supplier-price">&#8377;{r['total_spend']:,.0f}</div>
                        <div class="supplier-price-sub">total spend</div>
                    </div>
                    <div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                                    color:{savings_color};">
                            &#8377;{r['total_savings']:,.0f}</div>
                        <div class="supplier-price-sub">savings</div>
                    </div>
                    <div>
                        <div class="risk-label {'risk-low' if r['risk_score'] < 0.4 else 'risk-med' if r['risk_score'] < 0.7 else 'risk-high'}">
                            {r['risk_score']:.3f} risk</div>
                        <div class="risk-bar-wrap">
                            <div class="risk-bar" style="width:{r['risk_score']*100:.1f}%;
                                background:{risk_color(r['risk_score'])};"></div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Analytics error: {e}")
        st.info("Run at least one complete procurement to see analytics.")