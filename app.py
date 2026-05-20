"""
Restaurant P&L Forecast — Dark Theme Streamlit App
Запуск: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ── Конфигурация страницы ──────────────────────────────────────────────
st.set_page_config(
    page_title="Restaurant P&L Forecast",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Тёмная тема: CSS переменные и глобальные стили ────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;700;800&display=swap');

/* ── Глобальный фон ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, .block-container {
    background-color: #0d0f14 !important;
    color: #e2e8f0 !important;
    font-family: 'Syne', sans-serif !important;
}

/* ── Сайдбар ── */
[data-testid="stSidebar"] {
    background-color: #111318 !important;
    border-right: 1px solid #1e2130 !important;
}
[data-testid="stSidebar"] * { color: #c9d1e0 !important; }

/* ── Заголовки ── */
h1 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important;
     font-size: 2rem !important; color: #f0f4ff !important;
     letter-spacing: -0.5px; }
h2, h3, h4 { font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
              color: #cbd5e1 !important; }

/* ── Метрики ── */
div[data-testid="stMetric"] {
    background: #13161e !important;
    border: 1px solid #1e2538 !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
    transition: border-color 0.2s;
}
div[data-testid="stMetric"]:hover { border-color: #3b82f6 !important; }
div[data-testid="stMetricLabel"] > div { color: #94a3b8 !important; font-size: 12px !important;
                                          text-transform: uppercase; letter-spacing: 0.8px; }
div[data-testid="stMetricValue"] > div { color: #f0f4ff !important; font-family: 'JetBrains Mono' !important;
                                          font-size: 1.6rem !important; font-weight: 600 !important; }
div[data-testid="stMetricDelta"] svg { display: none; }
div[data-testid="stMetricDelta"] > div { font-size: 11px !important; font-family: 'JetBrains Mono' !important; }

/* ── Таблица данных ── */
div[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #1e2538 !important;
}
div[data-testid="stDataFrame"] * { font-family: 'JetBrains Mono' !important; font-size: 13px !important; }

/* ── Разделители ── */
hr { border-color: #1e2538 !important; margin: 28px 0 !important; }

/* ── Кнопка ── */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
}
div[data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    box-shadow: 0 0 20px rgba(59,130,246,0.4) !important;
}

/* ── Selectbox / Slider ── */
div[data-testid="stSelectbox"] > div,
div[data-baseweb="select"] > div {
    background-color: #13161e !important;
    border-color: #1e2538 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}
div[data-testid="stSlider"] { padding: 5px 0; }

/* ── Info / Error / Success блоки ── */
div[data-testid="stAlert"] {
    background-color: #13161e !important;
    border-radius: 10px !important;
    border-left-width: 3px !important;
}

/* ── Expander ── */
details { background: #13161e !important; border: 1px solid #1e2538 !important;
          border-radius: 10px !important; padding: 4px 12px !important; }
summary { color: #94a3b8 !important; font-size: 13px !important; }

/* ── Spinner ── */
div[data-testid="stSpinner"] > div { border-top-color: #3b82f6 !important; }

/* ── Полоска сверху страницы ── */
header[data-testid="stHeader"] { background: transparent !important; }

/* ── KPI карточка (кастомный html) ── */
.kpi-row { display: flex; gap: 12px; margin-bottom: 20px; }
.kpi-card {
    flex: 1;
    background: #13161e;
    border: 1px solid #1e2538;
    border-radius: 14px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s, box-shadow 0.25s;
}
.kpi-card:hover { border-color: #3b82f6; box-shadow: 0 0 24px rgba(59,130,246,.15); }
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 100%; height: 3px;
}
.kpi-card.blue::before  { background: linear-gradient(90deg,#3b82f6,#60a5fa); }
.kpi-card.amber::before { background: linear-gradient(90deg,#f59e0b,#fbbf24); }
.kpi-card.green::before { background: linear-gradient(90deg,#10b981,#34d399); }
.kpi-card.rose::before  { background: linear-gradient(90deg,#f43f5e,#fb7185); }
.kpi-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
             color: #64748b; margin-bottom: 10px; font-family: 'JetBrains Mono'; }
.kpi-value { font-size: 1.9rem; font-weight: 700; font-family: 'JetBrains Mono';
             color: #f0f4ff; line-height: 1; }
.kpi-delta { font-size: 11px; margin-top: 8px; font-family: 'JetBrains Mono';
             color: #64748b; }
.kpi-delta.up   { color: #34d399; }
.kpi-delta.down { color: #f87171; }

/* ── Заголовок секции ── */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #475569;
    margin: 28px 0 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-header::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg,#1e2538,transparent);
}
</style>
""", unsafe_allow_html=True)


