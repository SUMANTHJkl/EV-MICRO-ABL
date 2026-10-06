import os
import urllib.request
import pandas as pd
import numpy as np

EMBER_URL = "https://files.ember-energy.org/public-downloads/generation/outputs/release_generation_yearly_global.csv"
RAW_DATA_PATH = os.path.join("data", "raw", "ember_yearly_global.csv")
PROCESSED_DATA_PATH = os.path.join("data", "processed", "electricity_carbon_clean.csv")

# Standardized Mapping for Electricity Sources
SOURCE_MAP = {
    'Coal': 'Coal',
    'Gas': 'Natural Gas',
    'Oil': 'Oil',
    'Other fossil': 'Other Fossil',
    'Nuclear': 'Nuclear',
    'Hydro': 'Hydropower',
    'Solar': 'Solar',
    'Wind': 'Wind',
    'Bioenergy': 'Biomass',
    'Other renewables': 'Other Renewable',
    # Aggregated categories
    'Clean': 'Clean (Aggregate)',
    'Fossil': 'Fossil (Aggregate)',
    'Renewables': 'Renewables (Aggregate)',
    'Total generation': 'Total Generation',
    'Wind and solar': 'Wind & Solar (Aggregate)',
    'Hydro, bioenergy and other renewables': 'Other Renewables (Aggregate)',
    'Demand': 'Demand',
    'Net imports': 'Net Imports'
}

# Individual specific sources (excluding aggregated rows)
INDIVIDUAL_SOURCES = [
    'Coal', 'Natural Gas', 'Oil', 'Other Fossil',
    'Nuclear', 'Hydropower', 'Solar', 'Wind', 'Biomass', 'Other Renewable'
]

# Classification mapping (Nuclear is Non-renewable due to resource constraints)
RENEWABLE_MAP = {
    'Hydropower': True,
    'Solar': True,
    'Wind': True,
    'Biomass': True,
    'Other Renewable': True,
    'Coal': False,
    'Natural Gas': False,
    'Oil': False,
    'Nuclear': False,
    'Other Fossil': False
}

def download_dataset(url=EMBER_URL, save_path=RAW_DATA_PATH):
    """
    Downloads the Ember Yearly Electricity Data CSV if not already available locally.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
        print(f"[INFO] Local raw dataset found at '{save_path}'. Skipping download.")
        return save_path

    print(f"[INFO] Downloading dataset from '{url}'...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(save_path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"[SUCCESS] Downloaded raw dataset to '{save_path}'.")
    except Exception as e:
        print(f"[ERROR] Failed to download dataset: {e}")
        if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
            print("[INFO] Falling back to existing local copy.")
            return save_path
        raise e
    return save_path

def load_raw_data(file_path=RAW_DATA_PATH):
    """
    Loads raw CSV into DataFrame.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Raw data file not found at {file_path}. Run download_dataset() first.")
    df = pd.read_csv(file_path, low_memory=False)
    return df

def normalize_columns(df):
    """
    Standardizes column names into lowercase pythonic names.
    """
    column_mapping = {
        'Area': 'area',
        'ISO 3 code': 'iso_code',
        'Year': 'year',
        'Area type': 'area_type',
        'Electricity source': 'electricity_source',
        'Is aggregated source': 'is_aggregated_source',
        'Generation (TWh)': 'generation_twh',
        'Generation YoY change (TWh)': 'generation_yoy_change_twh',
        'Generation YoY change (%)': 'generation_yoy_change_pct',
        'Share of generation (%)': 'share_of_generation_pct',
        'Capacity (GW)': 'capacity_gw',
        'Emissions (MtCO2e)': 'emissions_mtco2e',
        'Emissions YoY change (MtCO2e)': 'emissions_yoy_change_mtco2e',
        'Emissions YoY change (%)': 'emissions_yoy_change_pct',
        'Share of emissions (%)': 'share_of_emissions_pct',
        'Emissions intensity (gCO2e/kWh)': 'emissions_intensity_gco2e_kwh',
        'Continent': 'continent',
        'Ember region': 'ember_region',
        'EU member': 'is_eu_member',
        'OECD member': 'is_oecd_member',
        'G20 member': 'is_g20_member',
        'G7 member': 'is_g7_member',
        'ASEAN member': 'is_asean_member'
    }
    df = df.rename(columns=column_mapping)
    return df

def standardize_sources(df):
    """
    Applies source standardization map to source names.
    """
    if 'electricity_source' in df.columns:
        df['electricity_source_clean'] = df['electricity_source'].map(SOURCE_MAP).fillna(df['electricity_source'])
    return df

