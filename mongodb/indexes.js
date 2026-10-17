// HealthInsight MongoDB Index Definitions
// Run in: mongosh or MongoDB Compass Shell
// Database: healthinsight

use healthinsight;

// ============================================================
// kpis collection — single document, no index needed
// ============================================================

// ============================================================
// condition_summary
// ============================================================
db.condition_summary.createIndex({ condition_description: 1 });
db.condition_summary.createIndex({ frequency: -1 });

// ============================================================
// demographic_summary
// ============================================================
db.demographic_summary.createIndex({ gender: 1, age_group: 1 });
db.demographic_summary.createIndex({ race: 1 });
db.demographic_summary.createIndex({ ethnicity: 1 });

// ============================================================
// encounter_type_summary
// ============================================================
db.encounter_type_summary.createIndex({ encounter_type: 1 });
db.encounter_type_summary.createIndex({ encounter_count: -1 });

// ============================================================
// encounter_trends
// ============================================================
db.encounter_trends.createIndex({ year: 1, month: 1 });

// ============================================================
// organization_summary
// ============================================================
db.organization_summary.createIndex({ organization_name: 1 });
db.organization_summary.createIndex({ total_encounters: -1 });
db.organization_summary.createIndex({ avg_cost: -1 });

print("All indexes created successfully.");
