# 🌿 Academic Project Report Notes: Carbon Footprint Analysis of Electricity Generation Sources

**Course / Subject:** Environmental Studies (EVS) Mini-Project  
**Domain:** Environmental Analytics & Clean Energy Transition  
**Evaluator Target:** Academic Panel & Faculty  

---

## 1. Executive Summary & Project Objective

Electricity generation is the single largest contributor to global greenhouse gas (GHG) emissions. However, different power generation technologies exhibit radically different operational carbon footprints. 

The primary objective of this project is to construct a **data-driven interactive analytics platform** using real-world electricity dataset from **Ember** to analyze:
1. Electricity generation (TWh) across thermal, nuclear, and renewable sources.
2. Total direct greenhouse gas emissions ($\text{MtCO}_2\text{e}$) associated with power production.
3. Weighted operational carbon intensity ($\text{gCO}_2\text{e/kWh}$) across power generation technologies and national grids.
4. Share of renewable vs. non-renewable electricity over time (1985–2025).
5. Side-by-side comparative grid assessments (with dedicated focus on India's energy transition).

---

## 2. Audited Dataset Statistics

* **Primary Dataset:** Ember Yearly Electricity Data (Global Output)
* **Dataset Provider:** Ember (Energy Think Tank)
* **Official URL:** `https://ember-energy.org/data/yearly-electricity-data/`
* **Direct Data Source:** `https://files.ember-energy.org/public-downloads/generation/outputs/release_generation_yearly_global.csv`
* **Total Volume:** 104,273 observations spanning 209 countries/territories and 1985–2025.
* **Core Variables Utilized:**
  * `Area` (Country/Region Name) & `ISO 3 code`
  * `Year` (Temporal dimension)
  * `Electricity source` (Thermal, Nuclear, Renewables)
  * `Generation (TWh)` (Gigawatt-hours / Terawatt-hours)
  * `Emissions (MtCO2e)` (Million Metric Tonnes of $\text{CO}_2$ equivalent)
  * `Emissions intensity (gCO2e/kWh)` (Grams of $\text{CO}_2\text{e}$ per Kilowatt-hour)

---

## 3. Mathematical & Environmental Formulas

### 3.1 Operational Carbon Intensity ($\text{gCO}_2\text{e/kWh}$)
$$\text{Carbon Intensity} = \frac{\text{Emissions } (\text{MtCO}_2\text{e}) \times 10^9 \text{ g}}{\text{Generation } (\text{TWh}) \times 10^9 \text{ kWh}} = \frac{\text{Emissions } (\text{MtCO}_2\text{e}) \times 1000}{\text{Generation } (\text{TWh})}$$

*Unit Conversion Equivalence:*
$$1 \text{ gCO}_2\text{e/kWh} = 1 \text{ kgCO}_2\text{e/MWh} = 1000 \text{ tCO}_2\text{e/GWh}$$

### 3.2 Renewable & Clean Share (%)
$$\text{Renewable Share (\%)} = \left( \frac{\sum \text{Generation}_{\text{Renewables}}}{\text{Total Generation}} \right) \times 100$$

$$\text{Clean Energy Share (\%)} = \left( \frac{\sum \text{Generation}_{\text{Renewables}} + \text{Generation}_{\text{Nuclear}}}{\text{Total Generation}} \right) \times 100$$

---

## 4. Resource Classification System

| Electricity Source | Primary Energy Source | Resource Classification | Low-Carbon Status |
| :--- | :--- | :--- | :--- |
| **Coal** | Fossil Fuel | Non-renewable | ❌ High Carbon (~800–1000+ gCO2e/kWh) |
| **Natural Gas** | Fossil Fuel | Non-renewable | ⚠️ Moderate Carbon (~400–500 gCO2e/kWh) |
| **Oil** | Fossil Fuel | Non-renewable | ❌ High Carbon (~700–900 gCO2e/kWh) |
| **Nuclear** | Fissile Material (Uranium) | Non-renewable | ✅ Low Operational Carbon (~12–25 gCO2e/kWh) |
| **Hydropower** | Kinetic Water | Renewable | ✅ Low Carbon |
| **Solar PV / Thermal**| Solar Radiation | Renewable | ✅ Low Carbon |
| **Wind (Onshore/Offshore)**| Atmospheric Wind | Renewable | ✅ Low Carbon |
| **Biomass / Bioenergy**| Organic Matter | Renewable | ⚠️ Combustion Carbon (Biogenic cycle) |

> 📌 **Academic Distinction Note:** Nuclear power is classified as **Non-renewable** in our resource taxonomy due to finite uranium reserves, while acknowledging that its **operational greenhouse gas intensity is near zero**.

---

## 5. Software Architecture & Pipeline

```text
[ Ember Direct CSV ] 
        ↓  (requests / urllib)
[ Raw Ingestion: data/raw/ember_yearly_global.csv ]
        ↓  (pandas normalization & sanitization)
[ Standardized Classification & Derived Metric Engine ]
        ↓  (data validation checks)
[ Processed Clean Storage: data/processed/electricity_carbon_clean.csv ]
        ↓  (modular analytics src/analysis.py)
[ Streamlit Web Application (app.py) & Plotly Interactive Visualizations ]
```

---

## 6. Key Findings & Environmental Policy Insights

1. **Fossil Fuel Dominance in Grid Carbon Intensity:** Thermal coal remains the largest single driver of power sector $\text{CO}_2$ emissions globally, contributing over 70% of total electricity emissions in developing grids.
2. **Decoupling Generation from Emissions:** Nations aggressively expanding Solar and Wind capacity (alongside firm Nuclear/Hydro power) demonstrate a steep drop in grid carbon intensity ($\text{gCO}_2\text{e/kWh}$) even as total electricity demand grows.
3. **India Energy Transition:** India's solar generation has grown exponentially post-2015, helping curb the rate of carbon intensity increase despite growing overall electricity demand.

---

## 7. Project Scope & Academic Limitations

1. **Direct Operational Focus:** This study evaluates operational power station emissions. It does not perform a cradle-to-grave Life Cycle Assessment (LCA) embodied carbon accounting for equipment manufacturing or plant construction.
2. **Reporting Basis:** Figures rely on country-level reporting compiled by Ember.
3. **Missing Value Integrity:** Missing emission datapoints are preserved as nulls rather than zero-filled to prevent statistical skew.
