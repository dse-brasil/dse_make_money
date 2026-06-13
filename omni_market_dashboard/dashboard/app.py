import streamlit as st
import pandas as pd
import numpy as np
import datetime
from omni_market_dashboard.workers.cdi_worker import fetch_latest_cdi, calculate_annualized_rate
from omni_market_dashboard.workers.fixed_income_scraper import FixedIncomeScraper
from omni_market_dashboard.core.risk_manager import RiskManager
from omni_market_dashboard.core.rebalancer import PortfolioRebalancer

# 1. Page Configuration
st.set_page_config(
    page_title="Family Office - Dashboard Omni-Market",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom Sleek Dark-Mode CSS (Glassmorphism & Gradients)
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #080B10;
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Gradient styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8, #818CF8, #F43F5E);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #94A3B8;
        margin-bottom: 2rem;
    }
    
    /* Glassmorphic Metrics Card */
    div[data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: transform 0.2s ease-in-out;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        border-color: rgba(56, 189, 248, 0.4);
    }
    
    /* Card headers */
    .card-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 1rem;
        border-bottom: 2px solid rgba(255, 255, 255, 0.05);
        padding-bottom: 0.5rem;
    }
    
    /* Info Box Alert Glassmorphism */
    .alert-card {
        background: rgba(244, 63, 94, 0.1);
        border: 1px solid rgba(244, 63, 94, 0.2);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #FDA4AF;
    }
    .info-card {
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #BAE6FD;
    }
