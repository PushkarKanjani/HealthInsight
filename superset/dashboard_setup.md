# Superset Dashboard Setup Guide
## HealthInsight Healthcare Analytics

> Connect Apache Superset to Trino and build the HealthInsight dashboard.

---

## Prerequisites

- Trino is running: `http://localhost:8080`
- Iceberg tables exist and are queryable via Trino
- Superset is installed and running: `http://localhost:8088`

---

## Step 1: Install Trino Python Client in Superset Environment

```bash
# In the Superset virtual environment
pip install trino
```

---

## Step 2: Add Trino as a Database in Superset

1. Go to **Settings → Database Connections → + Database**
2. Select engine: **Trino**
3. Enter connection details:
   ```
   SQLAlchemy URI: trino://localhost:8080/iceberg
   Display Name: HealthInsight Trino
   ```
4. Click **Test Connection** — must succeed before saving
5. Click **Save**

---

## Step 3: Create Datasets

For each SQL query below, create a new dataset in Superset:

**Settings → Datasets → + Dataset**

| Dataset Name | SQL File | Table |
|---|---|---|
| kpi_overview | `trino/queries/01_kpis.sql` | Virtual dataset |
| condition_frequency | `trino/queries/02_conditions.sql` | Virtual dataset |
| demographic_distribution | `trino/queries/03_demographics.sql` | Virtual dataset |
| encounter_analytics | `trino/queries/04_encounters.sql` | Virtual dataset |
| monthly_trends | `trino/queries/05_trends.sql` | Virtual dataset |

---

## Step 4: Create Charts

### KPI Cards (from `kpi_overview`)
- Chart type: **Big Number**
- Metric: `total_patients`
- Repeat for: `total_encounters`, `avg_encounter_duration_days`, `avg_claim_cost`

### Condition Frequency (from `condition_frequency`)
- Chart type: **Bar Chart (horizontal)**
- X-axis: `frequency`
- Y-axis: `condition_description`
- Sort: by frequency descending
- Limit: 20

### Gender Distribution (from `demographic_distribution`)
- Chart type: **Pie Chart**
- Metric: `patient_count`
- Group by: `gender`

### Monthly Trend (from `monthly_trends`)
- Chart type: **Line Chart**
- X-axis: `month` (formatted as Year-Month)
- Y-axis: `encounter_count`
- Use time grain: Month

### Encounter Type Count (from `encounter_analytics`)
- Chart type: **Bar Chart (vertical)**
- X-axis: `encounter_type`
- Y-axis: `encounter_count`

---

## Step 5: Build Dashboard

1. Go to **Dashboards → + Dashboard**
2. Title: `HealthInsight Healthcare Analytics`
3. Drag and drop charts into the layout
4. Add tabs:
   - Overview
   - Conditions
   - Demographics
   - Encounters
   - Organizations
   - Trends
   - Data Lineage

---

## Step 6: Apply Trustworthy Clinical Light Theme CSS

In Dashboard edit mode → **···** → **Edit CSS**:

```css
/* HealthInsight Clinical Light Theme (Inspired by Medisafe & Jinga Life) */
body, .dashboard {
  background-color: #F8FAFC !important;
  color: #0F172A !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}

/* Clinical elevated white cards */
.dashboard-component-chart-holder {
  background: #FFFFFF !important;
  border: 1px solid #E2E8F0 !important;
  border-radius: 12px !important;
  box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 6px 16px -2px rgba(15, 23, 42, 0.03) !important;
  transition: all 0.2s ease-in-out !important;
}

.dashboard-component-chart-holder:hover {
  border-color: #CBD5E1 !important;
  box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.06), 0 12px 20px -3px rgba(15, 23, 42, 0.05) !important;
}

/* Header & navigation bar */
.header-with-controls, .dashboard-header {
  background: #FFFFFF !important;
  border-bottom: 1px solid #E2E8F0 !important;
  box-shadow: 0 1px 2px 0 rgba(15, 23, 42, 0.03) !important;
}

.chart-header .header-title {
  color: #0F172A !important;
  font-weight: 600 !important;
  font-size: 15px !important;
}

/* Big Number / KPI values */
.dashboard-component-chart-holder .superset-legacy-chart-big-number text {
  fill: #0072CE !important;
  font-weight: 800 !important;
}

/* Filter bar & tab active indicators */
.ant-tabs-ink-bar {
  background: #0072CE !important;
}
.ant-tabs-tab-active .ant-tabs-tab-btn {
  color: #0072CE !important;
  font-weight: 600 !important;
}
```

---

## Screenshot Checklist for Dashboard

- [ ] Overview tab with all KPI cards loaded
- [ ] Conditions tab with top-20 bar chart
- [ ] Demographics tab with donut + bar charts
- [ ] Encounters tab with type breakdown
- [ ] Trends tab with monthly line chart
- [ ] SQL Lab query showing live Trino results
