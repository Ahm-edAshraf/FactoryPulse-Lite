"""Reusable UI fragments and theme helpers for Streamlit pages."""

from __future__ import annotations

from html import escape

import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap');

        :root {
          --bg-primary: #0c0e14;
          --bg-card: #151823;
          --bg-card-alt: #1a1e2e;
          --bg-elevated: #1e2235;
          --border: rgba(255, 255, 255, 0.06);
          --border-subtle: rgba(255, 255, 255, 0.03);
          --text-primary: #f0f2f5;
          --text-secondary: #8b92a5;
          --text-muted: #5c6378;
          --accent: #00d4aa;
          --accent-soft: rgba(0, 212, 170, 0.12);
          --accent-glow: rgba(0, 212, 170, 0.25);
          --healthy: #00d4aa;
          --watchlist: #f0b429;
          --impaired: #e8734a;
          --critical: #ef4444;
          --info: #3b82f6;
          --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
          --shadow-md: 0 8px 32px rgba(0, 0, 0, 0.4);
          --shadow-glow: 0 0 40px rgba(0, 212, 170, 0.08);
          --radius: 16px;
          --radius-sm: 10px;
          --radius-xs: 6px;
        }

        html, body, [class*="css"] {
          font-family: 'DM Sans', sans-serif;
          color: var(--text-primary);
        }

        #MainMenu, footer, [data-testid="stToolbar"],
        [data-testid="stDecoration"], [data-testid="stStatusWidget"], header {
          display: none !important;
        }

        .stApp {
          background: var(--bg-primary);
        }

        .block-container {
          max-width: 1400px;
          padding: 1.5rem 2rem 2.5rem 2rem;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
          background: #0e1018;
          border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] .block-container {
          padding: 0.75rem 0.75rem;
        }

        [data-testid="stSidebarNav"] { margin-top: 0.5rem; }

        [data-testid="stSidebarNav"] li {
          border-radius: var(--radius-sm);
          margin-bottom: 2px;
        }

        [data-testid="stSidebarNav"] li a {
          border-radius: var(--radius-sm);
          color: var(--text-secondary) !important;
          font-weight: 500;
        }

        [data-testid="stSidebarNav"] li a:hover {
          background: rgba(0, 212, 170, 0.08) !important;
          color: var(--accent) !important;
        }

        [data-testid="stSidebarNav"] li a[aria-current="page"] {
          background: rgba(0, 212, 170, 0.1) !important;
          color: var(--accent) !important;
          font-weight: 600;
        }

        /* ── Brand block ── */
        .fp-sidebar-brand {
          background: linear-gradient(135deg, rgba(0, 212, 170, 0.06), rgba(0, 212, 170, 0.02));
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 1rem;
          margin-bottom: 0.5rem;
        }

        .fp-brand-kicker {
          font-family: 'Sora', sans-serif;
          text-transform: uppercase;
          letter-spacing: 0.2em;
          font-size: 0.6rem;
          font-weight: 600;
          color: var(--accent);
          opacity: 0.8;
        }

        .fp-brand-title {
          font-family: 'Sora', sans-serif;
          font-size: 1.3rem;
          font-weight: 700;
          line-height: 1.1;
          margin: 0.3rem 0 0.25rem;
          color: var(--text-primary);
        }

        .fp-brand-copy {
          font-size: 0.78rem;
          color: var(--text-muted);
          line-height: 1.45;
        }

        /* ── Shared label styles ── */
        .fp-kicker,
        .fp-card-label,
        .fp-chip-label {
          font-family: 'Sora', sans-serif;
          text-transform: uppercase;
          letter-spacing: 0.18em;
          font-size: 0.65rem;
          font-weight: 600;
        }

        .fp-kicker { color: var(--accent); }

        /* ── Page header ── */
        .fp-page-header {
          border-bottom: 1px solid var(--border);
          padding: 0 0 1.2rem 0;
          margin-bottom: 1.5rem;
        }

        .fp-page-title {
          font-family: 'Sora', sans-serif;
          font-size: clamp(1.8rem, 3.5vw, 2.6rem);
          font-weight: 700;
          line-height: 1;
          margin: 0.25rem 0 0 0;
          color: var(--text-primary);
        }

        .fp-page-subtitle {
          max-width: 50rem;
          font-size: 0.95rem;
          color: var(--text-secondary);
          margin: 0.5rem 0 0 0;
          line-height: 1.5;
        }

        .fp-chip-row {
          display: flex;
          flex-wrap: wrap;
          gap: 0.6rem;
          margin-top: 0.85rem;
        }

        .fp-chip {
          background: var(--bg-card);
          border: 1px solid var(--border);
          border-radius: 999px;
          padding: 0.35rem 0.75rem;
          display: inline-flex;
          align-items: center;
          gap: 0.4rem;
        }

        .fp-chip-label { color: var(--text-muted); }

        .fp-chip-value {
          font-weight: 600;
          color: var(--text-primary);
          font-size: 0.85rem;
        }

        /* ── Metric card ── */
        .fp-card {
          background: var(--bg-card);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 1rem 1.1rem;
          min-height: 130px;
          transition: border-color 0.2s;
        }

        .fp-card:hover { border-color: rgba(255, 255, 255, 0.1); }

        .fp-card-label { color: var(--text-muted); }

        .fp-card-value {
          font-family: 'Sora', sans-serif;
          font-size: clamp(1.6rem, 2.4vw, 2.2rem);
          font-weight: 700;
          line-height: 1;
          margin: 0.45rem 0 0.35rem 0;
          color: var(--text-primary);
        }

        .fp-card-copy {
          font-size: 0.82rem;
          color: var(--text-muted);
          line-height: 1.4;
        }

        /* ── Panel ── */
        .fp-panel {
          background: var(--bg-card);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 1rem 1.1rem;
        }

        .fp-panel-title {
          font-family: 'Sora', sans-serif;
          font-size: 1.05rem;
          font-weight: 600;
          margin: 0 0 0.5rem 0;
          color: var(--text-primary);
        }

        .fp-panel-copy {
          font-size: 0.88rem;
          color: var(--text-secondary);
          line-height: 1.6;
        }

        .fp-small {
          font-size: 0.82rem;
          color: var(--text-muted);
        }

        /* ── Bullet list ── */
        .fp-list {
          margin: 0;
          padding-left: 1.1rem;
        }

        .fp-list li {
          margin-bottom: 0.45rem;
          color: var(--text-secondary);
          font-size: 0.88rem;
          line-height: 1.55;
        }

        .fp-list li::marker { color: var(--accent); }

        /* ── Badge ── */
        .fp-badge {
          display: inline-block;
          padding: 0.3rem 0.65rem;
          border-radius: 999px;
          font-family: 'Sora', sans-serif;
          font-size: 0.68rem;
          font-weight: 600;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          color: #fff;
        }

        /* ── Machine row (fleet / planner) ── */
        .fp-machine-row {
          background: var(--bg-card);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 0.9rem 1rem;
          margin-bottom: 0.5rem;
          transition: border-color 0.2s, background 0.2s;
        }

        .fp-machine-row:hover {
          border-color: rgba(0, 212, 170, 0.15);
          background: var(--bg-card-alt);
        }

        .fp-machine-name {
          font-family: 'Sora', sans-serif;
          font-weight: 600;
          font-size: 1rem;
          color: var(--text-primary);
        }

        .fp-machine-meta {
          font-size: 0.8rem;
          color: var(--text-muted);
          margin-top: 0.15rem;
        }

        .fp-rank {
          font-family: 'Sora', sans-serif;
          font-size: 0.6rem;
          font-weight: 700;
          letter-spacing: 0.15em;
          text-transform: uppercase;
          color: var(--accent);
          margin-bottom: 0.2rem;
        }

        /* ── Section titles ── */
        .fp-section-title {
          font-family: 'Sora', sans-serif;
          font-size: 1.15rem;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0 0 0.75rem 0;
        }

        /* ── Streamlit overrides ── */
        .stButton > button {
          border-radius: var(--radius-sm);
          border: 1px solid rgba(0, 212, 170, 0.25);
          background: rgba(0, 212, 170, 0.1);
          color: var(--accent);
          font-weight: 600;
          font-size: 0.82rem;
          padding: 0.45rem 1rem;
          transition: all 0.2s;
        }

        .stButton > button:hover {
          background: rgba(0, 212, 170, 0.18);
          border-color: rgba(0, 212, 170, 0.4);
          color: var(--accent);
        }

        [data-testid="stMetric"] {
          background: var(--bg-card);
          border: 1px solid var(--border);
          border-radius: var(--radius-sm);
          padding: 0.75rem 0.85rem;
        }

        [data-testid="stMetric"] [data-testid="stMetricLabel"] {
          color: var(--text-muted) !important;
        }

        [data-testid="stMetric"] [data-testid="stMetricValue"] {
          color: var(--text-primary) !important;
        }

        [data-testid="stExpander"] {
          border-radius: var(--radius-sm);
          overflow: hidden;
          border: 1px solid var(--border);
          background: var(--bg-card);
        }

        [data-testid="stExpander"] summary {
          color: var(--text-secondary) !important;
        }

        h1, h2, h3, h4, h5, h6 {
          font-family: 'Sora', sans-serif !important;
          color: var(--text-primary) !important;
        }

        h2 { font-size: 1.15rem !important; font-weight: 600 !important; }
        h3 { font-size: 1rem !important; font-weight: 600 !important; }

        p, li, span, div { color: var(--text-secondary); }

        [data-testid="stCaptionContainer"] { color: var(--text-muted) !important; }
        [data-testid="stCaptionContainer"] p { color: var(--text-muted) !important; }

        .stDataFrame { border-radius: var(--radius-sm); overflow: hidden; }

        [data-testid="stFileUploader"] {
          background: var(--bg-card) !important;
          border-radius: var(--radius-sm);
        }

        [data-testid="stFileUploader"] label {
          color: var(--text-secondary) !important;
        }

        /* scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg-primary); }
        ::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.08);
          border-radius: 3px;
        }

        /* toast */
        [data-testid="stToast"] {
          background: var(--bg-elevated) !important;
          border: 1px solid var(--border) !important;
          border-radius: var(--radius-sm) !important;
        }

        /* status indicators */
        .fp-status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          display: inline-block;
          margin-right: 6px;
          position: relative;
          top: -1px;
        }

        .fp-status-dot.critical {
          background: var(--critical);
          box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
        }
        .fp-status-dot.impaired { background: var(--impaired); }
        .fp-status-dot.watchlist { background: var(--watchlist); }
        .fp-status-dot.healthy { background: var(--healthy); }

        @media (max-width: 900px) {
          .block-container { padding: 1rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    st.sidebar.markdown(
        """
        <div class="fp-sidebar-brand">
          <div class="fp-brand-kicker">Predictive maintenance</div>
          <div class="fp-brand-title">FactoryPulse<span style="color:var(--accent);">Lite</span></div>
          <div class="fp-brand-copy">Machine health & remaining life for ASEAN SME operators.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(
    title: str,
    subtitle: str,
    eyebrow: str,
    chips: list[tuple[str, str]] | None = None,
) -> None:
    chip_markup = ""
    if chips:
        chip_markup = "<div class='fp-chip-row'>" + "".join(
            f"<div class='fp-chip'><div class='fp-chip-label'>{escape(label)}</div><div class='fp-chip-value'>{escape(value)}</div></div>"
            for label, value in chips
        ) + "</div>"

    st.markdown(
        f"""
        <section class="fp-page-header">
          <div class="fp-kicker">{escape(eyebrow)}</div>
          <h1 class="fp-page-title">{escape(title)}</h1>
          <p class="fp-page-subtitle">{escape(subtitle)}</p>
          {chip_markup}
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="fp-card">
          <div class="fp-card-label">{escape(label)}</div>
          <div class="fp-card-value">{escape(value)}</div>
          <div class="fp-card-copy">{escape(copy)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_panel(title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="fp-panel">
          <div class="fp-panel-title">{escape(title)}</div>
          <div class="fp-panel-copy">{escape(copy)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_bullet_panel(title: str, items: list[str]) -> None:
    list_markup = "".join(f"<li>{escape(item)}</li>" for item in items)
    st.markdown(
        f"""
        <div class="fp-panel">
          <div class="fp-panel-title">{escape(title)}</div>
          <ul class="fp-list">{list_markup}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def health_badge(health_state: str) -> str:
    colors = {
        "Healthy": "var(--healthy)",
        "Watchlist": "var(--watchlist)",
        "Impaired": "var(--impaired)",
        "Critical": "var(--critical)",
    }
    color = colors.get(health_state, "var(--accent)")
    return f'<span class="fp-badge" style="background:{color};">{escape(health_state)}</span>'


def render_machine_row(rank: int, name: str, meta: str, badge_html: str, rul: str, health: str, cost: str) -> None:
    st.markdown(
        f"""
        <div class="fp-machine-row">
          <div class="fp-rank">#{rank}</div>
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
            <div>
              <div class="fp-machine-name">{escape(name)}</div>
              <div class="fp-machine-meta">{escape(meta)}</div>
            </div>
            <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap;">
              {badge_html}
              <div style="text-align:right;">
                <div class="fp-small">RUL</div>
                <div style="font-family:'Sora',sans-serif;font-weight:600;color:var(--text-primary);font-size:0.95rem;">{escape(rul)}</div>
              </div>
              <div style="text-align:right;">
                <div class="fp-small">Health</div>
                <div style="font-family:'Sora',sans-serif;font-weight:600;color:var(--text-primary);font-size:0.95rem;">{escape(health)}</div>
              </div>
              <div style="text-align:right;">
                <div class="fp-small">Saved</div>
                <div style="font-family:'Sora',sans-serif;font-weight:600;color:var(--accent);font-size:0.95rem;">{escape(cost)}</div>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
