/**
 * HealthInsight v2 — AI Copilot & Patient Explorer Controller
 * Manages natural language query dispatching, Chart.js rendering, and patient lookup.
 */

let activeCharts = {};
let messageCounter = 0;

document.addEventListener('DOMContentLoaded', () => {
  const chatInput = document.getElementById('chat-input');
  const btnSend = document.getElementById('btn-send');
  const quickChips = document.querySelectorAll('.chip-btn');

  // Quick Chips click
  quickChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const question = chip.getAttribute('data-question');
      if (question) {
        if (chatInput) chatInput.value = question;
        submitQuestion(question);
      }
    });
  });

  // Send Button click
  if (btnSend) {
    btnSend.addEventListener('click', () => {
      const q = chatInput.value.trim();
      if (q) submitQuestion(q);
    });
  }

  // Input Enter key
  if (chatInput) {
    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const q = chatInput.value.trim();
        if (q) submitQuestion(q);
      }
    });
  }

  // Patient Explorer Search Button
  const btnSearchPatient = document.getElementById('btn-search-patient');
  const patientInput = document.getElementById('patient-id-input');

  if (btnSearchPatient && patientInput) {
    btnSearchPatient.addEventListener('click', () => {
      const pid = patientInput.value.trim();
      if (pid) lookupPatient(pid);
    });

    patientInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const pid = patientInput.value.trim();
        if (pid) lookupPatient(pid);
      }
    });
  }
});

/**
 * Dispatches clinical question to the backend and renders response.
 */
async function submitQuestion(question) {
  const chatThread = document.getElementById('chat-thread');
  const chatInput = document.getElementById('chat-input');
  const btnSend = document.getElementById('btn-send');

  if (!chatThread) return;

  // Append User Bubble
  const userBubble = document.createElement('div');
  userBubble.className = 'message-item message-user';
  userBubble.textContent = question;
  chatThread.appendChild(userBubble);

  if (chatInput) chatInput.value = '';
  if (btnSend) btnSend.disabled = true;

  // Append Loading Skeleton
  const loadingBubble = document.createElement('div');
  loadingBubble.className = 'message-item message-ai';
  loadingBubble.id = 'loading-bubble';
  loadingBubble.innerHTML = `
    <div style="display: flex; align-items: center; gap: 12px; color: var(--text-muted); font-size: 0.9rem;">
      <div class="pulse-dot" style="background: var(--cyan-primary); box-shadow: 0 0 12px var(--cyan-primary);"></div>
      <span>Synthesizing Trino SQL and executing across 321,528 Iceberg records...</span>
    </div>
  `;
  chatThread.appendChild(loadingBubble);
  chatThread.scrollTop = chatThread.scrollHeight;

  try {
    const res = await fetchWithAuth('/api/query/natural', {
      method: 'POST',
      body: JSON.stringify({ question })
    });

    const data = await res.json();
    loadingBubble.remove();

    if (res.ok) {
      renderAiResponse(data);
    } else {
      renderErrorBubble(data.detail || 'Query processing failed.');
    }
  } catch (err) {
    loadingBubble.remove();
    renderErrorBubble(err.message || 'Network error communicating with AI query engine.');
  } finally {
    if (btnSend) btnSend.disabled = false;
    chatThread.scrollTop = chatThread.scrollHeight;
  }
}

/**
 * Renders structured AI response with SQL block, data table, and Chart.js visualization.
 */