def render_html(html: str):
    """Render custom HTML across Streamlit versions."""
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# MATPLOTLIB ТЁМНАЯ ТЕМА
# ═══════════════════════════════════════════════════════════════════════
DARK_BG    = '#0d0f14'
DARK_PANEL = '#13161e'
DARK_GRID  = '#1e2538'
TEXT_COLOR = '#94a3b8'
ACCENT     = ['#3b82f6', '#f59e0b', '#10b981', '#f43f5e', '#a78bfa']

def apply_dark_style(fig, axes_list):
    fig.patch.set_facecolor(DARK_BG)
    for ax in (axes_list if hasattr(axes_list, '__iter__') else [axes_list]):
        ax.set_facecolor(DARK_PANEL)
        ax.tick_params(colors=TEXT_COLOR, labelsize=8)
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        ax.title.set_color('#cbd5e1')
        for spine in ax.spines.values():
            spine.set_edgecolor(DARK_GRID)
        ax.grid(True, color=DARK_GRID, linewidth=0.6, alpha=0.8)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt_money(x)))


# ═══════════════════════════════════════════════════════════════════════
# ЗАГРУЗКА
# ═══════════════════════════════════════════════════════════════════════
MODEL_DIR = "models"

@st.cache_resource(show_spinner="Загружаю модели...")
def load_all():
    try:
        shifts       = joblib.load(f"{MODEL_DIR}/target_shifts.joblib")
        feature_cols = joblib.load(f"{MODEL_DIR}/feature_columns.joblib")
        config       = json.load(open(f"{MODEL_DIR}/config.json"))
        metrics      = json.load(open(f"{MODEL_DIR}/metrics.json"))
        restaurants  = json.load(open(f"{MODEL_DIR}/restaurants.json"))
        all_targets  = json.load(open(f"{MODEL_DIR}/targets.json"))

        targets = []
        models  = {}
        for t in all_targets:
            lp = f"{MODEL_DIR}/lgbm_{t}.joblib"
            rp = f"{MODEL_DIR}/rf_{t}.joblib"
            if os.path.exists(lp) and os.path.exists(rp):
                models[t] = {'lgbm': joblib.load(lp), 'rf': joblib.load(rp)}
                targets.append(t)

        return models, shifts, feature_cols, config, targets, metrics, restaurants

    except FileNotFoundError as e:
        st.error(f"Файл не найден: {e}\n\nПоложи файлы из Google Drive в папку `models/`")
        st.stop()


@st.cache_data(show_spinner="Загружаю данные...")
def load_weekly():
    df = pd.read_csv(f"{MODEL_DIR}/weekly_data.csv")
    df['week_start'] = pd.to_datetime(df['week_start'])
    return df


