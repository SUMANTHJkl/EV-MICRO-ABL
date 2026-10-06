# 🌍 Carbon Footprint Analysis of Electricity Generation Sources

**Academic Level:** Environmental Studies (EVS) Mini-Project  
**Domain:** Environmental Analytics & Clean Energy Transition  
**Tech Stack:** Python, Pandas, NumPy, Plotly, Streamlit  
**Primary Dataset:** Ember Yearly Electricity Data (1985–2025)  

---

## 📌 1. Project Overview & Problem Statement

Electricity generation is vital for modern society, but power generation technologies differ dramatically in their operational carbon footprints. Thermal power plants burning coal or natural gas emit high quantities of greenhouse gases ($\text{CO}_2\text{e}$), whereas solar, wind, hydropower, and nuclear energy produce low operational carbon emissions.

This project delivers a **data-driven interactive analytics system** that processes real-world global power sector data to evaluate:
* How much electricity different sources generate ($\text{TWh}$).
* Total greenhouse gas emissions ($\text{MtCO}_2\text{e}$) associated with power production.
* Grid carbon intensity ($\text{gCO}_2\text{e/kWh}$) across energy sources and nations.
* Renewable vs. non-renewable electricity transition trends.
* Country-level grid comparisons with a quick focus on **India**.

---

## 🎯 2. Core Features & Dashboard Capabilities

1. **Dynamic Interactive Filters & Reset:** Filter globally by Country/Region (209 countries), Year Range (1985–2025), and Electricity Source. Includes a one-click **"🔄 Reset Filters"** button.
2. **🇮🇳 Quick Select India Focus:** One-click instant dashboard configuration for India's energy transition.
3. **KPI Metric Banner:** Dynamic calculations for Total Generation ($\text{TWh}$), CO₂e Emissions ($\text{MtCO}_2\text{e}$), Grid Carbon Intensity ($\text{gCO}_2\text{e/kWh}$), and Renewable Share ($\%$). Refined layout ensures numbers and units fit without wrapping.
4. **Source Breakdown (Tab 1):** Interactive bar charts comparing total generation (TWh), direct emissions (MtCO₂e), and carbon intensity (gCO₂e/kWh) across power technologies.
5. **Carbon Intensity Analysis (Tab 2):** Ranked horizontal charts and tabular data evaluating clean power efficiency ($\text{gCO}_2\text{e/kWh}$).
6. **Renewable Energy Tracker (Tab 3):** Donut charts and historical trend lines monitoring Solar, Wind, Hydro, and Biomass growth over time.
7. **Historical Trends (Tab 4):** Time-series trends of generation, emissions, and intensity.
8. **Side-by-Side Comparisons (Tab 5):** Compare two countries (e.g., India vs. USA) or two electricity sources (e.g., Coal vs. Solar) side-by-side.
9. **Interactive Global Map (Tab 6):** Plotly Choropleth map mapping carbon intensity and emissions worldwide by country.
10. **Automated Environmental Insights:** Dynamic natural-language takeaways generated programmatically from filtered datasets.
11. **Data Export:** Filtered dataset preview with instant CSV download button.

---

## 📊 3. Dataset Information & Audited Statistics

* **Name:** Ember Yearly Electricity Data
* **Provider:** Ember (Global Energy Think Tank)
* **Official URL:** [Ember Energy Data Page](https://ember-energy.org/data/yearly-electricity-data/)
* **Direct CSV Source:** `https://files.ember-energy.org/public-downloads/generation/outputs/release_generation_yearly_global.csv`
* **Total Rows Processed:** `104,273` rows
* **Unique Countries/Territories:** `209` nations (+ regional aggregates like G20, ASEAN, World)
* **Year Range:** `1985` to `2025`
* **Sources Covered:** `Coal`, `Natural Gas`, `Oil`, `Other Fossil`, `Nuclear`, `Hydropower`, `Solar`, `Wind`, `Biomass`, `Other Renewable`
* **Missing Value Integrity:** Missing values are preserved as nulls rather than zero-filled to prevent statistical distortion.

---

## 🏗️ 4. System Architecture & Data Flow

```text
User Interface (Streamlit app.py)
       ↑  ↓  (Filters & Dynamic Interactions)
Analytical Engine (src/analysis.py)
       ↑  ↓  (DataFrame Transformations & KPI Math)
Clean Processed Storage (data/processed/electricity_carbon_clean.csv)
       ↑  ↓  (Data Pipeline run_pipeline.py & src/data_processing.py)
Raw Ingestion (data/raw/ember_yearly_global.csv)
       ↑
Ember Dataset Direct CSV Download
```

---

## 📂 5. Project Directory Structure

```text
carbon-footprint-electricity/
│
├── data/
│   ├── raw/
│   │   └── ember_yearly_global.csv       # Raw Ember dataset
│   └── processed/
│       └── electricity_carbon_clean.csv # Processed & normalized clean dataset
│
├── report/
│   └── project_notes.md                 # Academic viva report & formulas
│
├── src/
│   ├── __init__.py                      # Python package marker
│   ├── data_processing.py               # Ingestion, cleaning & metric pipeline
│   └── analysis.py                      # Modular analytical DataFrame functions
│
├── app.py                               # Main Streamlit web application
├── run_pipeline.py                      # Pipeline execution script
├── requirements.txt                     # Project dependencies
└── README.md                            # Project documentation
```

---

## 🚀 6. How to Run the Application (Windows PowerShell)

### Step 1: Open PowerShell and Navigate to Project Directory
```powershell
cd c:\Users\Sumanth\Desktop\EV-MICRO\carbon-footprint-electricity
```

### Step 2: Install Required Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 3: Run the Data Processing Pipeline
```powershell
python run_pipeline.py
```

### Step 4: Launch the Interactive Streamlit Dashboard
```powershell
python -m streamlit run app.py
```
*(Open `http://localhost:8501` in your browser)*

---

## 🔬 7. Mathematical Formulas & Verification

### Operational Carbon Intensity ($\text{gCO}_2\text{e/kWh}$)
$$\text{Carbon Intensity} = \frac{\text{Total CO}_2\text{e Emissions (MtCO}_2\text{e}) \times 1000}{\text{Total Generation (TWh)}}$$

### Resource Classification Taxonomy
* **Renewable Sources:** Hydropower, Solar, Wind, Biomass, Other Renewables.
* **Non-Renewable Sources:** Coal, Natural Gas, Oil, Nuclear, Other Fossil.
* *Note on Nuclear:* Nuclear energy is classified under Non-renewable due to finite uranium fuel resources, while recognizing that its operational carbon intensity is low (~12–25 $\text{gCO}_2\text{e/kWh}$).

---

## ⚠️ 8. Academic Scope & Limitations

1. **Power Sector Operational Scope:** The analysis models direct generation emissions reported by Ember. It does not perform full life-cycle assessment (LCA) embodied carbon accounting.
2. **Missing Data Handling:** Missing metrics are preserved as nulls rather than zero-filled to maintain statistical accuracy.
