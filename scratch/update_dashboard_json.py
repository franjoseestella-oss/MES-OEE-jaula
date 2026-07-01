import json

dashboard_path = r"c:\Users\franj\OneDrive\Escritorio\COSAS  FRAN\PROYECTOS\JAULA ELEVACION\APLICACION MES-OEE\grafana\provisioning\dashboards\turno_actual_dashboard.json"

with open(dashboard_path, "r", encoding="utf-8-sig") as f:
    dashboard = json.load(f)

# Find the panel with id 1
updated = False
for panel in dashboard.get("panels", []):
    if panel.get("id") == 1:
        new_content = """<style>
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
    color: #fff;
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
    box-shadow: 0 0 8px rgba(255, 255, 255, 0.1);
  }
</style>
<div class="kpi-container">
  <div class="kpi-left">
    <div class="gauge-wrapper">
      <svg class="progress-ring" width="220" height="220">
        <circle class="progress-ring__background" stroke="rgba(255,255,255,0.05)" stroke-width="16" fill="transparent"
          r="90" cx="110" cy="110" />
        <circle class="progress-ring__circle" id="oee-ring" stroke="url(#oee-gradient-high)" stroke-width="16"
          stroke-linecap="round" fill="transparent" r="90" cx="110" cy="110" stroke-dasharray="565.49"
          stroke-dashoffset="565.49" />
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
      <div class="gauge-text"><span id="oee-val">--%</span><span class="gauge-label">OEE GLOBAL</span></div>
    </div>
  </div>
  <div class="kpi-right">
    <div class="bar-group">
      <div class="bar-header"><span>DISPONIBILIDAD</span><span id="avail-val">--%</span></div>
      <div class="bar-bg">
        <div class="bar-fill" id="avail-bar" style="width:0%;background:linear-gradient(90deg,#11998e,#38ef7d);"></div>
      </div>
    </div>
    <div class="bar-group">
      <div class="bar-header"><span>RENDIMIENTO</span><span id="perf-val">--%</span></div>
      <div class="bar-bg">
        <div class="bar-fill" id="perf-bar" style="width:0%;background:linear-gradient(90deg,#f2994a,#f2c94c);"></div>
      </div>
    </div>
    <div class="bar-group">
      <div class="bar-header"><span>CALIDAD</span><span id="qual-val">--%</span></div>
      <div class="bar-bg">
        <div class="bar-fill" id="qual-bar" style="background:linear-gradient(90deg,#f857a6,#ff5858); width:0%;"></div>
      </div>
    </div>
  </div>
</div>
<script>
(function(){
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

  function setProgress(p) {
    if (!oeeRing) return;
    oeeRing.style.strokeDashoffset = circumference - (p / 100 * circumference);
  }

  function updateKPIs() {
    var xhr = new XMLHttpRequest();
    var sql = JSON.stringify({
      queries: [{
        datasource: { type: 'mssql', uid: 'mes_sqlserver' },
        rawSql: "SELECT TOP 1 oee, availability, performance, quality FROM mes_oee_snapshots WHERE machine_id='JAULA-01' AND oee IS NOT NULL ORDER BY ts DESC",
        refId: 'A',
        format: 'table'
      }]
    });
    xhr.open('POST', API_BASE + '/ds/query', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
      if (xhr.status !== 200) return;
      try {
        var d = JSON.parse(xhr.responseText);
        var f = d.results && d.results.A && d.results.A.frames;
        if (f && f.length > 0) {
          var fld = f[0].schema.fields;
          var v = f[0].data.values;
          var r = {};
          for (var i = 0; i < fld.length; i++) {
            r[fld[i].name] = v[i];
          }
          var getVal = function(name) {
            var valArr = r[name];
            if (valArr && valArr.length > 0) {
              return valArr[0];
            }
            return null;
          };
          var rawOee = getVal('oee');
          var rawAvail = getVal('availability');
          var rawPerf = getVal('performance');
          var rawQual = getVal('quality');

          var oee = rawOee !== null ? Math.round(rawOee * 1000) / 10 : 0;
          var av = rawAvail !== null ? Math.round(rawAvail * 1000) / 10 : 0;
          var pf = rawPerf !== null ? Math.round(rawPerf * 1000) / 10 : 0;
          var ql = rawQual !== null ? Math.round(rawQual * 1000) / 10 : 0;

          if (oeeVal) oeeVal.textContent = oee + '%';
          setProgress(oee);

          if (oeeRing && oeeVal) {
            if (oee < 65) {
              oeeRing.setAttribute('stroke', 'url(#oee-gradient-low)');
              oeeVal.style.textShadow = '0 0 10px rgba(255,88,88,0.4)';
            } else if (oee < 85) {
              oeeRing.setAttribute('stroke', 'url(#oee-gradient-med)');
              oeeVal.style.textShadow = '0 0 10px rgba(242,201,76,0.4)';
            } else {
              oeeRing.setAttribute('stroke', 'url(#oee-gradient-high)');
              oeeVal.style.textShadow = '0 0 10px rgba(56,239,125,0.4)';
            }
          }

          if (availVal && availBar) {
            availVal.textContent = av + '%';
            availBar.style.width = av + '%';
          }
          if (perfVal && perfBar) {
            perfVal.textContent = pf + '%';
            perfBar.style.width = pf + '%';
          }
          if (qualVal && qualBar) {
            qualVal.textContent = ql + '%';
            qualBar.style.width = ql + '%';
          }
        }
      } catch (e) {
        console.error(e);
      }
    };
    xhr.send(sql);
  }

  updateKPIs();
  setInterval(updateKPIs, 5000);
})();
</script>"""
        panel["options"]["content"] = new_content
        updated = True

def update_machine_id_recursively(panels):
    updated_any = False
    for panel in panels:
        if "targets" in panel:
            for target in panel["targets"]:
                if "rawSql" in target and "MAQ-01" in target["rawSql"]:
                    target["rawSql"] = target["rawSql"].replace("MAQ-01", "JAULA-01")
                    updated_any = True
        if "panels" in panel:
            if update_machine_id_recursively(panel["panels"]):
                updated_any = True
    return updated_any

sql_updated = update_machine_id_recursively(dashboard.get("panels", []))

if updated or sql_updated:
    with open(dashboard_path, "w", encoding="utf-8-sig") as f:
        json.dump(dashboard, f, indent=4, ensure_ascii=False)
    print("Success: Local dashboard JSON has been updated.")
else:
    print("Error: No updates were made to the local dashboard JSON.")

