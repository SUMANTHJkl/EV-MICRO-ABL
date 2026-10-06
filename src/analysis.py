"""
Analytical logic module for Carbon Footprint Analysis of Electricity Generation Sources.
Contains reusable data processing functions operating on DataFrames.
"""

import pandas as pd
import numpy as np

def get_filtered_data(df, country="All Countries / Regions", year_range=None, sources=None):
    """
    Filters the clean DataFrame based on user selections.
    """
    filtered = df.copy()

    # Filter Country / Area
    if country and country != "All Countries / Regions":
        filtered = filtered[filtered['area'] == country]

    # Filter Year Range
    if year_range and len(year_range) == 2:
        start_yr, end_yr = year_range
        filtered = filtered[(filtered['year'] >= start_yr) & (filtered['year'] <= end_yr)]

    # Filter Sources
    if sources:
        if isinstance(sources, str) and sources != "All Sources":
            filtered = filtered[filtered['electricity_source_clean'] == sources]
        elif isinstance(sources, list) and "All Sources" not in sources:
            filtered = filtered[filtered['electricity_source_clean'].isin(sources)]

    return filtered

def calculate_kpis(df):
    """
    Calculates dynamic KPI metrics from filtered DataFrame:
    - Total Generation (TWh)
    - Total CO2e Emissions (MtCO2e)
    - Overall Carbon Intensity (gCO2e/kWh)
    - Renewable Share (%)
    """
    if df.empty:
        return {
            'total_generation_twh': 0.0,
            'total_emissions_mtco2e': 0.0,
            'overall_intensity_gco2e_kwh': 0.0,
            'renewable_share_pct': 0.0,
            'clean_share_pct': 0.0
        }

    # Filter to individual sources to avoid double-counting aggregates
    indiv_df = df[df['is_individual_source'] == True] if 'is_individual_source' in df.columns else df

    total_gen = indiv_df['generation_twh'].sum(skipna=True)
    total_emissions = indiv_df['emissions_mtco2e'].sum(skipna=True)

    # Weighted Carbon Intensity = (Total MtCO2e * 1000) / Total TWh
    if total_gen > 0 and pd.notna(total_emissions):
        overall_intensity = (total_emissions * 1000.0) / total_gen
    else:
        overall_intensity = np.nan

    # Renewable Share
    ren_gen = indiv_df[indiv_df['is_renewable'] == True]['generation_twh'].sum(skipna=True)
    ren_share = (ren_gen / total_gen * 100.0) if total_gen > 0 else 0.0

    # Clean Share (Renewable + Nuclear)
    clean_gen = indiv_df[indiv_df['electricity_source_clean'].isin(['Hydropower', 'Solar', 'Wind', 'Biomass', 'Other Renewable', 'Nuclear'])]['generation_twh'].sum(skipna=True)
    clean_share = (clean_gen / total_gen * 100.0) if total_gen > 0 else 0.0

    return {
        'total_generation_twh': round(total_gen, 2),
        'total_emissions_mtco2e': round(total_emissions, 2),
        'overall_intensity_gco2e_kwh': round(overall_intensity, 2) if pd.notna(overall_intensity) else 0.0,
        'renewable_share_pct': round(ren_share, 2),
        'clean_share_pct': round(clean_share, 2)
    }

def source_summary(df):
    """
    Aggregates electricity generation, emissions, and carbon intensity by source.
    """
    indiv_df = df[df['is_individual_source'] == True] if 'is_individual_source' in df.columns else df
    if indiv_df.empty:
        return pd.DataFrame(columns=['electricity_source_clean', 'generation_twh', 'emissions_mtco2e', 'emissions_intensity_gco2e_kwh', 'resource_category'])

    summary = indiv_df.groupby(['electricity_source_clean', 'resource_category'], as_index=False).agg({
        'generation_twh': 'sum',
        'emissions_mtco2e': 'sum'
    })

    # Compute weighted intensity for each source
    summary['emissions_intensity_gco2e_kwh'] = summary.apply(
        lambda r: (r['emissions_mtco2e'] * 1000.0 / r['generation_twh']) if r['generation_twh'] > 0 else np.nan,
        axis=1
    )

    summary = summary.sort_values(by='generation_twh', ascending=False)
    return summary

def renewable_summary(df):
    """
    Calculates Renewable vs Non-renewable breakdown.
    """
    indiv_df = df[df['is_individual_source'] == True] if 'is_individual_source' in df.columns else df
    if indiv_df.empty:
        return pd.DataFrame(columns=['resource_category', 'generation_twh', 'emissions_mtco2e', 'share_pct'])

    summary = indiv_df.groupby('resource_category', as_index=False).agg({
        'generation_twh': 'sum',
        'emissions_mtco2e': 'sum'
    })

    total_gen = summary['generation_twh'].sum()
    summary['share_pct'] = (summary['generation_twh'] / total_gen * 100.0) if total_gen > 0 else 0.0
    return summary