function renderAiResponse(data) {
  const chatThread = document.getElementById('chat-thread');
  messageCounter++;
  const msgId = `ai-msg-${messageCounter}`;
  const chartId = `chart-${messageCounter}`;
  const tableId = `table-${messageCounter}`;

  const aiBubble = document.createElement('div');
  aiBubble.className = 'message-item message-ai';
  aiBubble.id = msgId;

  // Format columns and table rows
  let tableHeaderHtml = data.columns.map(c => `<th>${escapeHtml(c)}</th>`).join('');
  let tableRowsHtml = data.rows.slice(0, 15).map(r => {
    const cells = r.map(cell => {
      let val = cell === null ? '<span style="color:var(--text-dim)">NULL</span>' : cell;
      if (typeof val === 'number') {
        val = Number.isInteger(val) ? val.toLocaleString() : val.toFixed(2);
      }
      return `<td>${val}</td>`;
    }).join('');
    return `<tr>${cells}</tr>`;
  }).join('');

  const engineLabel = data.engine === 'gemini-2.0-flash' ? '✦ Gemini 2.0 Flash' : '⚡ Clinical Template Router';

  aiBubble.innerHTML = `
    <div class="ai-meta-bar">
      <div class="meta-engine-tag">
        <svg style="width:16px;height:16px;fill:currentColor;" viewBox="0 0 24 24"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>
        <span>${engineLabel}</span>
      </div>
      <div class="meta-stats-pill">
        ⚡ ${data.execution_ms} ms · ${data.row_count} rows
      </div>
    </div>

    <div style="font-size: 0.95rem; color: var(--text-main);">
      ${escapeHtml(data.explanation)}
    </div>

    <!-- SQL Code Block -->
    <div class="sql-box">
      <div class="sql-header">
        <span>Generated Trino SQL</span>
        <button class="btn-copy-sql" onclick="copySqlToClipboard('${msgId}')">📋 Copy SQL</button>
      </div>
      <pre class="sql-code" id="${msgId}-sql">${escapeHtml(data.sql)}</pre>
    </div>

    <!-- View Toggle & Export -->
    <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 4px;">
      <div class="result-tabs">
        <button class="tab-btn active" onclick="switchResultTab('${msgId}', 'chart')">📊 Chart</button>
        <button class="tab-btn" onclick="switchResultTab('${msgId}', 'table')">📋 Data Table</button>
      </div>
      <button class="tab-btn" onclick="exportCsv('${msgId}')" style="display: flex; align-items: center; gap: 4px;">
        ⬇ Export CSV
      </button>
    </div>

    <!-- Chart Container -->
    <div class="chart-wrapper" id="${msgId}-chart-container">
      <canvas id="${chartId}"></canvas>
    </div>

    <!-- Table Container -->
    <div class="table-wrapper" id="${msgId}-table-container" style="display: none;">
      <table class="data-table" id="${tableId}">
        <thead><tr>${tableHeaderHtml}</tr></thead>
        <tbody>${tableRowsHtml}</tbody>
      </table>
    </div>
  `;

  chatThread.appendChild(aiBubble);

  // Store data on the DOM node for CSV export
  aiBubble.__queryData = data;

  // Initialize Chart.js
  setTimeout(() => {
    renderChart(chartId, data);
  }, 50);
}

/**
 * Render Chart.js with Cyber-Clinical Neon Glass Aesthetics
 */
function renderChart(canvasId, data) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !data.rows || data.rows.length === 0) return;

  const ctx = canvas.getContext('2d');
  const labels = data.rows.map(r => String(r[0] ?? 'N/A'));
  
  // Find first numeric column for dataset
  let numColIndex = 1;
  for (let c = 1; c < data.columns.length; c++) {
    if (data.rows.some(r => typeof r[c] === 'number')) {
      numColIndex = c;
      break;
    }
  }

  const values = data.rows.map(r => typeof r[numColIndex] === 'number' ? r[numColIndex] : parseFloat(r[numColIndex]) || 0);
  const metricLabel = data.columns[numColIndex] || 'Metric Value';

  const chartType = data.chart_type === 'doughnut' ? 'doughnut' : (data.chart_type === 'line' ? 'line' : 'bar');

  // Palette colors
  const palette = [
    'rgba(0, 212, 255, 0.85)',
    'rgba(139, 92, 246, 0.85)',
    'rgba(16, 185, 129, 0.85)',
    'rgba(245, 158, 11, 0.85)',
    'rgba(244, 63, 94, 0.85)',
    'rgba(56, 189, 248, 0.85)',
    'rgba(168, 85, 247, 0.85)'
  ];

  if (activeCharts[canvasId]) {
    activeCharts[canvasId].destroy();
  }

  activeCharts[canvasId] = new Chart(ctx, {
    type: chartType,
    data: {
      labels: labels,
      datasets: [{
        label: metricLabel,
        data: values,
        backgroundColor: chartType === 'doughnut' ? palette : 'rgba(0, 212, 255, 0.55)',
        borderColor: chartType === 'doughnut' ? '#050B18' : 'rgba(0, 212, 255, 1)',
        borderWidth: chartType === 'line' ? 2.5 : 1,
        fill: chartType === 'line',
        tension: 0.35,
        borderRadius: chartType === 'bar' ? 6 : 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: chartType === 'doughnut',
          labels: { color: '#94A3B8', font: { family: 'Inter', size: 11 } }
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          borderColor: 'rgba(0, 212, 255, 0.4)',
          borderWidth: 1,
          titleColor: '#FFFFFF',
          bodyColor: '#38BDF8',
          padding: 10,
          cornerRadius: 8
        }
      },
      scales: chartType === 'doughnut' ? {} : {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.04)' },
          ticks: { color: '#94A3B8', font: { family: 'Inter', size: 10 } }
        },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.04)' },
          ticks: { color: '#94A3B8', font: { family: 'Inter', size: 10 } }
        }
      }
    }
  });
}

