# Grafana MCP Server

Este es un servidor MCP (Model Context Protocol) diseñado para interactuar con la API de Grafana. Permite a los Modelos de Lenguaje (LLMs) como Claude o Cursor consultar, editar, actualizar paneles y dashboards de Grafana, así como ejecutar consultas directas (SQL/Prometheus/etc.) a través de los datasources configurados.

## Requisitos

- **Python 3.11+**
- El entorno virtual de Python actual ya tiene instalados los paquetes `mcp` y `fastmcp`.
- Grafana ejecutándose (por ejemplo, en `http://localhost:3010` o el puerto correspondiente en tu entorno).

## Configuración y Variables de Entorno

El servidor lee las siguientes variables de entorno o usa sus valores por defecto (configurados para apuntar a tu contenedor de Grafana local y usando el token proporcionado):

- `GRAFANA_URL`: URL base de Grafana. Por defecto `http://localhost:3010`.
- `GRAFANA_TOKEN`: Token de cuenta de servicio de Grafana. Debe configurarse como variable de entorno (ver ejemplo en `.env`).

Ambas variables se pueden configurar en el archivo `.env` dentro de la carpeta `grafana-mcp` o directamente en las variables de sistema.

## Herramientas Disponibles (Tools)

El servidor MCP expone las siguientes herramientas:

1. **`get_health`**: Verifica la conectividad y el estado de salud de Grafana.
2. **`list_dashboards`**: Lista todos los dashboards y carpetas en Grafana (soporta filtros por nombre, tag y tipo).
3. **`get_dashboard`**: Obtiene la estructura JSON completa de un dashboard por su UID.
4. **`save_dashboard`**: Crea o actualiza un dashboard enviando un modelo JSON.
5. **`delete_dashboard`**: Elimina un dashboard por su UID.
6. **`list_datasources`**: Muestra la lista de todos los orígenes de datos (datasources) conectados.
7. **`query_sql_datasource`**: Ejecuta una consulta SQL nativa en un datasource de base de datos (como SQL Server) y devuelve los resultados formateados limpiamente como una lista de filas/objetos JSON.
8. **`query_datasource_raw`**: Permite enviar una consulta JSON nativa libre a la API `/api/ds/query` de Grafana (útil para Prometheus, Loki, etc.).
9. **`get_panel`**: Extrae la configuración JSON de un panel específico de un dashboard a partir del UID del dashboard y el ID del panel.
10. **`update_panel`**: Modifica la configuración de un panel específico, fusiona los cambios indicados en JSON y guarda el dashboard automáticamente en Grafana.

---

## Cómo Integrarlo en tus Clientes MCP

### 1. Claude Desktop (Windows)

Para añadir este servidor MCP a Claude Desktop, debes editar el archivo de configuración `claude_desktop_config.json`.
Si el archivo o su directorio no existen, créalos en la siguiente ruta:
`%APPDATA%\Claude\claude_desktop_config.json` (que habitualmente se traduce a `C:\Users\<TuUsuario>\AppData\Roaming\Claude\claude_desktop_config.json`).

Agrega la siguiente sección bajo `"mcpServers"`:

```json
{
  "mcpServers": {
    "grafana-mcp": {
      "command": "python",
      "args": [
        "-u",
        "c:/Users/franj/OneDrive/Escritorio/COSAS  FRAN/PROYECTOS/JAULA ELEVACION/APLICACION MES-OEE/grafana-mcp/server.py"
      ],
      "env": {
        "GRAFANA_URL": "http://localhost:3010",
        "GRAFANA_TOKEN": "<TU_TOKEN_GRAFANA_AQUI>"
      }
    }
  }
}
```

*Nota: Asegúrate de reiniciar Claude Desktop tras guardar el archivo.*

### 2. Cursor (Editor de Código)

Para configurarlo en Cursor:
1. Ve a **Settings (Configuración) -> Features (Características) -> MCP**.
2. Haz clic en **+ Add New MCP Server** (Añadir nuevo servidor MCP).
3. Configura los siguientes campos:
   - **Name**: `grafana-mcp`
   - **Type**: `command`
   - **Command**: `python -u "c:/Users/franj/OneDrive/Escritorio/COSAS  FRAN/PROYECTOS/JAULA ELEVACION/APLICACION MES-OEE/grafana-mcp/server.py"`
4. Haz clic en **Save** y asegúrate de que el estado figure como conectado (un círculo verde).

### 3. Ejecución Manual y Desarrollo

Puedes correr e inspeccionar el servidor desde tu terminal local usando las herramientas de `fastmcp`:

```bash
# Para verificar la lista de herramientas detectadas y su formato
fastmcp inspect grafana-mcp/server.py

# Para levantar un inspector visual interactivo (abre un panel en el navegador)
fastmcp dev grafana-mcp/server.py

# Para iniciar el servidor directamente en modo STDIO
fastmcp run grafana-mcp/server.py
```
