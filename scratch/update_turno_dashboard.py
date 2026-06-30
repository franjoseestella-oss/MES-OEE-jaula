import json
import urllib.request
import urllib.error
import base64
import os

GRAFANA_URL = "http://localhost:3010"
USER = "fran.jose.estella@gmail.com"
PASS = "admin123"

auth = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

# Paths
filepath = 'grafana/provisioning/dashboards/turno_actual_dashboard.json'

# HTML content for Panel 1 (OEE y KPIs) - larger gauge (radius 90, width/height 220, larger font sizes, fixed percentage formula)
panel_1_content = """<style>
  .kpi-container {
    display: flex;
    align-items: center;
    justify-content: space-around;
    height: 100%;
    width: 100%;
    font-family: 'Outfit', 'Inter', -apple-system, sans-serif;
    color: #f3f4f6;
    padding: 16px;
    box-sizing: border-box;
    background: transparent;
  }
  .kpi-left {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .gauge-wrapper {
    position: relative;
    width: 220px;
    height: 220px;
  }
  .progress-ring {
    transform: rotate(-90deg);
  }
  .progress-ring__circle {
    transition: stroke-dashoffset 0.8s ease-in-out;
  }
  .gauge-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    display: flex;
    flex-direction: column;
  }
  #oee-val {
    font-size: 38px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #ffffff;
    text-shadow: 0 0 10px rgba(0, 242, 254, 0.4);
  }
  .gauge-label {
    font-size: 11px;
    font-weight: 600;
    color: #9ca3af;
    letter-spacing: 1px;
    margin-top: 4px;
  }
  .kpi-right {
    flex: 1.2;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 20px;
    padding-right: 20px;
  }
  .bar-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .bar-header {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #d1d5db;
  }
  .bar-bg {
    height: 10px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 5px;
    overflow: hidden;
    position: relative;
  }
  .bar-fill {
    height: 100%;
    border-radius: 5px;
    width: 0%;
    transition: width 0.8s ease-in-out;
    box-shadow: 0 0 8px rgba(255,255,255,0.1);
  }
</style>

<div class="kpi-container">
  <div class="kpi-left">
    <div class="gauge-wrapper">
      <svg class="progress-ring" width="220" height="220">
        <circle class="progress-ring__background" stroke="rgba(255,255,255,0.05)" stroke-width="16" fill="transparent" r="90" cx="110" cy="110"/>
        <circle class="progress-ring__circle" id="oee-ring" stroke="url(#oee-gradient-high)" stroke-width="16" stroke-linecap="round" fill="transparent" r="90" cx="110" cy="110" stroke-dasharray="565.49" stroke-dashoffset="565.49"/>
        <defs>
          <linearGradient id="oee-gradient-low" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#f857a6" />
            <stop offset="100%" stop-color="#ff5858" />
          </linearGradient>
          <linearGradient id="oee-gradient-med" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#f2994a" />
            <stop offset="100%" stop-color="#f2c94c" />
          </linearGradient>
          <linearGradient id="oee-gradient-high" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#11998e" />
            <stop offset="100%" stop-color="#38ef7d" />
          </linearGradient>
        </defs>
      </svg>
      <div class="gauge-text">
        <span id="oee-val">--%</span>
        <span class="gauge-label">OEE GLOBAL</span>
      </div>
    </div>
  </div>
  <div class="kpi-right">
    <div class="bar-group">
      <div class="bar-header">
        <span>DISPONIBILIDAD</span>
        <span id="avail-val">--%</span>
      </div>
      <div class="bar-bg">
        <div class="bar-fill" id="avail-bar" style="width: 0%; background: linear-gradient(90deg, #11998e, #38ef7d);"></div>
      </div>
    </div>
    <div class="bar-group">
      <div class="bar-header">
        <span>RENDIMIENTO</span>
        <span id="perf-val">--%</span>
      </div>
      <div class="bar-bg">
        <div class="bar-fill" id="perf-bar" style="width: 0%; background: linear-gradient(90deg, #f2994a, #f2c94c);"></div>
      </div>
    </div>
    <div class="bar-group">
      <div class="bar-header">
        <span>CALIDAD</span>
        <span id="qual-val">--%</span>
      </div>
      <div class="bar-bg">
        <div class="bar-fill" id="qual-bar" style="width: 0%; background: linear-gradient(90deg, #f857a6, #ff5858);"></div>
      </div>
    </div>
  </div>
</div>

<script>
(function() {
  var API_BASE = window.location.origin + '/api';
  var oeeRing = document.getElementById('oee-ring');
  var oeeVal = document.getElementById('oee-val');
  var availVal = document.getElementById('avail-val');
  var availBar = document.getElementById('avail-bar');
  var perfVal = document.getElementById('perf-val');
  var perfBar = document.getElementById('perf-bar');
  var qualVal = document.getElementById('qual-val');
  var qualBar = document.getElementById('qual-bar');
  
  var circumference = 565.49;

  function setProgress(percent) {
    if (!oeeRing) return;
    var offset = circumference - (percent / 100 * circumference);
    oeeRing.style.strokeDashoffset = offset;
  }

  function updateKPIs() {
    var xhr = new XMLHttpRequest();
    var sqlPayload = JSON.stringify({
      queries: [{
        datasource: {type: 'mssql', uid: 'mes_sqlserver'},
        rawSql: "SELECT TOP 1 oee, availability, performance, quality FROM mes_oee_snapshots WHERE machine_id = 'MAQ-01' AND oee IS NOT NULL ORDER BY ts DESC",
        refId: 'A', format: 'table'
      }]
    });
    xhr.open('POST', API_BASE + '/ds/query', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
      if (xhr.status !== 200) return;
      try {
        var data = JSON.parse(xhr.responseText);
        var frames = data.results && data.results.A && data.results.A.frames;
        if (frames && frames.length > 0) {
          var fields = frames[0].schema.fields;
          var vals = frames[0].data.values;
          var row = {};
          for (var fi = 0; fi < fields.length; fi++) {
            row[fields[fi].name] = vals[fi][0];
          }
          
          var oee = Math.round((row.oee || 0) * 10) / 10;
          var avail = Math.round((row.availability || 0) * 10) / 10;
          var perf = Math.round((row.performance || 0) * 10) / 10;
          var qual = Math.round((row.quality || 0) * 10) / 10;

          if (oeeVal) oeeVal.textContent = oee + '%';
          setProgress(oee);

          if (oeeRing && oeeVal) {
            if (oee < 65) {
              oeeRing.setAttribute('stroke', 'url(#oee-gradient-low)');
              oeeVal.style.textShadow = '0 0 10px rgba(255, 88, 88, 0.4)';
            } else if (oee < 85) {
              oeeRing.setAttribute('stroke', 'url(#oee-gradient-med)');
              oeeVal.style.textShadow = '0 0 10px rgba(242, 201, 76, 0.4)';
            } else {
              oeeRing.setAttribute('stroke', 'url(#oee-gradient-high)');
              oeeVal.style.textShadow = '0 0 10px rgba(56, 239, 125, 0.4)';
            }
          }

          if (availVal && availBar) {
            availVal.textContent = avail + '%';
            availBar.style.width = avail + '%';
          }
          if (perfVal && perfBar) {
            perfVal.textContent = perf + '%';
            perfBar.style.width = perf + '%';
          }
          if (qualVal && qualBar) {
            qualVal.textContent = qual + '%';
            qualBar.style.width = qual + '%';
          }
        }
      } catch(e) { console.error('Error parsing OEE response:', e); }
    };
    xhr.send(sqlPayload);
  }

  updateKPIs();
  setInterval(updateKPIs, 5000);
})();
</script>"""