/**
 * Toggle between Chart and Data Table views.
 */
function switchResultTab(msgId, tabType) {
  const chartContainer = document.getElementById(`${msgId}-chart-container`);
  const tableContainer = document.getElementById(`${msgId}-table-container`);
  const buttons = document.querySelectorAll(`#${msgId} .result-tabs .tab-btn`);

  buttons.forEach(b => b.classList.remove('active'));

  if (tabType === 'chart') {
    if (chartContainer) chartContainer.style.display = 'block';
    if (tableContainer) tableContainer.style.display = 'none';
    buttons[0]?.classList.add('active');
  } else {
    if (chartContainer) chartContainer.style.display = 'none';
    if (tableContainer) tableContainer.style.display = 'block';
    buttons[1]?.classList.add('active');
  }
}

/**
 * Copies generated SQL to clipboard with visual feedback.
 */
function copySqlToClipboard(msgId) {
  const codeEl = document.getElementById(`${msgId}-sql`);
  if (!codeEl) return;
  navigator.clipboard.writeText(codeEl.textContent).then(() => {
    const btn = document.querySelector(`#${msgId} .btn-copy-sql`);
    if (btn) {
      btn.textContent = '✓ Copied!';
      setTimeout(() => { btn.textContent = '📋 Copy SQL'; }, 2000);
    }
  });
}

/**
 * Exports query results to CSV format.
 */
function exportCsv(msgId) {
  const msgEl = document.getElementById(msgId);
  if (!msgEl || !msgEl.__queryData) return;

  const data = msgEl.__queryData;
  let csvContent = "data:text/csv;charset=utf-8,";
  csvContent += data.columns.join(",") + "\r\n";

  data.rows.forEach(row => {
    const escapedRow = row.map(v => {
      let str = v === null ? "" : String(v);
      if (str.includes(",") || str.includes("\"") || str.includes("\n")) {
        str = `"${str.replace(/"/g, '""')}"`;
      }
      return str;
    });
    csvContent += escapedRow.join(",") + "\r\n";
  });

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `healthinsight_query_${Date.now()}.csv`);
  document.body.appendChild(link);
  link.click();
  link.remove();
}

/**
 * Renders an error message bubble.
 */
function renderErrorBubble(errorText) {
  const chatThread = document.getElementById('chat-thread');
  const errBubble = document.createElement('div');
  errBubble.className = 'message-item message-ai';
  errBubble.style.borderColor = 'rgba(244, 63, 94, 0.4)';
  errBubble.innerHTML = `
    <div style="color: #FDA4AF; display: flex; align-items: center; gap: 8px; font-weight: 600;">
      <svg style="width:18px;height:18px;fill:currentColor;" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
      <span>Query Execution Error</span>
    </div>
    <div style="color: var(--text-muted); font-size: 0.9rem;">${escapeHtml(errorText)}</div>
  `;
  chatThread.appendChild(errBubble);
}

/**
 * Patient Explorer Lookup
 */
