import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.analysis import (
    get_filtered_data,
    calculate_kpis,
    source_summary,
    renewable_summary,
    yearly_trend,
    country_summary,
    carbon_intensity_summary,
    compare_countries,
    compare_sources,
    generate_environmental_insights
)

# Streamlit Page Configuration
st.set_page_config(
    page_title="Carbon Footprint Analysis of Electricity Generation",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load clean processed dataset with caching
PROCESSED_FILE = os.path.join("data", "processed", "electricity_carbon_clean.csv")

@st.cache_data
def load_data():
    if not os.path.exists(PROCESSED_FILE):
        return None
    df = pd.read_csv(PROCESSED_FILE)
    return df

df = load_data()

# Enhanced Custom CSS styling for visual excellence & high-contrast accessibility
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        line-height: 1.2;
    }
    .sub-header {
        font-size: 1.05rem;
        opacity: 0.85;
        margin-bottom: 1.2rem;
    }
    .disclaimer-box {
        background-color: rgba(59, 130, 246, 0.08);
        border-left: 4px solid #3B82F6;
        padding: 0.8rem 1.2rem;
        border-radius: 6px;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background-color: rgba(148, 163, 184, 0.08);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 10px;
        padding: 1rem 0.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .kpi-title {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        opacity: 0.75;
        margin-bottom: 0.2rem;
    }
    .kpi-num {
        font-size: 1.75rem;
        font-weight: 800;
        line-height: 1.1;
        margin-top: 0.1rem;
    }
    .kpi-unit {
        font-size: 0.85rem;
        font-weight: 600;
        opacity: 0.8;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Main Application Layout
if df is None:
    st.error("⚠️ **Processed dataset not found!**")
    st.info("Please run the data processing pipeline first by executing:\n```bash\npython run_pipeline.py\n```")
    st.stop()

# Application Header
st.markdown('<div class="main-header">🌍 Carbon Footprint Analysis of Electricity Generation Sources</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Interactive analysis of electricity generation, CO₂e emissions, carbon intensity, and renewable energy transitions.</div>', unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer-box">
    ℹ️ <strong>Methodology Note:</strong> This dashboard analyzes power-sector operational emissions and carbon intensity reported by the <strong>Ember Yearly Electricity Dataset</strong>. 
    It focuses on direct electricity-generation emissions and is not a full cradle-to-grave life-cycle assessment (LCA).
</div>
""", unsafe_allow_html=True)

# Sidebar Filters & Control Panel
st.sidebar.header("🔍 Filter Options")

min_year = int(df['year'].min())
max_year = int(df['year'].max())

# Country List Setup
country_types = ['Country', 'Country or economy', 'CountryOrTerritory']
all_countries_list = sorted(df[df['area_type'].isin(country_types)]['area'].dropna().unique().tolist())
country_options = ["All Countries / Regions"] + sorted(df['area'].dropna().unique().tolist())

# Sidebar Reset / Quick Buttons
c_btn1, c_btn2 = st.sidebar.columns(2)
with c_btn1:
    if st.button("🇮🇳 India Focus"):
        st.session_state['country_select'] = "India"
        st.session_state['source_select'] = "All Sources"

with c_btn2:
    if st.button("🔄 Reset Filters"):
        st.session_state['country_select'] = "India"
        st.session_state['year_select'] = (max(min_year, 2000), max_year)
        st.session_state['source_select'] = "All Sources"

default_country_index = country_options.index("India") if "India" in country_options else 0

selected_country = st.sidebar.selectbox(
    "Select Country / Region",
    options=country_options,
    index=default_country_index,
    key='country_select'
)

selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(max(min_year, 2000), max_year),
    key='year_select'
)

available_sources = ["All Sources"] + [
    'Coal', 'Natural Gas', 'Oil', 'Nuclear', 'Hydropower', 'Solar', 'Wind', 'Biomass', 'Other Renewable', 'Other Fossil'
]

selected_source = st.sidebar.selectbox(
    "Select Electricity Source",
    options=available_sources,
    index=0,
    key='source_select'
)

# Filter Dataframe
filtered_df = get_filtered_data(
    df,
    country=selected_country,
    year_range=selected_years,
    sources=selected_source
)

# Compute Dynamic KPIs
kpis = calculate_kpis(filtered_df)

# Top KPI Banner
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">⚡ Electricity Generated</div>
        <div class="kpi-num">{kpis['total_generation_twh']:,.2f}</div>
        <div class="kpi-unit">TWh</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🔥 CO₂e Emissions</div>
        <div class="kpi-num">{kpis['total_emissions_mtco2e']:,.2f}</div>
        <div class="kpi-unit">MtCO₂e</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    intensity_num = f"{kpis['overall_intensity_gco2e_kwh']:,.2f}" if kpis['overall_intensity_gco2e_kwh'] > 0 else "N/A"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🌿 Carbon Intensity</div>
        <div class="kpi-num">{intensity_num}</div>
        <div class="kpi-unit">gCO₂e/kWh</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">☀️ Renewable Share</div>
        <div class="kpi-num">{kpis['renewable_share_pct']:.2f}%</div>
        <div class="kpi-unit">of Total Generation</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Empty Data Warning
if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filter combination. Please adjust your sidebar choices.")
    st.stop()

# Main Navigation Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Source Breakdown",
    "🌿 Carbon Intensity",
    "☀️ Renewable Energy",
    "📈 Historical Trends",
    "⚖️ Comparisons",
    "🗺️ Global Map & Ranking"
])

# ---------------------------------------------------------
# TAB 1: SOURCE BREAKDOWN
# ---------------------------------------------------------
with tab1:
    st.subheader("Electricity Generation, Emissions & Carbon Intensity by Source")
    src_df = source_summary(filtered_df)

    if not src_df.empty:
        c1, c2 = st.columns(2)

        with c1:
            fig_gen = px.bar(
                src_df,
                x='electricity_source_clean',
                y='generation_twh',
                color='resource_category',
                title="Chart 1: Electricity Generation by Source (TWh)",
                labels={'electricity_source_clean': 'Electricity Source', 'generation_twh': 'Generation (TWh)', 'resource_category': 'Category'},
                color_discrete_map={'Renewable': '#10B981', 'Non-renewable': '#EF4444', 'Aggregated / Other': '#6B7280'}
            )
            fig_gen.update_layout(xaxis_tickangle=-45, legend_title_text='Resource Category')
            st.plotly_chart(fig_gen, use_container_width=True)

        with c2:
            fig_emi = px.bar(
                src_df,
                x='electricity_source_clean',
                y='emissions_mtco2e',
                color='resource_category',
                title="Chart 2: CO₂e Emissions by Source (MtCO₂e)",
                labels={'electricity_source_clean': 'Electricity Source', 'emissions_mtco2e': 'Emissions (MtCO₂e)', 'resource_category': 'Category'},
                color_discrete_map={'Renewable': '#10B981', 'Non-renewable': '#EF4444', 'Aggregated / Other': '#6B7280'}
            )
            fig_emi.update_layout(xaxis_tickangle=-45, legend_title_text='Resource Category')
            st.plotly_chart(fig_emi, use_container_width=True)

        # Chart 3: Carbon Intensity by Source
        valid_src_int = src_df[src_df['emissions_intensity_gco2e_kwh'].notna() & (src_df['generation_twh'] > 0)].sort_values('emissions_intensity_gco2e_kwh', ascending=False)
        if not valid_src_int.empty:
            fig_int_src = px.bar(
                valid_src_int,
                x='electricity_source_clean',
                y='emissions_intensity_gco2e_kwh',
                color='resource_category',
                title="Chart 3: Weighted Carbon Intensity by Source (gCO₂e/kWh)",
                labels={'electricity_source_clean': 'Electricity Source', 'emissions_intensity_gco2e_kwh': 'Carbon Intensity (gCO₂e/kWh)', 'resource_category': 'Category'},
                color_discrete_map={'Renewable': '#10B981', 'Non-renewable': '#EF4444', 'Aggregated / Other': '#6B7280'}
            )
            fig_int_src.update_layout(xaxis_tickangle=-45, legend_title_text='Resource Category')
            st.plotly_chart(fig_int_src, use_container_width=True)

        st.markdown("### 💡 Analytical Takeaways")
        top_gen_src = src_df.sort_values('generation_twh', ascending=False).iloc[0]
        top_emi_src = src_df.sort_values('emissions_mtco2e', ascending=False).iloc[0]

        st.info(
            f"• **Dominant Electricity Technology:** **{top_gen_src['electricity_source_clean']}** generates the largest proportion of power ({top_gen_src['generation_twh']:.2f} TWh).\n"
            f"• **Largest Carbon Emitter:** **{top_emi_src['electricity_source_clean']}** accounts for the highest operational greenhouse gas output ({top_emi_src['emissions_mtco2e']:.2f} MtCO₂e)."
        )

# ---------------------------------------------------------
# TAB 2: CARBON INTENSITY
# ---------------------------------------------------------
with tab2:
    st.subheader("Carbon Intensity Analysis (gCO₂e/kWh)")
    st.write(
        "Carbon intensity represents reported CO₂e emissions per unit of electricity generated. "
        "Lower carbon intensity indicates a cleaner, decarbonized power grid."
    )

    intensity_df = carbon_intensity_summary(filtered_df)
    valid_int = intensity_df[intensity_df['emissions_intensity_gco2e_kwh'].notna() & (intensity_df['generation_twh'] > 0)]

    if not valid_int.empty:
        fig_int = px.bar(
            valid_int,
            x='emissions_intensity_gco2e_kwh',
            y='electricity_source_clean',
            orientation='h',
            color='resource_category',
            title="Carbon Intensity by Electricity Source (gCO₂e/kWh)",
            labels={'emissions_intensity_gco2e_kwh': 'Carbon Intensity (gCO₂e/kWh)', 'electricity_source_clean': 'Source'},
            color_discrete_map={'Renewable': '#10B981', 'Non-renewable': '#EF4444', 'Aggregated / Other': '#6B7280'}
        )
        fig_int.update_layout(yaxis={'categoryorder': 'total ascending'}, legend_title_text='Resource Category')
        st.plotly_chart(fig_int, use_container_width=True)

        st.markdown("### 📋 Carbon Intensity Data Table")
        display_tbl = valid_int[['electricity_source_clean', 'resource_category', 'generation_twh', 'emissions_mtco2e', 'emissions_intensity_gco2e_kwh']].copy()
        display_tbl.columns = ['Electricity Source', 'Resource Classification', 'Generation (TWh)', 'Emissions (MtCO₂e)', 'Carbon Intensity (gCO₂e/kWh)']
        st.dataframe(display_tbl.style.format({
            'Generation (TWh)': '{:,.2f}',
            'Emissions (MtCO₂e)': '{:,.2f}',
            'Carbon Intensity (gCO₂e/kWh)': '{:,.2f}'
        }), use_container_width=True)

# ---------------------------------------------------------
# TAB 3: RENEWABLE ENERGY
# ---------------------------------------------------------
with tab3:
    st.subheader("Renewable vs. Non-Renewable Generation Breakdown")
    ren_df = renewable_summary(filtered_df)

    if not ren_df.empty:
        c1, c2 = st.columns(2)

        with c1:
            fig_pie = px.pie(
                ren_df,
                values='generation_twh',
                names='resource_category',
                title="Electricity Generation Share by Resource Category",
                color='resource_category',
                color_discrete_map={'Renewable': '#10B981', 'Non-renewable': '#EF4444', 'Aggregated / Other': '#6B7280'},
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            ren_sources = filtered_df[filtered_df['is_renewable'] == True]
            if not ren_sources.empty:
                ren_trend = ren_sources.groupby(['year', 'electricity_source_clean'], as_index=False)['generation_twh'].sum()
                fig_ren_trend = px.line(
                    ren_trend,
                    x='year',
                    y='generation_twh',
                    color='electricity_source_clean',
                    title="Renewable Electricity Generation Over Time (TWh)",
                    labels={'year': 'Year', 'generation_twh': 'Generation (TWh)', 'electricity_source_clean': 'Source'}
                )
                st.plotly_chart(fig_ren_trend, use_container_width=True)

        st.info(
            f"ℹ️ **Classification Taxonomy:** For resource management analysis, **Nuclear** is classified under Non-renewable due to fissile material resource constraints, "
            f"while **Hydropower, Solar, Wind, Biomass, and Other Renewables** constitute the Renewable category."
        )

# ---------------------------------------------------------
# TAB 4: HISTORICAL TRENDS
# ---------------------------------------------------------
with tab4:
    st.subheader("Historical Trends (Generation, Emissions & Carbon Intensity)")
    trend_df = yearly_trend(filtered_df)

    if not trend_df.empty:
        c1, c2 = st.columns(2)

        with c1:
            fig_t_gen = px.line(
                trend_df,
                x='year',
                y='generation_twh',
                title="Total Electricity Generation Over Time (TWh)",
                markers=True,
                line_shape='linear'
            )
            st.plotly_chart(fig_t_gen, use_container_width=True)

        with c2:
            fig_t_emi = px.line(
                trend_df,
                x='year',
                y='emissions_mtco2e',
                title="Total CO₂e Emissions Over Time (MtCO₂e)",
                markers=True,
                color_discrete_sequence=['#EF4444']
            )
            st.plotly_chart(fig_t_emi, use_container_width=True)

        valid_t_int = trend_df[trend_df['carbon_intensity_gco2e_kwh'].notna()]
        if not valid_t_int.empty:
            fig_t_int = px.line(
                valid_t_int,
                x='year',
                y='carbon_intensity_gco2e_kwh',
                title="Weighted Grid Carbon Intensity Over Time (gCO₂e/kWh)",
                markers=True,
                color_discrete_sequence=['#8B5CF6']
            )
            st.plotly_chart(fig_t_int, use_container_width=True)

# ---------------------------------------------------------
# TAB 5: COMPARISONS
# ---------------------------------------------------------
with tab5:
    st.subheader("Side-by-Side Comparative Analysis")

    sub_t1, sub_t2 = st.tabs(["🌎 Country vs. Country", "⚡ Source vs. Source"])

    with sub_t1:
        st.write("Compare the electricity generation profile and carbon intensity of two countries.")
        
        ca1, ca2 = st.columns(2)
        with ca1:
            idx_a = all_countries_list.index("India") if "India" in all_countries_list else 0
            c_a = st.selectbox("Select Country A", options=all_countries_list, index=idx_a, key='country_a')
        with ca2:
            idx_b = all_countries_list.index("United States") if "United States" in all_countries_list else min(1, len(all_countries_list)-1)
            c_b = st.selectbox("Select Country B", options=all_countries_list, index=idx_b, key='country_b')

        if c_a and c_b:
            comp_df = compare_countries(df, c_a, c_b)
            st.dataframe(comp_df.style.format({
                'total_generation_twh': '{:,.2f}',
                'total_emissions_mtco2e': '{:,.2f}',
                'overall_intensity_gco2e_kwh': '{:,.2f}',
                'renewable_share_pct': '{:.2f}%',
                'clean_share_pct': '{:.2f}%'
            }), use_container_width=True)

            fig_comp = px.bar(
                comp_df,
                x='Country',
                y=['total_generation_twh', 'total_emissions_mtco2e'],
                barmode='group',
                title=f"Comparative Output: {c_a} vs. {c_b}"
            )
            st.plotly_chart(fig_comp, use_container_width=True)

    with sub_t2:
        st.write("Compare two electricity generation technologies side-by-side.")
        indiv_sources = ['Coal', 'Natural Gas', 'Oil', 'Nuclear', 'Hydropower', 'Solar', 'Wind', 'Biomass']
        
        sa1, sa2 = st.columns(2)
        with sa1:
            s_a = st.selectbox("Select Source A", options=indiv_sources, index=0, key='source_a')
        with sa2:
            s_b = st.selectbox("Select Source B", options=indiv_sources, index=5, key='source_b')

        if s_a and s_b:
            comp_src = compare_sources(df, s_a, s_b)
            st.dataframe(comp_src.style.format({
                'total_generation_twh': '{:,.2f}',
                'total_emissions_mtco2e': '{:,.2f}',
                'overall_intensity_gco2e_kwh': '{:,.2f}',
                'renewable_share_pct': '{:.2f}%'
            }), use_container_width=True)

# ---------------------------------------------------------
# TAB 6: GLOBAL MAP & RANKING
# ---------------------------------------------------------
with tab6:
    st.subheader("Global Electricity Emissions & Intensity Map")

    recent_year = int(filtered_df['year'].max())
    map_df = df[(df['year'] == recent_year) & (df['area_type'].isin(country_types)) & (df['is_individual_source'] == True)]

    if not map_df.empty:
        country_geo = map_df.groupby(['area', 'iso_code'], as_index=False).agg({
            'generation_twh': 'sum',
            'emissions_mtco2e': 'sum'
        })
        country_geo['intensity_gco2e_kwh'] = country_geo.apply(
            lambda r: (r['emissions_mtco2e'] * 1000.0 / r['generation_twh']) if r['generation_twh'] > 0 else np.nan,
            axis=1
        )

        fig_map = px.choropleth(
            country_geo,
            locations='iso_code',
            color='intensity_gco2e_kwh',
            hover_name='area',
            color_continuous_scale='Reds',
            title=f"Global Grid Carbon Intensity by Country ({recent_year}) [gCO₂e/kWh]",
            labels={'intensity_gco2e_kwh': 'Carbon Intensity (gCO₂e/kWh)'}
        )
        st.plotly_chart(fig_map, use_container_width=True)

        st.markdown(f"### 🏆 Top 10 CO₂ Emission Power Grids ({recent_year})")
        top_emitters = country_geo.sort_values('emissions_mtco2e', ascending=False).head(10)
        st.dataframe(top_emitters[['area', 'generation_twh', 'emissions_mtco2e', 'intensity_gco2e_kwh']].style.format({
            'generation_twh': '{:,.2f}',
            'emissions_mtco2e': '{:,.2f}',
            'intensity_gco2e_kwh': '{:,.2f}'
        }), use_container_width=True)

# ---------------------------------------------------------
# ENVIRONMENTAL INSIGHTS SECTION
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🌱 Automated Environmental Insights")
insights = generate_environmental_insights(filtered_df)
for ins in insights:
    st.markdown(f"- {ins}")

# ---------------------------------------------------------
# FILTERED DATA TABLE & CSV DOWNLOAD
# ---------------------------------------------------------
with st.expander("📥 View Filtered Dataset & Download CSV"):
    st.dataframe(filtered_df, use_container_width=True)
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data CSV",
        data=csv_data,
        file_name="filtered_electricity_carbon_data.csv",
        mime="text/csv"
    )

# ---------------------------------------------------------
# METHODOLOGY & LIMITATIONS FOOTER
# ---------------------------------------------------------
st.markdown("---")
with st.expander("📚 Data Source, Methodology & Academic Limitations"):
    st.markdown("""
    ### 📊 Data Source
    * **Dataset:** Ember Yearly Electricity Data
    * **Provider:** Ember (Energy Think Tank)
    * **Official Dataset Page:** [https://ember-energy.org/data/yearly-electricity-data/](https://ember-energy.org/data/yearly-electricity-data/)
    
    ### ⚙️ Analytical Methodology
    1. **Data Ingestion:** Raw CSV parsed with normalized column mapping.
    2. **Source Classification:** Electricity technologies categorized into Renewable vs Non-renewable (Nuclear treated as non-renewable due to fissile material constraints).
    3. **Weighted Carbon Intensity Formula:**
       $$\\text{Carbon Intensity (gCO}_2\\text{e/kWh)} = \\frac{\\text{Total CO}_2\\text{e Emissions (MtCO}_2\\text{e}) \\times 1000}{\\text{Total Generation (TWh)}}$$
    
    ### ⚠️ Limitations & Scoping
    * **Operational Scope:** This project evaluates power-sector direct generation emissions reported by Ember. It does not calculate cradle-to-grave life-cycle assessment (LCA) embodied carbon.
    * **Missing Data:** Missing data points are preserved as nulls rather than assumed as zero to avoid distorting grid intensity metrics.
    """)