</style>
""", unsafe_allow_html=True)

# 3. Fetch Data dynamically
@st.cache_data(ttl=3600)  # Cache for 1 hour to avoid spamming the Central Bank API
def get_cdi_data():
    record = fetch_latest_cdi()
    if record:
        daily = float(record["valor"])
        annual = calculate_annualized_rate(daily)
        return {"date": record["data"], "daily": daily, "annual": annual}
    return {"date": "N/A", "daily": 0.0, "annual": 10.45} # Fallback

cdi_info = get_cdi_data()

# 4. Sidebar Controls
st.sidebar.markdown("<h2 class='card-title'>Digital Family Office</h2>", unsafe_allow_html=True)
st.sidebar.subheader("Parâmetros do Portfólio")

# Current allocation sliders (for real-time rebalancing math)
alloc_fixed = st.sidebar.number_input("Tesouraria (CDBs) R$", value=180000.0, step=10000.0)
alloc_stocks = st.sidebar.number_input("B3 Ações / Trade R$", value=120000.0, step=10000.0)
alloc_crypto = st.sidebar.number_input("Crypto / Arbitragem R$", value=50000.0, step=5000.0)
alloc_fii = st.sidebar.number_input("Fundos Imobiliários R$", value=100000.0, step=10000.0)

current_allocs = {
    "FIXED_INCOME": alloc_fixed,
    "B3_STOCK": alloc_stocks,
    "CRYPTO": alloc_crypto,
    "FII": alloc_fii
}

total_wealth = sum(current_allocs.values())

st.sidebar.markdown("---")
st.sidebar.subheader("Resultados do Período")
day_trade_profits = st.sidebar.number_input("Lucro Day Trade Acumulado R$", value=28000.0, step=1000.0)

# 5. Main Content Area
st.markdown("<h1 class='main-header'>Dashboard Omni-Market de Investimentos</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Consolidado Patrimonial da Tesouraria e Alta Liquidez (Family Office)</p>", unsafe_allow_html=True)

# Row 1: KPI Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Patrimônio Total Custodiado",
        value=f"R$ {total_wealth:,.2f}",
        delta=f"+ R$ {day_trade_profits:,.2f} (Trade)"
    )

with col2:
    st.metric(
        label="Taxa CDI Anual (SGS BCB)",
        value=f"{cdi_info['annual']:.4f}% p.a.",
        delta=f"{cdi_info['daily']:.6f}% a.d.",
        delta_color="normal"
    )

with col3:
    # Estimate FII Yield (Mocked portfolio yield average)
    avg_fii_yield = 9.85 # % p.a.
    monthly_passive_income = (alloc_fii * (avg_fii_yield / 100.0)) / 12.0
    st.metric(
        label="Renda Passiva Mensal Est.",
        value=f"R$ {monthly_passive_income:,.2f}",
        delta=f"{avg_fii_yield}% p.a. FII Yield"
    )

with col4:
    # High Frequency Share of wallet
    hf_pct = ((alloc_stocks + alloc_crypto) / total_wealth) * 100.0
    st.metric(
        label="Alocação em Risco (Alta Liq.)",
        value=f"{hf_pct:.1f}%",
        delta="Max Recomendado 40%" if hf_pct > 40 else "Nível Seguro",
        delta_color="inverse" if hf_pct > 40 else "normal"
    )

# Row 2: Risk Management & Capital Protection Advice
st.markdown("<h3 class='card-title'>Motor de Gerenciamento de Risco e Salvaguarda</h3>", unsafe_allow_html=True)

rm = RiskManager(current_allocs)
sweep_result = rm.evaluate_treasury_sweep(day_trade_profits)

if sweep_result["sweep_recommended"]:
    st.markdown(f"""
    <div class="alert-card">
        <strong>🚨 ALERTA DE SWEEP DE TESOURARIA:</strong> Recomenda-se resgatar 
        <strong>R$ {sweep_result['sweep_amount']:,.2f}</strong> dos lucros excedentes do Day Trade/Ações 
        e alocar imediatamente em <strong>CDBs de Liquidez Diária</strong>.<br/>
        <em>Razão: {sweep_result['reason']}</em>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="info-card">
        <strong>✓ POLÍTICA DE RISCO ADEQUADA:</strong> {sweep_result['reason']}.
    </div>
    """, unsafe_allow_html=True)

# Row 3: Visual Charts and Broker Shelves ranking
chart_col, shelf_col = st.columns([3, 2])

with chart_col:
    st.markdown("<h3 class='card-title'>Distribuição Histórica & Alocação Atual</h3>", unsafe_allow_html=True)
    
    # Generate mock chart data for portfolio equity over time
    dates = pd.date_range(start="2026-05-01", end="2026-06-13", freq="D")
    base_equity = np.linspace(total_wealth * 0.95, total_wealth, len(dates))
    noise = np.random.normal(0, 5000, len(dates))
    
    df_chart = pd.DataFrame({
        "Data": dates,
        "Patrimônio Consolidado": base_equity + noise,
        "Curva de Acumulação CDBs": np.linspace(alloc_fixed * 0.97, alloc_fixed, len(dates))
    }).set_index("Data")
    
    st.line_chart(df_chart)

with shelf_col:
    st.markdown("<h3 class='card-title'>Melhores Taxas CDB/LCI/LCA (Renda Fixa)</h3>", unsafe_allow_html=True)
    
    scraper = FixedIncomeScraper()
    ranked_assets = scraper.map_broker_shelves()
    
    df_ranked = pd.DataFrame(ranked_assets)
    # Rename headers for user-friendly table
    df_ranked = df_ranked.rename(columns={
        "broker": "Corretora",
        "issuer": "Emissor",
        "type": "Tipo",
        "rate_pct_cdi": "Taxa (% CDI)",
        "days_to_maturity": "Vencimento (Dias)",
        "equivalent_cdi_pct": "Equivalente CDB (% CDI)",
        "fgc_covered": "Garantia FGC"
    })
    
    st.dataframe(df_ranked[["Emissor", "Tipo", "Taxa (% CDI)", "Equivalente CDB (% CDI)", "Corretora", "Garantia FGC"]], use_container_width=True)

# Row 4: Asset Rebalancer Math
st.markdown("<h3 class='card-title'>Plano de Rebalanceamento Estrutural</h3>", unsafe_allow_html=True)
rebalancer = PortfolioRebalancer()
rebal_results = rebalancer.calculate_rebalancing(current_allocs)

if "rebalancing_details" in rebal_results:
    df_rebal = pd.DataFrame(rebal_results["rebalancing_details"]).T
    
    # Style deviations
    df_rebal["current_value"] = df_rebal["current_value"].map("R$ {:,.2f}".format)
    df_rebal["target_value"] = df_rebal["target_value"].map("R$ {:,.2f}".format)
    df_rebal["deviation_value"] = df_rebal["deviation_value"].map("R$ {:,.2f}".format)
    df_rebal["current_percentage"] = df_rebal["current_percentage"].map("{:.2f}%".format)
    df_rebal["target_percentage"] = df_rebal["target_percentage"].map("{:.2f}%".format)
    df_rebal["deviation_percentage"] = df_rebal["deviation_percentage"].map("{:.2f}%".format)
    
    st.dataframe(df_rebal, use_container_width=True)