# ═══════════════════════════════════════════════════════════════════════
# ПРОГНОЗ
# ═══════════════════════════════════════════════════════════════════════
def forecast_restaurant(restaurant_id, horizon, weekly,
                        models, shifts, feature_cols, config, targets):
    hist = weekly[weekly['restaurant_id'] == restaurant_id].copy()
    min_weeks = config.get('min_weeks', 8)
    if len(hist) < min_weeks:
        raise ValueError(f"Недостаточно данных: {len(hist)} нед. (нужно ≥ {min_weeks})")

    extended = hist.copy()
    rows = []

    for step in range(1, horizon + 1):
        next_week = extended['week_start'].max() + pd.Timedelta(weeks=1)

        def lag(col, n):
            s = extended[col] if col in extended.columns else pd.Series()
            return float(s.iloc[-n]) if len(s) >= n else (float(s.mean()) if len(s) else 0.0)

        def roll(col, n):
            return float(extended[col].tail(n).mean()) if col in extended.columns else 0.0

        woy, m = next_week.isocalendar()[1], next_week.month

        row = {
            'week_of_year': woy, 'month': m, 'quarter': (m-1)//3+1,
            'week_sin': np.sin(2*np.pi*woy/52), 'week_cos': np.cos(2*np.pi*woy/52),
            'month_sin': np.sin(2*np.pi*m/12),  'month_cos': np.cos(2*np.pi*m/12),
            'has_promotion': 0, 'special_event': 0,
            'n_active_days': roll('n_active_days', 4),
            'n_menu_items':  roll('n_menu_items',  4),
        }

        for t in targets:
            for ln in [1,2,4,8]:  row[f'{t}_lag_{ln}w'] = lag(t, ln)
            for w  in [4,8,12]:   row[f'{t}_roll{w}w']  = roll(t, w)
            row[f'{t}_std4w'] = float(extended[t].tail(4).std()) if t in extended.columns and len(extended[t].tail(4)) > 1 else 0.0
            row[f'{t}_trend']  = lag(t,1) - lag(t,4)
            row[f'{t}_lag_52w'] = float(extended[t].iloc[-52]) if len(extended)>=52 and t in extended.columns else lag(t,1)
            row[f'restaurant_mean_{t}'] = float(extended[t].mean()) if t in extended.columns and len(extended[t]) > 0 else 0.0

        row.update({
            'sold_lag_1w': lag('total_sold',1), 'sold_lag_4w': lag('total_sold',4),
            'sold_roll4w': roll('total_sold',4),
            'avg_price_lag1':  row.get('revenue_lag_1w',0) / (row.get('sold_lag_1w',0)+1),
            'margin_lag1':     row.get('profit_lag_1w',0)  / (row.get('revenue_lag_1w',0)+1),
            'margin_roll4':    row.get('profit_roll4w',0)  / (row.get('revenue_roll4w',0)+1),
            'promo_x_revenue': 0, 'event_x_revenue': 0,
            'days_active_lag1': roll('n_active_days',4),
        })

        for col in feature_cols:
            if col.startswith('restaurant_type_') and col not in row:
                row[col] = int(hist[col].iloc[-1]) if col in hist.columns else 0

        X_new = pd.DataFrame(
            [pd.Series(row).reindex(feature_cols).fillna(0.0).astype(float)],
            columns=feature_cols
        )
        X_values = X_new.values
        sr = {'week_start': next_week}

        for t in targets:
            sh = shifts[t]
            pl = float(np.expm1(models[t]['lgbm'].predict(X_new))[0] - sh)
            pr = float(np.expm1(models[t]['rf'].predict(X_values))[0] - sh)
            pe = (pl + pr) / 2
            sr[t] = round(pe,2); sr[f'{t}_lgbm'] = round(pl,2)
            sr[f'{t}_rf'] = round(pr,2); sr[f'{t}_std'] = round(abs(pl-pr)/2,2)

        if 'profit' not in targets and 'revenue' in targets and 'expenses' in targets:
            sr['profit']     = round(sr['revenue'] - sr['expenses'], 2)
            sr['profit_std'] = round(sr.get('revenue_std',0) + sr.get('expenses_std',0), 2)

        nr = extended.iloc[-1].copy()
        nr['week_start'] = next_week
        for t in targets: nr[t] = sr[t]
        nr['total_sold'] = roll('total_sold', 4)
        extended = pd.concat([extended, nr.to_frame().T], ignore_index=True)
        rows.append(sr)

    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════════════
