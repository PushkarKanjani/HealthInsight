/**
 * HealthInsight v2 — Lakehouse Health & KPI Monitor
 * Polls real-time telemetry from Trino, Iceberg, and MongoDB.
 */

async function loadExecutiveKPIs() {
  try {
    const res = await fetchWithAuth('/api/kpis');
    if (!res.ok) return;
    const data = await res.json();

    const elPatients = document.getElementById('kpi-patients');
    const elEncounters = document.getElementById('kpi-encounters');
    const elCost = document.getElementById('kpi-cost');
    const elDuration = document.getElementById('kpi-duration');

    if (elPatients && data.total_patients) {
      elPatients.textContent = Number(data.total_patients).toLocaleString();
    }
    if (elEncounters && data.total_encounters) {
      elEncounters.textContent = Number(data.total_encounters).toLocaleString();
    }
    if (elCost && data.total_claim_cost) {
      elCost.textContent = '$' + (Number(data.total_claim_cost) / 1000000).toFixed(2) + 'M';
    }
    if (elDuration && data.avg_claim_cost) {
      elDuration.textContent = '$' + Number(data.avg_claim_cost).toFixed(2);
    }
  } catch (err) {
    console.error('Failed to load KPIs:', err);
  }
}

async function loadSystemHealth() {
  try {
    const res = await fetchWithAuth('/api/health');
    if (!res.ok) return;
    const data = await res.json();
    const services = data.services || {};

    // 1. Trino
    const trinoStatusEl = document.getElementById('trino-status-pill');
    const trinoLatencyEl = document.getElementById('trino-latency');
    const trinoRecordsEl = document.getElementById('trino-records');
    if (services.trino && services.trino.status === 'healthy') {
      if (trinoStatusEl) trinoStatusEl.innerHTML = '<span class="pulse-dot"></span> CONNECTED';
      if (trinoLatencyEl) trinoLatencyEl.textContent = `${services.trino.latency_ms} ms`;
      if (trinoRecordsEl && services.trino.total_encounters) {
        trinoRecordsEl.textContent = `${Number(services.trino.total_encounters).toLocaleString()} rows`;
      }
    }

    // 2. Iceberg
    const icebergTablesEl = document.getElementById('iceberg-tables');
    if (services.iceberg) {
      if (icebergTablesEl) icebergTablesEl.textContent = `${services.iceberg.tables_registered} registered`;
    }

    // 3. MongoDB
    const mongoStatusEl = document.getElementById('mongo-status-pill');
    const mongoLatencyEl = document.getElementById('mongo-latency');
    const mongoCollectionsEl = document.getElementById('mongo-collections');
    if (services.mongodb && services.mongodb.status === 'healthy') {
      if (mongoStatusEl) mongoStatusEl.innerHTML = '<span class="pulse-dot"></span> OPERATIONAL';
      if (mongoLatencyEl) mongoLatencyEl.textContent = `${services.mongodb.latency_ms} ms`;
      if (mongoCollectionsEl) mongoCollectionsEl.textContent = `${services.mongodb.collections_count} collections`;
    }

    // 4. AI Copilot
    const aiStatusEl = document.getElementById('ai-status-pill');
    const aiEngineEl = document.getElementById('ai-engine-name');
    if (services.ai_copilot) {
      if (aiStatusEl) aiStatusEl.innerHTML = '<span class="pulse-dot"></span> ONLINE';
      if (aiEngineEl) {
        aiEngineEl.textContent = services.ai_copilot.mode === 'gemini-2.0-flash'
          ? 'Gemini 2.0 Flash'
          : 'Deterministic Fallback (12 Clinical Templates)';
      }
    }

  } catch (err) {
    console.error('Failed to load system health:', err);
  }
}

async function loadCollectionsList() {
  try {
    const res = await fetchWithAuth('/api/collections');
    if (!res.ok) return;
    const collections = await res.json();
    const tableBody = document.getElementById('collections-table-body');
    if (!tableBody) return;

    tableBody.innerHTML = '';
    collections.forEach((col) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-family: 'JetBrains Mono', monospace; font-weight: 600; color: #38BDF8;">healthinsight.${col.collection}</td>
        <td><span style="background: rgba(16, 185, 129, 0.15); color: #10B981; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600;">${col.document_count.toLocaleString()} docs</span></td>
        <td style="color: var(--text-muted); font-size: 0.85rem;">${col.description}</td>
        <td><span style="font-size: 0.8rem; color: var(--text-dim);">${col.storage_engine}</span></td>
      `;
      tableBody.appendChild(tr);
    });
  } catch (err) {
    console.error('Failed to load collections list:', err);
  }
}

// Initial triggers
document.addEventListener('DOMContentLoaded', () => {
  loadExecutiveKPIs();
  loadSystemHealth();
  loadCollectionsList();

  // Poll health every 25 seconds
  setInterval(loadSystemHealth, 25000);
});