def yearly_trend(df):
    """
    Aggregates metrics by year.
    """
    indiv_df = df[df['is_individual_source'] == True] if 'is_individual_source' in df.columns else df
    if indiv_df.empty:
        return pd.DataFrame(columns=['year', 'generation_twh', 'emissions_mtco2e', 'carbon_intensity_gco2e_kwh'])

    trend = indiv_df.groupby('year', as_index=False).agg({
        'generation_twh': 'sum',
        'emissions_mtco2e': 'sum'
    })

    trend['carbon_intensity_gco2e_kwh'] = trend.apply(
        lambda r: (r['emissions_mtco2e'] * 1000.0 / r['generation_twh']) if r['generation_twh'] > 0 else np.nan,
        axis=1
    )
    trend = trend.sort_values('year')
    return trend

def country_summary(df):
    """
    Aggregates data by country for rankings.
    """
    country_types = ['Country', 'Country or economy', 'CountryOrTerritory']
    country_df = df[(df['area_type'].isin(country_types)) & (df['is_individual_source'] == True)]
    if country_df.empty:
        return pd.DataFrame()

    summary = country_df.groupby('area', as_index=False).agg({
        'generation_twh': 'sum',
        'emissions_mtco2e': 'sum'
    })

    summary['carbon_intensity_gco2e_kwh'] = summary.apply(
        lambda r: (r['emissions_mtco2e'] * 1000.0 / r['generation_twh']) if r['generation_twh'] > 0 else np.nan,
        axis=1
    )
    return summary.sort_values('emissions_mtco2e', ascending=False)

def carbon_intensity_summary(df):
    """
    Extracts and ranks individual electricity sources by reported carbon intensity.
    """
    summary = source_summary(df)
    return summary.sort_values('emissions_intensity_gco2e_kwh', ascending=True)

def compare_countries(df, country_a, country_b):
    """
    Compares two countries across core metrics.
    """
    df_a = get_filtered_data(df, country=country_a)
    df_b = get_filtered_data(df, country=country_b)

    kpi_a = calculate_kpis(df_a)
    kpi_b = calculate_kpis(df_b)

    res_a = {'Country': country_a, **kpi_a}
    res_b = {'Country': country_b, **kpi_b}

    return pd.DataFrame([res_a, res_b])

def compare_sources(df, source_a, source_b):
    """
    Compares two individual electricity sources.
    """
    df_a = get_filtered_data(df, sources=source_a)
    df_b = get_filtered_data(df, sources=source_b)

    kpi_a = calculate_kpis(df_a)
    kpi_b = calculate_kpis(df_b)

    res_a = {'Source': source_a, **kpi_a}
    res_b = {'Source': source_b, **kpi_b}

    return pd.DataFrame([res_a, res_b])

def generate_environmental_insights(df):
    """
    Generates programmatic analytical insights and dynamic observations.
    """
    insights = []
    indiv_df = df[df['is_individual_source'] == True] if 'is_individual_source' in df.columns else df

    if indiv_df.empty:
        return ["No data available for the selected filters to generate insights."]

    src_df = source_summary(df)
    kpis = calculate_kpis(df)

    if not src_df.empty:
        # Highest emission source
        top_emitter = src_df.sort_values('emissions_mtco2e', ascending=False).iloc[0]
        if top_emitter['emissions_mtco2e'] > 0:
            insights.append(
                f"🔥 **Highest Emission Source:** **{top_emitter['electricity_source_clean']}** contributed the largest share of CO₂e emissions, total carbon output: **{top_emitter['emissions_mtco2e']:.2f} MtCO₂e**."
            )

        # Top generation source
        top_gen = src_df.sort_values('generation_twh', ascending=False).iloc[0]
        insights.append(
            f"⚡ **Top Generation Technology:** **{top_gen['electricity_source_clean']}** is the leading electricity generation source, producing **{top_gen['generation_twh']:.2f} TWh**."
        )

        # Lowest carbon intensity source
        clean_df = src_df[src_df['emissions_intensity_gco2e_kwh'].notna() & (src_df['generation_twh'] > 0)].sort_values('emissions_intensity_gco2e_kwh', ascending=True)
        if not clean_df.empty:
            cleanest = clean_df.iloc[0]
            insights.append(
                f"🌱 **Cleanest Power Generation:** **{cleanest['electricity_source_clean']}** has the lowest carbon intensity at **{cleanest['emissions_intensity_gco2e_kwh']:.2f} gCO₂e/kWh**."
            )

    # Renewable vs Clean share
    insights.append(
        f"📊 **Grid Cleanliness Metrics:** Renewable energy accounts for **{kpis['renewable_share_pct']:.2f}%** of total generation, while clean energy (including Nuclear) represents **{kpis['clean_share_pct']:.2f}%**."
    )

    # Overall intensity status
    intensity_val = kpis['overall_intensity_gco2e_kwh']
    if intensity_val > 500:
        status = "high carbon intensity (fossil fuel dominant)"
    elif intensity_val > 250:
        status = "moderate carbon intensity (transitioning grid)"
    else:
        status = "low carbon intensity (decarbonized grid)"
        
    insights.append(
        f"🌍 **Overall Grid Assessment:** The weighted grid carbon intensity is **{intensity_val:.2f} gCO₂e/kWh**, indicating a **{status}**."
    )

    return insights