def fmt_money(val):
    v = float(val)
    if abs(v) >= 1_000_000: return f"${v/1_000_000:.2f}M"
    if abs(v) >= 1_000:     return f"${v/1_000:.1f}K"
    return f"${v:.0f}"

def fmt_pct(val): return f"{float(val):.1f}%"

def kpi_card(label, value, delta="", color="blue"):
    delta_class = "up" if delta.startswith("+") else ("down" if delta.startswith("-") else "")
    delta_html  = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card {color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>"""


# ═══════════════════════════════════════════════════════════════════════
# ГЛАВНАЯ
# ═══════════════════════════════════════════════════════════════════════
def main():
    models, shifts, feature_cols, config, targets, metrics_data, restaurants = load_all()
    weekly = load_weekly()

    all_targets_display = list(set(targets + (['profit'] if 'revenue' in targets and 'expenses' in targets else [])))

    # ── SIDEBAR ───────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## 🍽️ P&L Forecast")
        st.markdown("<hr style='border-color:#1e2538;margin:12px 0'>", unsafe_allow_html=True)

        selected = st.selectbox("Ресторан", options=restaurants, index=0)
        horizon  = st.slider("Горизонт (недели)", 1, 12,
                             value=config.get('forecast_horizon', 6))

        st.markdown("<hr style='border-color:#1e2538;margin:12px 0'>", unsafe_allow_html=True)
        st.markdown("**Модели**")
        st.caption(f"LightGBM + Random Forest → Ensemble")
        st.caption(f"Таргеты: {', '.join(targets)}")

        if metrics_data:
            st.markdown("<hr style='border-color:#1e2538;margin:12px 0'>", unsafe_allow_html=True)
            st.markdown("**Качество (тест)**")
            for t in targets:
                ens = metrics_data.get(t, {}).get('ensemble', {})
                if ens:
                    st.metric(t.upper(),
                              f"WMAPE {ens.get('wmape',0):.1f}%",
                              f"MAE {fmt_money(ens.get('mae',0))}")

        st.markdown("<hr style='border-color:#1e2538;margin:12px 0'>", unsafe_allow_html=True)
        run_btn = st.button("▶  Запустить прогноз", type="primary", use_container_width=True)

    # ── ИСТОРИЯ ───────────────────────────────────────────────────────
    hist = weekly[weekly['restaurant_id'] == selected].sort_values('week_start')
    if hist.empty:
        st.error(f"Нет данных для {selected}")
        return

    last4 = hist.tail(4)
    prev4 = hist.iloc[-8:-4] if len(hist) >= 8 else hist.head(4)

    avg_rev  = last4['revenue'].mean()  if 'revenue'  in last4.columns else 0
    avg_exp  = last4['expenses'].mean() if 'expenses' in last4.columns else 0
    avg_prof = last4['profit'].mean()   if 'profit'   in last4.columns else avg_rev - avg_exp
    margin   = avg_prof / avg_rev * 100 if avg_rev > 0 else 0

    def pct_delta(col, df_a, df_b):
        a, b = df_a[col].mean(), df_b[col].mean()
        return f"{(a-b)/abs(b)*100:+.1f}% vs −4 нед." if b != 0 else ""

    # ── ЗАГОЛОВОК ─────────────────────────────────────────────────────
    st.markdown(f"# {selected}")
    st.markdown(f"<div style='color:#475569;font-size:13px;font-family:JetBrains Mono;margin-top:-16px;margin-bottom:24px;'>Последнее обновление: {hist['week_start'].max().strftime('%d.%m.%Y')} · {len(hist)} недель истории</div>", unsafe_allow_html=True)

    # ── KPI СТРОКА ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Последние 4 недели</div>', unsafe_allow_html=True)

    d_rev  = pct_delta('revenue',  last4, prev4) if 'revenue'  in last4.columns else ""
    d_prof = pct_delta('profit',   last4, prev4) if 'profit'   in last4.columns else ""

    kpi_html = '<div class="kpi-row">'
    kpi_html += kpi_card("Средний доход / нед.",   fmt_money(avg_rev),  d_rev,  "blue")
    kpi_html += kpi_card("Средний расход / нед.",  fmt_money(avg_exp),  "",     "amber")
    kpi_html += kpi_card("Средняя прибыль / нед.", fmt_money(avg_prof), d_prof, "green")
    kpi_html += kpi_card("Маржа",                  fmt_pct(margin),     "",     "rose")
    kpi_html += '</div>'
    render_html(kpi_html)

    # ── ИСТОРИЧЕСКИЕ ГРАФИКИ ──────────────────────────────────────────
    st.markdown('<div class="section-header">История продаж</div>', unsafe_allow_html=True)

    plot_cols  = [c for c in ['revenue','expenses','profit'] if c in hist.columns]
    plot_names = {'revenue':'Доход', 'expenses':'Расход', 'profit':'Прибыль'}
    plot_clrs  = {'revenue': ACCENT[0], 'expenses': ACCENT[1], 'profit': ACCENT[2]}

    fig, axes = plt.subplots(1, len(plot_cols), figsize=(16, 4))
    if len(plot_cols) == 1: axes = [axes]
    apply_dark_style(fig, axes)
    fig.patch.set_facecolor(DARK_BG)

    for ax, col in zip(axes, plot_cols):
        clr = plot_clrs[col]
        ax.plot(hist['week_start'], hist[col], color=clr, lw=2,
                marker='o', markersize=3, zorder=3)
        ax.fill_between(hist['week_start'], hist[col], alpha=0.12, color=clr)
        ax.set_title(plot_names[col], fontsize=12, fontweight='bold', color='#cbd5e1', pad=10)
        ax.tick_params(axis='x', rotation=30, labelsize=7)

    plt.tight_layout(pad=2)
    st.pyplot(fig)
    plt.close()

    # ── ПРОГНОЗ ───────────────────────────────────────────────────────
    st.markdown(f'<div class="section-header">Прогноз — {horizon} недель</div>', unsafe_allow_html=True)

    if not run_btn:
        st.markdown("""
        <div style='background:#13161e;border:1px dashed #1e2538;border-radius:12px;
                    padding:32px;text-align:center;color:#475569;font-size:14px;'>
            ← Нажми <strong style='color:#3b82f6'>▶ Запустить прогноз</strong> в боковой панели
        </div>""", unsafe_allow_html=True)
        return

    with st.spinner("Считаю прогноз..."):
        try:
            fdf = forecast_restaurant(
                selected, horizon, weekly, models,
                shifts, feature_cols, config, targets
            )
        except Exception as e:
            st.error(str(e)); return

    # ── ИТОГО ─────────────────────────────────────────────────────────
    t_rev  = fdf['revenue'].sum()  if 'revenue'  in fdf.columns else 0
    t_exp  = fdf['expenses'].sum() if 'expenses' in fdf.columns else 0
    t_prof = fdf['profit'].sum()   if 'profit'   in fdf.columns else t_rev - t_exp
    t_marg = t_prof / t_rev * 100 if t_rev > 0 else 0

    kpi2  = '<div class="kpi-row">'
    kpi2 += kpi_card(f"Доход за {horizon} нед.",   fmt_money(t_rev),  "", "blue")
    kpi2 += kpi_card(f"Расход за {horizon} нед.",  fmt_money(t_exp),  "", "amber")
    kpi2 += kpi_card(f"Прибыль за {horizon} нед.", fmt_money(t_prof), "", "green")
    kpi2 += kpi_card("Средняя маржа",              fmt_pct(t_marg),   "", "rose")
    kpi2 += '</div>'
    render_html(kpi2)

    # ── ТАБЛИЦА ───────────────────────────────────────────────────────
    st.markdown("**Детальная таблица**")

    rows = []
    for _, r in fdf.iterrows():
        rev  = r.get('revenue',  0)
        exp  = r.get('expenses', 0)
        prof = r.get('profit',   rev - exp)
        marg = prof / rev * 100 if rev > 0 else 0
        row  = {
            'Неделя':  r['week_start'].strftime('%d.%m.%Y'),
            'Доход':   fmt_money(rev),
            'Расход':  fmt_money(exp),
            'Прибыль': fmt_money(prof),
            'Маржа':   fmt_pct(marg),
        }
        for t in targets:
            if f'{t}_std' in r and r[f'{t}_std'] > 0:
                row[f'±{t[:3].capitalize()}'] = fmt_money(r[f'{t}_std'])
        rows.append(row)

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
    )

    # ── ГРАФИК ИСТОРИЯ + ПРОГНОЗ ──────────────────────────────────────
    st.markdown("**История + прогноз**")

    hist_tail = hist.tail(min(16, len(hist)))
    fig2, axes2 = plt.subplots(1, len(plot_cols), figsize=(16, 5))
    if len(plot_cols) == 1: axes2 = [axes2]
    apply_dark_style(fig2, axes2)
    fig2.patch.set_facecolor(DARK_BG)
    fig2.suptitle(f"{selected} — История и прогноз",
                  color='#94a3b8', fontsize=12, y=1.02)

    for ax, col in zip(axes2, plot_cols):
        if col not in fdf.columns: continue
        clr = plot_clrs[col]

        ax.plot(hist_tail['week_start'], hist_tail[col],
                color=clr, lw=2, marker='o', markersize=4, label='Факт', zorder=3)
        ax.fill_between(hist_tail['week_start'], hist_tail[col], alpha=0.1, color=clr)

        ax.plot(fdf['week_start'], fdf[col], color=clr, lw=2,
                linestyle='--', marker='s', markersize=5, label='Прогноз',
                alpha=0.85, zorder=3)

        sc = f'{col}_std'
        if sc in fdf.columns:
            ax.fill_between(fdf['week_start'],
                            fdf[col] - fdf[sc], fdf[col] + fdf[sc],
                            alpha=0.12, color=clr, label='±погрешность')

        ax.axvline(fdf['week_start'].min(), color='#334155',
                   linestyle=':', lw=1.5, zorder=2)

        ax.set_title(plot_names[col], fontsize=11, fontweight='bold',
                     color='#cbd5e1', pad=8)
        ax.legend(fontsize=7, framealpha=0,
                  labelcolor='#94a3b8', loc='upper left')
        ax.tick_params(axis='x', rotation=30, labelsize=7)

    plt.tight_layout(pad=2)
    st.pyplot(fig2)
    plt.close()

    # ── ДЕТАЛИ МОДЕЛЕЙ ────────────────────────────────────────────────
    with st.expander("🔬 LightGBM vs Random Forest vs Ensemble"):
        for t in targets:
            cols_t   = [c for c in [t, f'{t}_lgbm', f'{t}_rf'] if c in fdf.columns]
            if not cols_t: continue
            st.markdown(f"**{t.upper()}**")
            cdf = fdf[['week_start'] + cols_t].copy()
            cdf['week_start'] = cdf['week_start'].dt.strftime('%d.%m.%Y')
            cdf.columns = (
                ['Неделя'] +
                [c.replace(t,'Ensemble').replace(f'{t}_lgbm','LightGBM').replace(f'{t}_rf','RF')
                 for c in cols_t]
            )
            for c in cdf.columns[1:]:
                cdf[c] = cdf[c].apply(fmt_money)
            st.dataframe(cdf, use_container_width=True, hide_index=True)

    # ── ФУТЕР ─────────────────────────────────────────────────────────
    st.markdown("<hr style='border-color:#1e2538;margin:32px 0 16px'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center;color:#334155;font-size:11px;"
        "font-family:JetBrains Mono;letter-spacing:1px;'>"
        "RESTAURANT P&L FORECAST · ML PROJECT · LGBM + RF ENSEMBLE"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
