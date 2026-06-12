import os
import json
import httpx
from typing import Optional, Dict, Any, List
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server named "grafana"
mcp = FastMCP("grafana")

# Configuration (defaults to Docker setup and the user's provided token)
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3010").rstrip("/")
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN", "")

headers = {
    "Authorization": f"Bearer {GRAFANA_TOKEN}",
    "Content-Type": "application/json"
}

@mcp.tool()
async def get_health() -> str:
    """
    Check the health of the Grafana server.
    """
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{GRAFANA_URL}/api/health")
            if r.status_code == 200:
                return f"Grafana is healthy. Response: {r.text}"
            return f"Grafana returned health error: {r.status_code} - {r.text}"
    except Exception as e:
        return f"Failed to connect to Grafana at {GRAFANA_URL}: {e}"

@mcp.tool()
async def list_dashboards(query: Optional[str] = None, tag: Optional[str] = None, type: Optional[str] = None) -> str:
    """
    List all dashboards and folders in Grafana.
    
    Args:
        query: Optional search term to filter dashboards/folders by title.
        tag: Optional tag to filter dashboards.
        type: Optional type to filter (e.g., 'dash-db' for dashboards, 'dash-folder' for folders).
    """
    params = {}
    if query:
        params["query"] = query
    if tag:
        params["tag"] = tag
    if type:
        params["type"] = type
        
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{GRAFANA_URL}/api/search", headers=headers, params=params)
            if r.status_code != 200:
                return f"Error listing dashboards: {r.status_code} - {r.text}"
            return json.dumps(r.json(), indent=2)
    except Exception as e:
        return f"Exception occurred while listing dashboards: {e}"

@mcp.tool()
async def get_dashboard(uid: str) -> str:
    """
    Retrieve the full dashboard JSON structure by its unique identifier (UID).
    
    Args:
        uid: The unique identifier (UID) of the dashboard (e.g., 'mes-oee-v1').
    """
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", headers=headers)
            if r.status_code != 200:
                return f"Error retrieving dashboard {uid}: {r.status_code} - {r.text}"
            return json.dumps(r.json(), indent=2)
    except Exception as e:
        return f"Exception occurred while retrieving dashboard {uid}: {e}"

@mcp.tool()
async def save_dashboard(dashboard_json: str, folder_uid: Optional[str] = None, message: Optional[str] = None) -> str:
    """
    Create or update a dashboard in Grafana.
    
    Args:
        dashboard_json: The complete dashboard JSON model as a string.
        folder_uid: Optional UID of the folder to place the dashboard in.
        message: Optional commit/change message describing the update.
    """
    try:
        db_data = json.loads(dashboard_json)
    except Exception as e:
        return f"Error: Invalid JSON format for dashboard_json: {e}"
        
    if isinstance(db_data, dict):
        if "dashboard" in db_data:
            payload = db_data
        else:
            payload = {
                "dashboard": db_data,
                "overwrite": True
            }
    else:
        return "Error: Dashboard JSON must be an object/dict"
        
    if folder_uid:
        payload["folderUid"] = folder_uid
    if message:
        payload["message"] = message
        
    if "overwrite" not in payload:
        payload["overwrite"] = True
        
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{GRAFANA_URL}/api/dashboards/db", headers=headers, json=payload)
            if r.status_code != 200:
                return f"Error saving dashboard: {r.status_code} - {r.text}"
            return json.dumps(r.json(), indent=2)
    except Exception as e:
        return f"Exception occurred while saving dashboard: {e}"

@mcp.tool()
async def delete_dashboard(uid: str) -> str:
    """
    Delete a dashboard by its UID.
    
    Args:
        uid: The unique identifier (UID) of the dashboard.
    """
    try:
        async with httpx.AsyncClient() as client:
            r = await client.delete(f"{GRAFANA_URL}/api/dashboards/uid/{uid}", headers=headers)
            if r.status_code != 200:
                return f"Error deleting dashboard {uid}: {r.status_code} - {r.text}"
            return json.dumps(r.json(), indent=2)
    except Exception as e:
        return f"Exception occurred while deleting dashboard {uid}: {e}"

@mcp.tool()
async def list_datasources() -> str:
    """
    List all configured data sources in Grafana.
    """
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{GRAFANA_URL}/api/datasources", headers=headers)
            if r.status_code != 200:
                return f"Error listing data sources: {r.status_code} - {r.text}"
            return json.dumps(r.json(), indent=2)
    except Exception as e:
        return f"Exception occurred while listing data sources: {e}"

@mcp.tool()
async def query_sql_datasource(
    datasource_uid: str,
    query: str,
    from_time: str = "now-24h",
    to_time: str = "now"
) -> str:
    """
    Execute a raw SQL query on a specific SQL database datasource in Grafana and return the results as a clean list of rows.
    
    Args:
        datasource_uid: The UID of the database datasource (e.g., 'mes_sqlserver').
        query: The raw SQL query to run.
        from_time: Optional start time for the time range (default 'now-24h').
        to_time: Optional end time for the time range (default 'now').
    """
    payload = {
        "queries": [
            {
                "refId": "A",
                "datasource": {
                    "uid": datasource_uid
                },
                "rawSql": query,
                "format": "table"
            }
        ],
        "from": from_time,
        "to": to_time
    }
    
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{GRAFANA_URL}/api/ds/query", headers=headers, json=payload)
            if r.status_code != 200:
                return f"Error executing query: {r.status_code} - {r.text}"
            
            res_json = r.json()
            results = res_json.get("results", {})
            parsed_results = {}
            
            for ref_id, result in results.items():
                frames = result.get("frames", [])
                parsed_frames = []
                for frame in frames:
                    fields = frame.get("schema", {}).get("fields", [])
                    data_values = frame.get("data", {}).get("values", [])
                    if not fields or not data_values:
                        continue
                    
                    col_names = [f.get("name") for f in fields]
                    rows = []
                    num_rows = len(data_values[0]) if data_values else 0
                    for r_idx in range(num_rows):
                        row = {}
                        for c_idx, name in enumerate(col_names):
                            val = data_values[c_idx][r_idx]
                            row[name] = val
                        rows.append(row)
                    parsed_frames.append({
                        "query_executed": frame.get("schema", {}).get("meta", {}).get("executedQueryString"),
                        "rows": rows
                    })
                parsed_results[ref_id] = parsed_frames
                
            return json.dumps(parsed_results, indent=2)
            
    except Exception as e:
        return f"Exception occurred while executing SQL query: {e}"