def classify_renewable_status(df):
    """
    Adds renewable classification and category columns.
    Note: Nuclear is classified as Non-renewable.
    """
    df['is_renewable'] = df['electricity_source_clean'].map(RENEWABLE_MAP)
    df['resource_category'] = df['is_renewable'].map({
        True: 'Renewable',
        False: 'Non-renewable'
    }).fillna('Aggregated / Other')
    return df

def clean_data(df):
    """
    Performs data cleaning, metric validation, derived calculations, and deduplication.
    """
    df = df.copy()

    # Ensure year is integer
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)

    # Ensure numeric columns
    numeric_cols = ['generation_twh', 'emissions_mtco2e', 'emissions_intensity_gco2e_kwh', 'share_of_generation_pct']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Remove negative generation or emissions if improperly logged
    if 'generation_twh' in df.columns:
        df['generation_twh'] = df['generation_twh'].apply(lambda x: np.nan if (pd.notnull(x) and x < 0) else x)
    if 'emissions_mtco2e' in df.columns:
        df['emissions_mtco2e'] = df['emissions_mtco2e'].apply(lambda x: np.nan if (pd.notnull(x) and x < 0) else x)

    # Convert is_aggregated_source to boolean
    if 'is_aggregated_source' in df.columns:
        df['is_aggregated_source'] = df['is_aggregated_source'].astype(str).str.lower().map({'true': True, 'false': False}).fillna(False)

    # Fill missing carbon intensity if both emissions and generation are present and generation > 0
    # Formula: 1 MtCO2e / 1 TWh = 1000 gCO2e / 1 kWh
    mask_calc_intensity = df['emissions_intensity_gco2e_kwh'].isna() & df['emissions_mtco2e'].notna() & (df['generation_twh'] > 0)
    df.loc[mask_calc_intensity, 'emissions_intensity_gco2e_kwh'] = (df.loc[mask_calc_intensity, 'emissions_mtco2e'] * 1000.0) / df.loc[mask_calc_intensity, 'generation_twh']

    # Mark individual source flag
    df['is_individual_source'] = df['electricity_source_clean'].isin(INDIVIDUAL_SOURCES)

    # Drop exact duplicate rows
    df = df.drop_duplicates()

    return df

def validate_data(df):
    """
    Performs data integrity checks and returns diagnostic validation report.
    """
    total_rows = len(df)
    country_types = ['Country', 'Country or economy', 'CountryOrTerritory']
    unique_countries = df[df['area_type'].isin(country_types)]['area'].nunique() if 'area_type' in df.columns else df['area'].nunique()
    min_year = df['year'].min() if not df.empty else None
    max_year = df['year'].max() if not df.empty else None
    unique_sources = df['electricity_source_clean'].nunique() if 'electricity_source_clean' in df.columns else 0
    
    missing_gen = df['generation_twh'].isna().sum() if 'generation_twh' in df.columns else 0
    missing_emissions = df['emissions_mtco2e'].isna().sum() if 'emissions_mtco2e' in df.columns else 0
    missing_intensity = df['emissions_intensity_gco2e_kwh'].isna().sum() if 'emissions_intensity_gco2e_kwh' in df.columns else 0

    print("==================================================")
    print("           DATA VALIDATION SUMMARY               ")
    print("==================================================")
    print(f" Total Processed Rows    : {total_rows}")
    print(f" Unique Countries        : {unique_countries}")
    print(f" Year Range              : {min_year} - {max_year}")
    print(f" Standardized Sources    : {unique_sources}")
    print(f" Missing Generation Rows : {missing_gen}")
    print(f" Missing Emissions Rows  : {missing_emissions}")
    print(f" Missing Intensity Rows  : {missing_intensity}")
    print("==================================================")

    # Basic critical checks
    assert total_rows > 0, "Validation Failed: Dataset is empty!"
    assert min_year is not None and min_year >= 1980, f"Validation Failed: Invalid year range ({min_year})"
    print("[SUCCESS] Data validation passed clean checks.")
    return True

def save_processed_data(df, output_path=PROCESSED_DATA_PATH):
    """
    Saves clean DataFrame to CSV.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[SUCCESS] Saved clean processed dataset to '{output_path}'.")
    return output_path

def run_full_pipeline():
    """
    Runs complete ingestion and data processing pipeline.
    """
    raw_path = download_dataset()
    df_raw = load_raw_data(raw_path)
    df_norm = normalize_columns(df_raw)
    df_std = standardize_sources(df_norm)
    df_class = classify_renewable_status(df_std)
    df_clean = clean_data(df_class)
    validate_data(df_clean)
    save_processed_data(df_clean)
    return df_clean

if __name__ == "__main__":
    run_full_pipeline()
