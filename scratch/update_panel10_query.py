import json
import os

def main():
    dashboard_path = r'grafana/provisioning/dashboards/plan_dashboard.json'
    if not os.path.exists(dashboard_path):
        print(f"File not found: {dashboard_path}")
        return

    with open(dashboard_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find Panel 10
    panel_10 = None
    for panel in data.get('panels', []):
        if panel.get('id') == 10:
            panel_10 = panel
            break
    
    if not panel_10:
        print("Panel 10 not found!")
        return

    raw_sql = panel_10['targets'][0]['rawSql']
    print("Original rawSql snippet:")
    print("..." + raw_sql[-1000:] + "\n")

    target_segment = (
        "WHEN (s.actual_end IS NULL OR ft.t < s.actual_end)\n"
        "                 AND EXISTS (\n"
        "                     SELECT 1 FROM AlarmIntervals a \n"
        "                     WHERE ft.t >= a.alarm_start AND ft.t < a.alarm_end\n"
        "                 ) THEN 'Alarma'"
    )
    
    replacement_segment = (
        "WHEN s.actual_start IS NOT NULL AND ft.t >= s.actual_start AND (s.actual_end IS NULL OR ft.t < s.actual_end)\n"
        "                 AND EXISTS (\n"
        "                     SELECT 1 FROM AlarmIntervals a \n"
        "                     WHERE ft.t >= a.alarm_start AND ft.t < a.alarm_end\n"
        "                 ) THEN 'Alarma'"
    )

    if target_segment in raw_sql:
        print("Found target segment!")
        new_sql = raw_sql.replace(target_segment, replacement_segment)
        panel_10['targets'][0]['rawSql'] = new_sql
        
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Saved updated dashboard JSON successfully.")
    else:
        print("Target segment NOT found in rawSql. Maybe it is already modified?")
        # Let's search for some substrings to see what is there
        if "AlarmIntervals" in raw_sql:
            print("AlarmIntervals is present. Let's print the WHEN conditions around it:")
            lines = raw_sql.split('\n')
            for i, line in enumerate(lines):
                if "AlarmIntervals" in line:
                    start_idx = max(0, i - 4)
                    end_idx = min(len(lines), i + 6)
                    print(f"Context lines {start_idx} to {end_idx}:")
                    for j in range(start_idx, end_idx):
                        print(f"{j}: {lines[j]}")

if __name__ == '__main__':
    main()
