# HealthInsight — MongoDB Serving Layer Verification
> **Phase 4 / Prompt 11 Verification**
> **Executed Engine:** Apache Spark 3.5 & PyMongo 4.19
> **Database:** `healthinsight` on `localhost:27017`

---

## 1. Verified Collection Inventory

| Collection Name | Document Count | Source Analytical Table | Description |
|---|---|---|---|
| `kpis` | **1** | `iceberg.healthcare.encounter_analytics` | High-level operational, visit volume, and financial KPIs |
| `condition_summary` | **180** | `iceberg.healthcare.condition_analytics` | Unique clinical condition codes, descriptions, and diagnosis counts |
| `encounter_type_summary` | **6** | `iceberg.healthcare.encounter_analytics` | Breakdown by encounter class (`wellness`, `outpatient`, `ambulatory`, `inpatient`, `emergency`, `urgentcare`) |
| `encounter_trends` | **1,297** | `iceberg.healthcare.encounter_analytics` | Longitudinal monthly visit volumes and claim totals across multi-decade history |
| `demographic_summary` | **89** | `iceberg.healthcare.encounter_analytics` | Patient demographic slices by gender, age group, race, and ethnicity |
| `organization_summary` | **5,209** | `iceberg.healthcare.encounter_analytics` | Clinical facilities, hospitals, and outpatient clinics with visit and billing totals |

---

## 2. Sample Verified Documents

### `kpis` Document
```json
{
  "total_patients": 12330,
  "total_encounters": 321528,
  "avg_duration_minutes": 14006.46,
  "avg_claim_cost": 128.71,
  "total_claim_cost": 41384293.84,
  "total_payer_coverage": 20469649.26,
  "total_out_of_pocket": 20914644.58,
  "source_table": "iceberg.healthcare.encounter_analytics",
  "generated_at": "2026-10-18T11:12:14.379208+00:00"
}
```

### Top 3 Conditions (`condition_summary`)
1. **Suspected COVID-19** (Code: `840544004`): 9,106 diagnoses
2. **COVID-19** (Code: `840539006`): 8,820 diagnoses
3. **Fever (finding)** (Code: `386661006`): 8,083 diagnoses

### Encounter Breakdown by Class (`encounter_type_summary`)
1. **wellness**: 120,441 visits | Total Billing: $12,716,664.12
2. **outpatient**: 105,437 visits | Total Billing: $14,942,881.08
3. **ambulatory**: 71,215 visits | Total Billing: $9,655,873.30
4. **inpatient**: 11,821 visits | Total Billing: $2,787,249.49
5. **emergency**: 8,832 visits | Total Billing: $868,540.08
6. **urgentcare**: 3,782 visits | Total Billing: $413,085.77

---

## 3. Index Verification
All indexes created and verified:
* `condition_summary`: `condition_description: 1`, `frequency: -1`
* `encounter_type_summary`: `encounter_class: 1`, `encounter_count: -1`
* `encounter_trends`: `year: 1, month: 1`
* `demographic_summary`: `patient_gender: 1, age_group: 1`
* `organization_summary`: `organization_name: 1`, `total_encounters: -1`