@mcp.tool()
async def query_datasource_raw(payload_json: str) -> str:
    """
    Execute a raw/custom query on Grafana's /api/ds/query endpoint. 
    Use this for non-SQL queries (like Prometheus or Loki) or advanced multi-query requests.
    
    Args:
        payload_json: The complete raw JSON payload string required by Grafana's query endpoint.
    """
    try:
        data = json.loads(payload_json)
    except Exception as e:
        return f"Error: Invalid JSON format for payload_json: {e}"
        
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{GRAFANA_URL}/api/ds/query", headers=headers, json=data)
            if r.status_code != 200:
                return f"Error executing raw query: {r.status_code} - {r.text}"
            return json.dumps(r.json(), indent=2)
    except Exception as e:
        return f"Exception occurred while executing raw query: {e}"

@mcp.tool()
async def get_panel(dashboard_uid: str, panel_id: int) -> str:
    """
    Retrieve the configuration of a specific panel in a dashboard by dashboard UID and panel ID.
    
    Args:
        dashboard_uid: The UID of the dashboard.
        panel_id: The ID of the panel.
    """
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{GRAFANA_URL}/api/dashboards/uid/{dashboard_uid}", headers=headers)
            if r.status_code != 200:
                return f"Error retrieving dashboard {dashboard_uid}: {r.status_code} - {r.text}"
            
            db_data = r.json()
            dashboard = db_data.get("dashboard", {})
            panels = dashboard.get("panels", [])
            
            def find_panel(panels_list, pid):
                for p in panels_list:
                    if p.get("id") == pid:
                        return p
                    if "panels" in p:
                        found = find_panel(p["panels"], pid)
                        if found:
                            return found
                return None
                
            panel = find_panel(panels, panel_id)
            if not panel:
                return f"Panel {panel_id} not found in dashboard {dashboard_uid}."
                
            return json.dumps(panel, indent=2)
    except Exception as e:
        return f"Exception occurred while retrieving panel {panel_id}: {e}"

@mcp.tool()
async def update_panel(dashboard_uid: str, panel_id: int, panel_updates_json: str, commit_message: Optional[str] = None) -> str:
    """
    Modify a specific panel's configuration in a dashboard. 
    This retrieves the dashboard, updates the panel JSON with the provided changes, and saves the dashboard back.
    
    Args:
        dashboard_uid: The UID of the dashboard.
        panel_id: The ID of the panel to update.
        panel_updates_json: A JSON string containing the fields and values to update/merge into the panel.
        commit_message: Optional description of the changes made.
    """
    try:
        updates = json.loads(panel_updates_json)
    except Exception as e:
        return f"Error: Invalid JSON format for panel_updates_json: {e}"
        
    try:
        async with httpx.AsyncClient() as client:
            # 1. Fetch existing dashboard
            r = await client.get(f"{GRAFANA_URL}/api/dashboards/uid/{dashboard_uid}", headers=headers)
            if r.status_code != 200:
                return f"Error fetching dashboard {dashboard_uid}: {r.status_code} - {r.text}"
                
            db_data = r.json()
            dashboard = db_data.get("dashboard", {})
            meta = db_data.get("meta", {})
            folder_uid = meta.get("folderUid", "")
            panels = dashboard.get("panels", [])
            
            # 2. Find and update the panel recursively
            def update_panel_recursive(panels_list, pid, updates_dict):
                for i, p in enumerate(panels_list):
                    if p.get("id") == pid:
                        # Merge updates_dict into p
                        for k, v in updates_dict.items():
                            if isinstance(v, dict) and k in p and isinstance(p[k], dict):
                                p[k].update(v)
                            else:
                                p[k] = v
                        return True
                    if "panels" in p:
                        if update_panel_recursive(p["panels"], pid, updates_dict):
                            return True
                return False
                
            success = update_panel_recursive(panels, panel_id, updates)
            if not success:
                return f"Panel {panel_id} not found in dashboard {dashboard_uid}."
                
            # 3. Save dashboard back
            save_payload = {
                "dashboard": dashboard,
                "overwrite": True
            }
            if folder_uid:
                save_payload["folderUid"] = folder_uid
            if commit_message:
                save_payload["message"] = commit_message
            else:
                save_payload["message"] = f"Update panel {panel_id} via MCP server"
                
            r_save = await client.post(f"{GRAFANA_URL}/api/dashboards/db", headers=headers, json=save_payload)
            if r_save.status_code != 200:
                return f"Error saving dashboard after panel update: {r_save.status_code} - {r_save.text}"
                
            return f"Panel {panel_id} in dashboard {dashboard_uid} updated successfully. Save result:\n{r_save.text}"
    except Exception as e:
        return f"Exception occurred while updating panel {panel_id}: {e}"

if __name__ == "__main__":
    mcp.run()
