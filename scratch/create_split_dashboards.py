import json
import os

def main():
    dashboard_dir = 'grafana/provisioning/dashboards'
    
    # 1. Load log_dashboard.json (currently containing everything)
    log_path = os.path.join(dashboard_dir, 'log_dashboard.json')
    with open(log_path, 'r', encoding='utf-8') as f:
        log_dashboard = json.load(f)
        
    print("Loaded log_dashboard.json")
    
    # Define navigation links for OEE, LOG_SECUENCIAS, and REGISTRO
    nav_links = [
        {
            "asDropdown": False,
            "icon": "home",
            "includeVars": False,
            "keepTime": False,
            "tags": [],
            "targetBlank": False,
            "title": "Inicio",
            "type": "link",
            "url": "/d/mes-home-v1"
        },
        {
            "asDropdown": False,
            "icon": "dashboard",
            "includeVars": True,
            "keepTime": True,
            "tags": [],
            "targetBlank": False,
            "title": "OEE/MES",
            "type": "link",
            "url": "/d/mes-oee-v1"
        },
        {
            "asDropdown": False,
            "icon": "dashboard",
            "includeVars": True,
            "keepTime": True,
            "tags": [],
            "targetBlank": False,
            "title": "LOG_SECUENCIAS",
            "type": "link",
            "url": "/d/mes-log-v1"
        },
        {
            "asDropdown": False,
            "icon": "dashboard",
            "includeVars": True,
            "keepTime": True,
            "tags": [],
            "targetBlank": False,
            "title": "REGISTRO",
            "type": "link",
            "url": "/d/mes-reg-v1"
        }
    ]
    
    # 2. Extract panels for the REGISTRO dashboard (ID 9 and 16)
    reg_panels = [p for p in log_dashboard['panels'] if p.get('id') in (9, 16)]
    
    # Remove these panels from the LOG_SECUENCIAS dashboard
    seq_panels = [p for p in log_dashboard['panels'] if p.get('id') not in (9, 16)]
    
    # Update LOG_SECUENCIAS dashboard
    log_dashboard['panels'] = seq_panels
    log_dashboard['title'] = "LOGISNEXT — LOG_SECUENCIAS"
    log_dashboard['uid'] = "mes-log-v1"
    log_dashboard['links'] = nav_links
    log_dashboard.pop('id', None)
    log_dashboard['version'] = None
    
    # Write back LOG_SECUENCIAS dashboard
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_dashboard, f, indent=2, ensure_ascii=False)
    print("Updated LOGISNEXT — LOG_SECUENCIAS dashboard.")
    
    # 3. Create the REGISTRO dashboard
    import copy
    reg_dashboard = copy.deepcopy(log_dashboard)
    reg_dashboard['title'] = "LOGISNEXT — REGISTRO"
    reg_dashboard['uid'] = "mes-reg-v1"
    reg_dashboard['links'] = nav_links
    
    # Adjust panels position to top of dashboard y=0
    for p in reg_panels:
        if p.get('id') == 9:
            p['gridPos'] = {"h": 20, "w": 12, "x": 0, "y": 0}
        elif p.get('id') == 16:
            p['gridPos'] = {"h": 20, "w": 12, "x": 12, "y": 0}
            
    reg_dashboard['panels'] = reg_panels
    reg_dashboard.pop('id', None)
    reg_dashboard['version'] = None
    
    reg_path = os.path.join(dashboard_dir, 'registro_dashboard.json')
    with open(reg_path, 'w', encoding='utf-8') as f:
        json.dump(reg_dashboard, f, indent=2, ensure_ascii=False)
    print("Created LOGISNEXT — REGISTRO dashboard.")
    
    # 4. Load & Update OEE/MES dashboard
    oee_path = os.path.join(dashboard_dir, 'oee_dashboard.json')
    if os.path.exists(oee_path):
        with open(oee_path, 'r', encoding='utf-8') as f:
            oee_dashboard = json.load(f)
        oee_dashboard['title'] = "LOGISNEXT — MES / OEE"
        oee_dashboard['uid'] = "mes-oee-v1"
        oee_dashboard['links'] = nav_links
        oee_dashboard.pop('id', None)
        oee_dashboard['version'] = None
        with open(oee_path, 'w', encoding='utf-8') as f:
            json.dump(oee_dashboard, f, indent=2, ensure_ascii=False)
        print("Updated LOGISNEXT — MES / OEE dashboard.")
    
    # 5. Create INICIO (Home) dashboard
    home_dashboard = copy.deepcopy(log_dashboard)
    home_dashboard['title'] = "LOGISNEXT — INICIO"
    home_dashboard['uid'] = "mes-home-v1"
    # Home has no top nav links or maybe only Inicio itself to be clean
    home_dashboard['links'] = [] 
    home_dashboard['templating'] = {"list": []}
    
    home_html = """<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; min-height: 480px; font-family: 'Inter', -apple-system, sans-serif; background: radial-gradient(circle at 50% 50%, #1a1d24 0%, #0e1014 100%); padding: 40px; border-radius: 8px; border: 1px solid #2d3139;">
  <h1 style="color: #ffffff; font-size: 2.6rem; font-weight: 700; margin-bottom: 8px; letter-spacing: 0.5px; text-shadow: 0 4px 10px rgba(0,0,0,0.5);">SISTEMA MES — JAULA DE ELEVACIÓN</h1>
  <p style="color: #8e96a5; font-size: 1.1rem; margin-bottom: 48px; text-align: center; max-width: 600px;">Seleccione uno de los módulos principales para acceder al panel correspondiente.</p>
  
  <div style="display: flex; gap: 32px; width: 100%; max-width: 800px; justify-content: center;">
    <a href="/d/mes-oee-v1" style="flex: 1; max-width: 360px; text-decoration: none;">
      <div style="background: linear-gradient(135deg, rgba(37, 201, 214, 0.08) 0%, rgba(37, 201, 214, 0.03) 100%); border: 1px solid rgba(37, 201, 214, 0.35); border-radius: 12px; padding: 48px 32px; text-align: center; cursor: pointer; transition: all 0.25s ease-in-out; box-shadow: 0 4px 20px rgba(0,0,0,0.25);"
           onmouseover="this.style.transform='translateY(-5px)'; this.style.borderColor='rgba(37, 201, 214, 0.8)'; this.style.boxShadow='0 10px 25px rgba(37, 201, 214, 0.2)';" 
           onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='rgba(37, 201, 214, 0.35)'; this.style.boxShadow='0 4px 20px rgba(0,0,0,0.25)';">
        <div style="font-size: 3.5rem; margin-bottom: 24px; color: #25C9D6;">📊</div>
        <h2 style="color: #ffffff; font-size: 1.6rem; font-weight: 600; margin: 0 0 12px 0;">OEE / MES</h2>
        <p style="color: #a2aab7; font-size: 0.95rem; margin: 0; line-height: 1.45;">Indicadores OEE en tiempo real, tasas de disponibilidad, rendimiento, calidad y estado de máquina.</p>
      </div>
    </a>
    
    <a href="/d/mes-log-v1" style="flex: 1; max-width: 360px; text-decoration: none;">
      <div style="background: linear-gradient(135deg, rgba(47, 208, 106, 0.08) 0%, rgba(47, 208, 106, 0.03) 100%); border: 1px solid rgba(47, 208, 106, 0.35); border-radius: 12px; padding: 48px 32px; text-align: center; cursor: pointer; transition: all 0.25s ease-in-out; box-shadow: 0 4px 20px rgba(0,0,0,0.25);"
           onmouseover="this.style.transform='translateY(-5px)'; this.style.borderColor='rgba(47, 208, 106, 0.8)'; this.style.boxShadow='0 10px 25px rgba(47, 208, 106, 0.2)';" 
           onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='rgba(47, 208, 106, 0.35)'; this.style.boxShadow='0 4px 20px rgba(0,0,0,0.25)';">
        <div style="font-size: 3.5rem; margin-bottom: 24px; color: #2FD06A;">⚙️</div>
        <h2 style="color: #ffffff; font-size: 1.6rem; font-weight: 600; margin: 0 0 12px 0;">LOG SECUENCIAS</h2>
        <p style="color: #a2aab7; font-size: 0.95rem; margin: 0; line-height: 1.45;">Historial de pruebas, tiempos y márgenes de elevación y descenso con detalle por modelo.</p>
      </div>
    </a>
  </div>
</div>"""

    home_dashboard['panels'] = [
        {
            "gridPos": {
                "h": 22,
                "w": 24,
                "x": 0,
                "y": 0
            },
            "id": 1,
            "options": {
                "content": home_html,
                "mode": "html"
            },
            "title": "",
            "type": "text"
        }
    ]
    
    home_path = os.path.join(dashboard_dir, 'home_dashboard.json')
    with open(home_path, 'w', encoding='utf-8') as f:
        json.dump(home_dashboard, f, indent=2, ensure_ascii=False)
    print("Created LOGISNEXT — INICIO dashboard.")

if __name__ == '__main__':
    main()