# HTML content for Panel 2 (TURNO) - larger layout, three column cards including OBJETIVO TEÓRICO: 800, removed OK/NOK ratio progress bar
panel_2_content = """<style>
  .turno-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    font-family: 'Outfit', 'Inter', -apple-system, sans-serif;
    color: #f3f4f6;
    padding: 16px;
    box-sizing: border-box;
    background: transparent;
    justify-content: space-between;
  }
  .turno-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 8px;
    margin-bottom: 12px;
  }
  .turno-title {
    font-size: 18px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 0.5px;
  }
  .turno-times {
    font-size: 13px;
    font-weight: 600;
    color: #9ca3af;
    background: rgba(255, 255, 255, 0.05);
    padding: 4px 10px;
    border-radius: 4px;
  }
  .turno-content {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    justify-content: space-between;
    gap: 12px;
  }
  .pieces-row {
    display: flex;
    gap: 12px;
  }
  .piece-card {
    flex: 1;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 8px;
    padding: 10px 12px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .card-target {
    border-left: 3px solid #00f2fe;
  }
  .card-ok {
    border-left: 3px solid #2fd06a;
  }
  .card-nok {
    border-left: 3px solid #e32636;
  }
  .piece-label {
    font-size: 10px;
    font-weight: 700;
    color: #9ca3af;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
  }
  .piece-value {
    font-size: 22px;
    font-weight: 800;
    color: #ffffff;
  }
  .card-target .piece-value {
    color: #00f2fe;
    text-shadow: 0 0 10px rgba(0, 242, 254, 0.2);
  }
  .card-ok .piece-value {
    color: #2fd06a;
    text-shadow: 0 0 10px rgba(47, 208, 106, 0.2);
  }
  .card-nok .piece-value {
    color: #e32636;
    text-shadow: 0 0 10px rgba(227, 38, 54, 0.2);
  }
  .durations-section {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .dur-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .dur-header {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #d1d5db;
  }
  .dur-value {
    color: #9ca3af;
    font-weight: 600;
  }
  .dur-bg {
    height: 8px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
    overflow: hidden;
  }
  .dur-bar {
    height: 100%;
    border-radius: 4px;
    width: 0%;
    transition: width 0.8s ease-in-out;
  }
  .bar-marcha {
    background: linear-gradient(90deg, #11998e, #38ef7d);
  }
  .bar-parada {
    background: linear-gradient(90deg, #2b5876, #4e4376);
  }
  .bar-error {
    background: linear-gradient(90deg, #f857a6, #ff5858);
  }
</style>

<div class="turno-container">
  <div class="turno-header">
    <span class="turno-title">Turno <span id="shift-label">--</span></span>
    <span class="turno-times" id="shift-times">Inicio: --:-- | Fin: --:--</span>
  </div>

  <div class="turno-content">
    <div class="pieces-row">
      <div class="piece-card card-target">
        <span class="piece-label">OBJETIVO TEÓRICO</span>
        <span class="piece-value" id="target-val">800</span>
      </div>
      <div class="piece-card card-ok">
        <span class="piece-label">PIEZAS OK</span>
        <span class="piece-value" id="ok-val">0</span>
      </div>
      <div class="piece-card card-nok">
        <span class="piece-label">PIEZAS NOK</span>
        <span class="piece-value" id="nok-val">0</span>
      </div>
    </div>

    <div class="durations-section">
      <div class="dur-group">
        <div class="dur-header">
          <span>TIEMPO EN MARCHA</span>
          <span class="dur-value" id="marcha-val">0h 00m (0%)</span>
        </div>
        <div class="dur-bg">
          <div class="dur-bar bar-marcha" id="marcha-bar" style="width: 0%"></div>
        </div>
      </div>

      <div class="dur-group">
        <div class="dur-header">
          <span>TIEMPO PARADA</span>
          <span class="dur-value" id="parada-val">0h 00m (0%)</span>
        </div>
        <div class="dur-bg">
          <div class="dur-bar bar-parada" id="parada-bar" style="width: 0%"></div>
        </div>
      </div>

      <div class="dur-group">
        <div class="dur-header">
          <span>TIEMPO ERROR</span>
          <span class="dur-value" id="error-val">0h 00m (0%)</span>
        </div>
        <div class="dur-bg">
          <div class="dur-bar bar-error" id="error-bar" style="width: 0%"></div>
        </div>
      </div>
    </div>
  </div>
</div>

<script>
(function() {
  var API_BASE = window.location.origin + '/api';
  
  var shiftLabel = document.getElementById('shift-label');
  var shiftTimes = document.getElementById('shift-times');
  var okVal = document.getElementById('ok-val');
  var nokVal = document.getElementById('nok-val');
  
  var marchaVal = document.getElementById('marcha-val');
  var marchaBar = document.getElementById('marcha-bar');
  var paradaVal = document.getElementById('parada-val');
  var paradaBar = document.getElementById('parada-bar');
  var errorVal = document.getElementById('error-val');
  var errorBar = document.getElementById('error-bar');

  function formatDuration(seconds) {
    var h = Math.floor(seconds / 3600);
    var m = Math.floor((seconds % 3600) / 60);
    return h + 'h ' + (m < 10 ? '0' : '') + m + 'm';
  }

  function updateTurno() {
    var xhr = new XMLHttpRequest();
    var sqlPayload = JSON.stringify({
      queries: [{
        datasource: {type: 'mssql', uid: 'mes_sqlserver'},
        rawSql: "DECLARE @latest_ts DATETIME; DECLARE @shift_label VARCHAR(10); DECLARE @shift_start DATETIME; DECLARE @shift_end DATETIME; DECLARE @total_pieces INT; DECLARE @good_pieces INT; SELECT TOP 1 @latest_ts = ts, @shift_label = shift_label, @total_pieces = total_pieces, @good_pieces = good_pieces FROM mes_oee_snapshots WHERE machine_id = 'MAQ-01' AND oee IS NOT NULL ORDER BY ts DESC; IF @shift_label = 'T1' BEGIN SET @shift_start = DATEADD(hour, 7, CAST(CAST(@latest_ts AS DATE) AS DATETIME)); SET @shift_end = DATEADD(hour, 15, CAST(CAST(@latest_ts AS DATE) AS DATETIME)); END ELSE IF @shift_label = 'T2' BEGIN SET @shift_start = DATEADD(hour, 15, CAST(CAST(@latest_ts AS DATE) AS DATETIME)); SET @shift_end = DATEADD(hour, 23, CAST(CAST(@latest_ts AS DATE) AS DATETIME)); END ELSE IF @shift_label = 'T3' BEGIN IF DATEPART(hour, @latest_ts) < 7 BEGIN SET @shift_start = DATEADD(hour, 23, CAST(CAST(DATEADD(day, -1, @latest_ts) AS DATE) AS DATETIME)); SET @shift_end = DATEADD(hour, 7, CAST(CAST(@latest_ts AS DATE) AS DATETIME)); END ELSE BEGIN SET @shift_start = DATEADD(hour, 23, CAST(CAST(@latest_ts AS DATE) AS DATETIME)); SET @shift_end = DATEADD(hour, 7, CAST(CAST(DATEADD(day, 1, @latest_ts) AS DATE) AS DATETIME)); END END; WITH EventDurations AS ( SELECT state, timestamp, LEAD(timestamp) OVER (ORDER BY timestamp) AS next_timestamp FROM dbo.mes_machine_events WHERE machine_id = 'MAQ-01' AND timestamp >= @shift_start AND timestamp <= @shift_end ), AggregatedDurations AS ( SELECT SUM(CASE WHEN state = 'Running' THEN DATEDIFF(second, timestamp, CASE WHEN next_timestamp IS NULL OR next_timestamp > @shift_end THEN @shift_end ELSE next_timestamp END) ELSE 0 END) AS duration_running, SUM(CASE WHEN state IN ('Stopped', 'Setup', 'Break') THEN DATEDIFF(second, timestamp, CASE WHEN next_timestamp IS NULL OR next_timestamp > @shift_end THEN @shift_end ELSE next_timestamp END) ELSE 0 END) AS duration_stopped, SUM(CASE WHEN state IN ('Micro-stop', 'Disconnected') THEN DATEDIFF(second, timestamp, CASE WHEN next_timestamp IS NULL OR next_timestamp > @shift_end THEN @shift_end ELSE next_timestamp END) ELSE 0 END) AS duration_error FROM EventDurations ) SELECT @shift_label AS shift_label, CONVERT(VARCHAR(5), @shift_start, 108) AS shift_start, CONVERT(VARCHAR(5), @shift_end, 108) AS shift_end, @total_pieces AS total_pieces, @good_pieces AS good_pieces, (@total_pieces - @good_pieces) AS bad_pieces, COALESCE(duration_running, 0) AS duration_running, COALESCE(duration_stopped, 0) AS duration_stopped, COALESCE(duration_error, 0) AS duration_error FROM AggregatedDurations;",
        refId: 'A', format: 'table'
      }]
    });
    xhr.open('POST', API_BASE + '/ds/query', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
      if (xhr.status !== 200) return;
      try {
        var data = JSON.parse(xhr.responseText);
        var frames = data.results && data.results.A && data.results.A.frames;
        if (frames && frames.length > 0) {
          var fields = frames[0].schema.fields;
          var vals = frames[0].data.values;
          var row = {};
          for (var fi = 0; fi < fields.length; fi++) {
            row[fields[fi].name] = vals[fi][0];
          }
          
          if (shiftLabel) shiftLabel.textContent = row.shift_label || '--';
          if (shiftTimes) shiftTimes.textContent = 'Inicio: ' + (row.shift_start || '--:--') + ' | Fin: ' + (row.shift_end || '--:--');
          
          var ok = row.good_pieces || 0;
          var nok = row.bad_pieces || 0;

          if (okVal) okVal.textContent = ok;
          if (nokVal) nokVal.textContent = nok;

          var running = row.duration_running || 0;
          var stopped = row.duration_stopped || 0;
          var error = row.duration_error || 0;
          var totalDur = running + stopped + error;

          if (totalDur === 0) totalDur = 28800;

          var runPct = Math.round((running / totalDur) * 100);
          var stopPct = Math.round((stopped / totalDur) * 100);
          var errPct = Math.round((error / totalDur) * 100);

          if (marchaVal && marchaBar) {
            marchaVal.textContent = formatDuration(running) + ' (' + runPct + '%)';
            marchaBar.style.width = runPct + '%';
          }
          if (paradaVal && paradaBar) {
            paradaVal.textContent = formatDuration(stopped) + ' (' + stopPct + '%)';
            paradaBar.style.width = stopPct + '%';
          }
          if (errorVal && errorBar) {
            errorVal.textContent = formatDuration(error) + ' (' + errPct + '%)';
            errorBar.style.width = errPct + '%';
          }
        }
      } catch(e) { console.error('Error parsing Turno response:', e); }
    };
    xhr.send(sqlPayload);
  }

  updateTurno();
  setInterval(updateTurno, 5000);
})();
</script>"""

