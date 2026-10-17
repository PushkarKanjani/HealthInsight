// HealthInsight MongoDB Validation Queries
// Run in: mongosh or MongoDB Compass Shell
// Purpose: Verify that all collections are populated with real data from Spark

use healthinsight;

print("=== HealthInsight MongoDB Validation ===\n");

// --- KPIs ---
print("--- KPIs ---");
print("Document count:", db.kpis.countDocuments());
printjson(db.kpis.findOne());

// --- Condition Summary ---
print("\n--- Condition Summary ---");
print("Document count:", db.condition_summary.countDocuments());
print("Top 5 conditions:");
db.condition_summary.find({}, { condition_description: 1, frequency: 1, _id: 0 })
    .sort({ frequency: -1 }).limit(5).forEach(printjson);

// --- Demographic Summary ---
print("\n--- Demographic Summary ---");
print("Document count:", db.demographic_summary.countDocuments());
printjson(db.demographic_summary.findOne());

// --- Encounter Type Summary ---
print("\n--- Encounter Type Summary ---");
print("Document count:", db.encounter_type_summary.countDocuments());
db.encounter_type_summary.find({}, { encounter_type: 1, encounter_count: 1, _id: 0 })
    .sort({ encounter_count: -1 }).forEach(printjson);

// --- Encounter Trends ---
print("\n--- Encounter Trends (first 5 months) ---");
print("Document count:", db.encounter_trends.countDocuments());
db.encounter_trends.find({}, { year: 1, month: 1, encounter_count: 1, _id: 0 })
    .sort({ year: 1, month: 1 }).limit(5).forEach(printjson);

// --- Organization Summary ---
print("\n--- Organization Summary (top 5) ---");
print("Document count:", db.organization_summary.countDocuments());
db.organization_summary.find({}, { organization_name: 1, total_encounters: 1, _id: 0 })
    .sort({ total_encounters: -1 }).limit(5).forEach(printjson);

print("\n=== Validation Complete ===");
