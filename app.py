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

/* ── Sidebar metrics cards ── */
.sidebar-metric-card {
    background: #13161e;
    border: 1px solid #1e2538;
    border-radius: 10px;
    padding: 12px;
    margin: 10px 0;
}
.sidebar-metric-card.revenue { border-top: 3px solid #3b82f6; }
.sidebar-metric-card.expenses { border-top: 3px solid #f59e0b; }
.sidebar-metric-card.profit { border-top: 3px solid #10b981; }
.sidebar-metric-title {
    color: #f0f4ff;
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: .8px;
}
.sidebar-metric-head,
.sidebar-metric-row {
    display: grid;
    grid-template-columns: 1.15fr .9fr .9fr .85fr;
    gap: 6px;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
}
.sidebar-metric-head {
    color: #64748b;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: .6px;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e2538;
}
.sidebar-metric-row {
    color: #94a3b8;
    font-size: 10px;
    padding-top: 7px;
}
.sidebar-metric-row.active {
    color: #f0f4ff !important;
    font-weight: 600;
}
.sidebar-metric-model { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sidebar-metric-num { text-align: right; }
.sidebar-metric-best { color: #10b981 !important; font-weight: 700; }

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

        # Все возможные модели — загружаем только те, для которых есть файлы
        MODEL_FILES = {
            'lgbm': 'lgbm_{t}.joblib',
            'xgb':  'xgb_{t}.joblib',
            'cb':   'cb_{t}.joblib',
            'rf':   'rf_{t}.joblib',
        }

        targets = []
        models  = {}
        for t in all_targets:
            loaded = {}
            for key, fname in MODEL_FILES.items():
                path = f"{MODEL_DIR}/{fname.format(t=t)}"
                if os.path.exists(path):
                    loaded[key] = joblib.load(path)

            # Нужна хотя бы одна модель чтобы включить таргет
            if loaded:
                models[t] = loaded
                targets.append(t)

        available_models = list(next(iter(models.values())).keys()) if models else []
        st.sidebar.caption(f"Загружено моделей: {', '.join(available_models).upper()}")

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
            row[f'{t}_std4w']  = float(extended[t].tail(4).std()) if t in extended.columns else 0.0
            row[f'{t}_trend']  = lag(t,1) - lag(t,4)
            row[f'{t}_lag_52w'] = float(extended[t].iloc[-52]) if len(extended)>=52 and t in extended.columns else lag(t,1)
            row[f'restaurant_mean_{t}'] = float(extended[t].mean()) if t in extended.columns else 0.0

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

        X_new = (pd.Series(row)
                 .reindex(feature_cols)
                 .fillna(0.0)
                 .astype(float)
                 .values
                 .reshape(1, -1))

        # ── Предсказания всех доступных моделей ──────────────────────
        step_result = {'week_start': next_week}

        for target in targets:
            sh     = float(shifts[target])
            preds  = {}

            for model_key, model_obj in models[target].items():
                raw  = model_obj.predict(X_new)
                val  = float(np.expm1(raw[0] if hasattr(raw, '__len__') else raw)) - sh
                preds[model_key] = val
                step_result[f'{target}_{model_key}'] = round(val, 2)

            # Ensemble = среднее всех доступных моделей
            p_ens = float(np.mean(list(preds.values())))
            step_result[target] = round(p_ens, 2)

            # Погрешность = std предсказаний моделей
            step_result[f'{target}_std'] = round(
                float(np.std(list(preds.values()))), 2
            )

        if 'profit' not in targets and \
           'revenue' in targets and 'expenses' in targets:
            step_result['profit'] = round(
                step_result['revenue'] - step_result['expenses'], 2
            )
            step_result['profit_std'] = round(
                step_result.get('revenue_std', 0) +
                step_result.get('expenses_std', 0), 2
            )

        # Добавляем прогноз в историю для следующего шага
        nr = extended.iloc[-1].copy()
        nr['week_start'] = next_week
        for target in targets:
            nr[target] = step_result[target]
        nr['total_sold'] = roll('total_sold', 4)
        extended = pd.concat([extended, nr.to_frame().T], ignore_index=True)
        rows.append(step_result)

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


def render_html(html: str):
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)


def kpi_card(label, value, delta="", color="blue"):
    delta_class = "up" if delta.startswith("+") else ("down" if delta.startswith("-") else "")
    delta_html  = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card {color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>"""


def render_metric_row(items):
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        with col:
            st.metric(
                label=item["label"],
                value=item["value"],
                delta=item.get("delta") or None,
            )


def sidebar_metric_card(target, title, metrics_data, model_keys, model_colors, active_model_key):
    t_data = metrics_data.get(target, {})
    rows = [mk for mk in model_keys if mk in t_data]
    if not rows:
        return ""

    best_mae = min((t_data[mk].get('mae', 0) for mk in rows), default=0)
    best_wmape = min((t_data[mk].get('wmape', 0) for mk in rows), default=0)

    card_html = f"""
    <div class="sidebar-metric-card {target}">
        <div class="sidebar-metric-title">{title}</div>
        <div class="sidebar-metric-head">
            <div>Model</div>
            <div class="sidebar-metric-num">MAE</div>
            <div class="sidebar-metric-num">RMSE</div>
            <div class="sidebar-metric-num">WMAPE</div>
        </div>"""

    for mk in rows:
        m = t_data.get(mk, {})
        mae_v = m.get('mae', 0)
        rmse_v = m.get('rmse', 0)
        wmape_v = m.get('wmape', 0)

        row_cls = " active" if mk == active_model_key else ""
        mae_cls = " sidebar-metric-best" if abs(mae_v - best_mae) < 1 else ""
        wmape_cls = " sidebar-metric-best" if abs(wmape_v - best_wmape) < 0.05 else ""
        marker = "▶ " if mk == active_model_key else ""
        color = model_colors.get(mk, '#64748b')

        card_html += f"""
        <div class="sidebar-metric-row{row_cls}">
            <div class="sidebar-metric-model" style="color:{color};">{marker}{mk}</div>
            <div class="sidebar-metric-num{mae_cls}">{mae_v:,.0f}</div>
            <div class="sidebar-metric-num">{rmse_v:,.0f}</div>
            <div class="sidebar-metric-num{wmape_cls}">{wmape_v:.1f}%</div>
        </div>"""

    card_html += """
    </div>"""
    return card_html


# ═══════════════════════════════════════════════════════════════════════
# ГЛАВНАЯ
# ═══════════════════════════════════════════════════════════════════════
def main():
    models, shifts, feature_cols, config, targets, metrics_data, restaurants = load_all()
    weekly = load_weekly()

    all_targets_display = list(set(targets + (['profit'] if 'revenue' in targets and 'expenses' in targets else [])))

    # ── Маппинг названий моделей ──────────────────────────────────────
    MODEL_LABELS = {
        'ensemble': 'Ensemble',
        'lgbm':     'LightGBM',
        'xgb':      'XGBoost',
        'cb':       'CatBoost',
        'rf':       'Random Forest',
    }
    MODEL_COLORS = {
        'ensemble': '#a78bfa',
        'lgbm':     '#3b82f6',
        'xgb':      '#f59e0b',
        'cb':       '#10b981',
        'rf':       '#f43f5e',
    }

    # Определяем доступные модели из загруженных файлов
    loaded_model_keys = list(next(iter(models.values())).keys()) if models else []
    available_options = ['Ensemble'] + [MODEL_LABELS[k] for k in
                         ['lgbm','xgb','cb','rf'] if k in loaded_model_keys]

    # ── SIDEBAR ───────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## 🍽️ P&L Forecast")
        render_html("<hr style='border-color:#1e2538;margin:12px 0'>")

        selected = st.selectbox("Ресторан", options=restaurants, index=0)
        horizon  = st.slider("Горизонт (недели)", 1, 12,
                             value=config.get('forecast_horizon', 6))

        render_html("<hr style='border-color:#1e2538;margin:12px 0'>")
        st.markdown("**Модель прогноза**")
        selected_model_label = st.radio(
            label="",
            options=available_options,
            index=0,
            label_visibility="collapsed"
        )
        # Обратный маппинг: "LightGBM" → "lgbm"
        label_to_key = {v: k for k, v in MODEL_LABELS.items()}
        selected_model_key = label_to_key.get(selected_model_label, 'ensemble')

        # ── Метрики всех моделей ─────────────────────────────────────
        if metrics_data:
            render_html("<hr style='border-color:#1e2538;margin:12px 0'>")
            st.markdown("**Метрики (тест)**")

            all_model_keys = ['lgbm', 'xgb', 'cb', 'rf', 'ensemble']
            metric_cards = "".join(
                sidebar_metric_card(t, title, metrics_data, all_model_keys, MODEL_COLORS, selected_model_key)
                for t, title in [
                    ('revenue', 'Revenue'),
                    ('expenses', 'Expenses'),
                    ('profit', 'Profit'),
                ]
            )
            if metric_cards:
                render_html(metric_cards)

        render_html("<hr style='border-color:#1e2538;margin:12px 0'>")
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
    render_html(f"<div style='color:#475569;font-size:13px;font-family:JetBrains Mono;margin-top:-16px;margin-bottom:24px;'>Последнее обновление: {hist['week_start'].max().strftime('%d.%m.%Y')} · {len(hist)} недель истории</div>")

    # ── KPI СТРОКА ────────────────────────────────────────────────────
    render_html('<div class="section-header">Последние 4 недели</div>')

    d_rev  = pct_delta('revenue',  last4, prev4) if 'revenue'  in last4.columns else ""
    d_prof = pct_delta('profit',   last4, prev4) if 'profit'   in last4.columns else ""

    render_metric_row([
        {"label": "Средний доход / нед.", "value": fmt_money(avg_rev), "delta": d_rev},
        {"label": "Средний расход / нед.", "value": fmt_money(avg_exp)},
        {"label": "Средняя прибыль / нед.", "value": fmt_money(avg_prof), "delta": d_prof},
        {"label": "Маржа", "value": fmt_pct(margin)},
    ])

    # ── ИСТОРИЧЕСКИЕ ГРАФИКИ ──────────────────────────────────────────
    render_html('<div class="section-header">История продаж</div>')

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
    render_html(f'<div class="section-header">Прогноз — {horizon} недель</div>')

    if not run_btn:
        render_html("""
        <div style='background:#13161e;border:1px dashed #1e2538;border-radius:12px;
                    padding:32px;text-align:center;color:#475569;font-size:14px;'>
            ← Нажми <strong style='color:#3b82f6'>▶ Запустить прогноз</strong> в боковой панели
        </div>""")
        return

    with st.spinner("Считаю прогноз..."):
        try:
            fdf = forecast_restaurant(
                selected, horizon, weekly, models,
                shifts, feature_cols, config, targets
            )
        except Exception as e:
            st.error(str(e)); return

    # ── Выбираем колонки выбранной модели ─────────────────────────────
    def get_col(target_name):
        """Возвращает нужную колонку в зависимости от выбранной модели."""
        if selected_model_key == 'ensemble':
            return target_name  # ensemble хранится напрямую
        col = f'{target_name}_{selected_model_key}'
        return col if col in fdf.columns else target_name

    model_color = MODEL_COLORS.get(selected_model_key, '#a78bfa')
    model_label = MODEL_LABELS.get(selected_model_key, 'Ensemble')

    # Заголовок с выбранной моделью
    render_html(
        f"<div style='display:inline-block;background:{model_color}22;"
        f"border:1px solid {model_color};border-radius:8px;"
        f"padding:4px 14px;font-size:12px;font-family:JetBrains Mono;"
        f"color:{model_color};margin-bottom:16px;'>"
        f"▶ {model_label}</div>"
    )

    # ── ИТОГО ─────────────────────────────────────────────────────────
    t_rev  = fdf[get_col('revenue')].sum()  if get_col('revenue')  in fdf.columns else 0
    t_exp  = fdf[get_col('expenses')].sum() if get_col('expenses') in fdf.columns else 0
    t_prof = fdf[get_col('profit')].sum()   if get_col('profit')   in fdf.columns else t_rev - t_exp
    t_marg = t_prof / t_rev * 100 if t_rev > 0 else 0

    render_metric_row([
        {"label": f"Доход за {horizon} нед.", "value": fmt_money(t_rev)},
        {"label": f"Расход за {horizon} нед.", "value": fmt_money(t_exp)},
        {"label": f"Прибыль за {horizon} нед.", "value": fmt_money(t_prof)},
        {"label": "Средняя маржа", "value": fmt_pct(t_marg)},
    ])

    # ── ТАБЛИЦА ───────────────────────────────────────────────────────
    st.markdown(f"**Детальная таблица — {model_label}**")

    rows = []
    for _, r in fdf.iterrows():
        rev  = r.get(get_col('revenue'),  r.get('revenue',  0))
        exp  = r.get(get_col('expenses'), r.get('expenses', 0))
        prof = r.get(get_col('profit'),   r.get('profit', rev - exp))
        marg = prof / rev * 100 if rev > 0 else 0
        row  = {
            'Неделя':  r['week_start'].strftime('%d.%m.%Y'),
            'Доход':   fmt_money(rev),
            'Расход':  fmt_money(exp),
            'Прибыль': fmt_money(prof),
            'Маржа':   fmt_pct(marg),
        }
        # Погрешность только для ensemble
        if selected_model_key == 'ensemble':
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
    st.markdown(f"**История + прогноз ({model_label})**")

    hist_tail = hist.tail(min(16, len(hist)))
    fig2, axes2 = plt.subplots(1, len(plot_cols), figsize=(16, 5))
    if len(plot_cols) == 1: axes2 = [axes2]
    apply_dark_style(fig2, axes2)
    fig2.patch.set_facecolor(DARK_BG)
    fig2.suptitle(f"{selected} — {model_label}",
                  color='#94a3b8', fontsize=12, y=1.02)

    for ax, col in zip(axes2, plot_cols):
        clr      = plot_clrs[col]
        pred_col = get_col(col)
        if pred_col not in fdf.columns and col not in fdf.columns:
            continue

        # История (факт)
        if col in hist_tail.columns:
            ax.plot(hist_tail['week_start'], hist_tail[col],
                    color=clr, lw=2, marker='o', markersize=4,
                    label='Факт', zorder=3)
            ax.fill_between(hist_tail['week_start'], hist_tail[col],
                            alpha=0.1, color=clr)

        # Выбранная модель
        if pred_col in fdf.columns:
            ax.plot(fdf['week_start'], fdf[pred_col],
                    color=model_color, lw=2.5, linestyle='--',
                    marker='s', markersize=5,
                    label=model_label, alpha=0.9, zorder=4)

        # Для ensemble: показываем все модели тонкими линиями
        if selected_model_key == 'ensemble':
            for mk, mk_label in MODEL_LABELS.items():
                if mk == 'ensemble': continue
                mc = f'{col}_{mk}'
                if mc in fdf.columns:
                    ax.plot(fdf['week_start'], fdf[mc],
                            color=MODEL_COLORS.get(mk, '#475569'),
                            lw=0.8, linestyle=':', alpha=0.5,
                            label=mk_label)

        # Погрешность (только ensemble)
        sc = f'{col}_std'
        if selected_model_key == 'ensemble' and sc in fdf.columns:
            ax.fill_between(fdf['week_start'],
                            fdf[col] - fdf[sc], fdf[col] + fdf[sc],
                            alpha=0.1, color=model_color,
                            label='±погрешность')

        ax.axvline(fdf['week_start'].min(), color='#334155',
                   linestyle=':', lw=1.5, zorder=2)
        ax.set_title(plot_names[col], fontsize=11, fontweight='bold',
                     color='#cbd5e1', pad=8)
        ax.legend(fontsize=6.5, framealpha=0,
                  labelcolor='#94a3b8', loc='upper left')
        ax.tick_params(axis='x', rotation=30, labelsize=7)

    plt.tight_layout(pad=2)
    st.pyplot(fig2)
    plt.close()

    # ── СРАВНЕНИЕ ВСЕХ МОДЕЛЕЙ ────────────────────────────────────────
    MODEL_LABELS_LOCAL = {'lgbm': 'LightGBM', 'xgb': 'XGBoost',
                          'cb': 'CatBoost', 'rf': 'Random Forest'}

    with st.expander("🔬 Сравнение всех моделей по неделям"):
        for t in targets:
            model_cols = [f'{t}_{k}' for k in MODEL_LABELS_LOCAL if f'{t}_{k}' in fdf.columns]
            all_cols   = [t] + model_cols
            present    = [c for c in all_cols if c in fdf.columns]
            if not present: continue

            st.markdown(f"**{t.upper()}**")
            cdf = fdf[['week_start'] + present].copy()
            cdf['week_start'] = cdf['week_start'].dt.strftime('%d.%m.%Y')

            col_names = ['Неделя']
            for c in present:
                if c == t:
                    col_names.append('Ensemble')
                else:
                    key = c.replace(f'{t}_', '')
                    col_names.append(MODEL_LABELS_LOCAL.get(key, key.upper()))
            cdf.columns = col_names

            for c in cdf.columns[1:]:
                cdf[c] = cdf[c].apply(fmt_money)
            st.dataframe(cdf, use_container_width=True, hide_index=True)

    # ── ФУТЕР ─────────────────────────────────────────────────────────
    render_html("<hr style='border-color:#1e2538;margin:32px 0 16px'>")
    render_html(
        "<div style='text-align:center;color:#334155;font-size:11px;"
        "font-family:JetBrains Mono;letter-spacing:1px;'>"
        "RESTAURANT P&L FORECAST · ML PROJECT · LGBM + XGB + CATBOOST + RF ENSEMBLE"
        "</div>"
    )


if __name__ == "__main__":
    main()