async function lookupPatient(patientId) {
  const container = document.getElementById('patient-result-container');
  if (!container) return;

  container.innerHTML = `
    <div style="padding: 32px; text-align: center; color: var(--text-muted);">
      <div class="pulse-dot" style="margin: 0 auto 12px;"></div>
      <span>Querying longitudinal patient record across Trino and MongoDB...</span>
    </div>
  `;

  try {
    const res = await fetchWithAuth(`/api/patient/${encodeURIComponent(patientId)}`);
    if (!res.ok) {
      container.innerHTML = `
        <div style="padding: 24px; color: #FDA4AF; background: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: var(--radius-md);">
          Patient record for ID "${escapeHtml(patientId)}" was not found in the synthetic lakehouse.
        </div>
      `;
      return;
    }

    const data = await res.json();
    const demo = data.demographics;
    const conds = data.diagnosed_conditions;
    const encs = data.recent_encounters;

    // Conditions HTML
    let condsHtml = conds.length ? conds.map(c => `
      <span style="background: rgba(139, 92, 246, 0.15); border: 1px solid rgba(139, 92, 246, 0.3); color: #C4B5FD; padding: 4px 10px; border-radius: 9999px; font-size: 0.8rem; display: inline-flex; align-items: center; gap: 6px;">
        ● ${escapeHtml(c.condition_description)}
      </span>
    `).join('') : '<span style="color: var(--text-dim); font-size: 0.85rem;">No documented conditions</span>';

    // Encounters timeline HTML
    let encsHtml = encs.length ? encs.map(e => `
      <div class="timeline-item">
        <div>
          <div style="font-weight: 600; color: white; font-size: 0.9rem;">${escapeHtml(e.encounter_description || e.encounter_class)}</div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 2px;">
            ${escapeHtml(e.organization_name || 'Hospital')} · ${e.encounter_date} · ${e.duration_minutes} mins
          </div>
        </div>
        <div style="text-align: right;">
          <div style="font-weight: 700; color: #38BDF8; font-size: 0.95rem;">$${Number(e.total_claim_cost).toFixed(2)}</div>
          <div style="font-size: 0.75rem; color: var(--text-dim);">Out of pocket: $${Number(e.patient_out_of_pocket).toFixed(2)}</div>
        </div>
      </div>
    `).join('') : '<div style="color: var(--text-dim); font-size: 0.85rem;">No recorded clinical visits.</div>';

    container.innerHTML = `
      <div class="patient-card-grid">
        
        <!-- Demographics Card -->
        <div class="glass-panel patient-demographics-card">
          <div class="patient-avatar-box">
            <div class="patient-avatar">${demo.patient_gender}</div>
            <div>
              <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--cyan-primary);">${demo.patient_id.substring(0, 16)}...</div>
              <div style="font-size: 1.1rem; font-weight: 700; color: white;">Longitudinal Subject</div>
              <div style="font-size: 0.8rem; color: var(--text-muted);">${demo.patient_city}, ${demo.patient_state}</div>
            </div>
          </div>

          <div class="detail-row">
            <span class="detail-label">Gender</span>
            <span class="detail-value">${demo.patient_gender === 'M' ? 'Male' : 'Female'}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Birthdate</span>
            <span class="detail-value">${demo.patient_birthdate}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Race / Ethnicity</span>
            <span class="detail-value">${demo.patient_race} · ${demo.patient_ethnicity}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Total Visits</span>
            <span class="detail-value" style="color: var(--cyan-primary); font-weight: 700;">${Number(demo.total_encounters).toLocaleString()}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Total Claim Spend</span>
            <span class="detail-value" style="color: #10B981; font-weight: 700;">$${Number(demo.total_claim_cost).toLocaleString()}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Out of Pocket</span>
            <span class="detail-value">$${Number(demo.total_out_of_pocket).toLocaleString()}</span>
          </div>

          <div style="margin-top: 8px;">
            <div style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); margin-bottom: 8px; text-transform: uppercase;">Diagnosed Conditions</div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
              ${condsHtml}
            </div>
          </div>
        </div>

        <!-- Encounters Timeline Card -->
        <div class="glass-panel" style="padding: 24px;">
          <h3 style="color: white; font-size: 1.15rem; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between;">
            <span>Recent Clinical Encounters</span>
            <span style="font-size: 0.8rem; color: var(--text-muted); font-weight: 400;">Last ${encs.length} recorded events</span>
          </h3>
          <div class="timeline-list">
            ${encsHtml}
          </div>
        </div>

      </div>
    `;

  } catch (err) {
    container.innerHTML = `
      <div style="padding: 24px; color: #FDA4AF; background: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: var(--radius-md);">
        Error loading patient profile: ${escapeHtml(err.message)}
      </div>
    `;
  }
}

function escapeHtml(str) {
  if (typeof str !== 'string') return String(str ?? '');
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