# Load local dashboard JSON
with open(filepath, 'r', encoding='utf-8') as f:
    dashboard_data = json.load(f)

# Update positions and contents of Panels
for panel in dashboard_data.get('panels', []):
    pid = panel.get('id')
    # Panel 1: OEE y KPIs
    if pid == 1:
        panel['gridPos'] = {"h": 12, "w": 14, "x": 0, "y": 0}
        panel['options']['content'] = panel_1_content
        print("Updated Panel 1 layout and content.")
    
    # Panel 2: TURNO
    elif pid == 2:
        panel['gridPos'] = {"h": 12, "w": 10, "x": 14, "y": 0}
        panel['options']['content'] = panel_2_content
        print("Updated Panel 2 layout and content.")
    
    # Panel 5: State Timeline
    elif pid == 5:
        panel['gridPos']['y'] = 12
        print("Updated Panel 5 grid position.")
        
    # Panel 10: Top 5 Stop Reasons
    elif pid == 10:
        panel['gridPos']['y'] = 20
        print("Updated Panel 10 grid position.")
        
    # Panel 11: MTBF
    elif pid == 11:
        panel['gridPos']['y'] = 20
        print("Updated Panel 11 grid position.")
        
    # Panel 13: Top 5 Reject Reasons
    elif pid == 13:
        panel['gridPos']['y'] = 20
        print("Updated Panel 13 grid position.")
        
    # Panel 12: MTTR
    elif pid == 12:
        panel['gridPos']['y'] = 24
        print("Updated Panel 12 grid position.")

# Save modified local file
with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
print("Successfully saved updated JSON to local provisioning file.")

# Prepare API payload (remove ID/Version or just keep them for overwrite)
dashboard_to_push = dict(dashboard_data)
dashboard_to_push.pop("id", None)
dashboard_to_push["version"] = None

payload = {
    "dashboard": dashboard_to_push,
    "overwrite": True,
    "message": "Enlarge OEE & Turno panels, add theoretical target, and remove OK/NOK ratio progress bar."
}

# Post to Grafana API
data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(
    f"{GRAFANA_URL}/api/dashboards/db",
    data=data, headers=headers, method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print(f"Dashboard pushed to Grafana. Status: {result.get('status')}")
        
        # Fetch the latest live version to sync back local ID/Version
        req_get = urllib.request.Request(f"{GRAFANA_URL}/api/dashboards/uid/panel-oee-mes-fabrica", headers=headers)
        with urllib.request.urlopen(req_get) as resp_get:
            existing = json.loads(resp_get.read().decode("utf-8"))
            final_dashboard = existing["dashboard"]
            
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(final_dashboard, f, indent=2, ensure_ascii=False)
        print("Successfully synchronized local file with the live dashboard.")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode()}")
