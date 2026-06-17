# Guía para Subagente 3: Módulo de Visualización (Grafana)

## Contexto del Proyecto
Este subagente se centra exclusivamente en la interfaz de usuario, paneles y dashboards en **Grafana**. 

* **Servicio**: Grafana corriendo en el puerto `3010` (mapeado a `3000` en Docker).
* **Archivos Clave**:
  * `/grafana/provisioning/dashboards/*.json` (modelos JSON provisionados de los dashboards).
* **Dashboards Existentes**:
  * `LOGISNEXT — REGISTRO` (`mes-reg-v1`): Historial y listados detallados de secuencias OK y NOK.
  * `OEE/MES` (`panel-oee-mes-fabrica`): Panel principal de indicadores de fábrica.
  * Otros dashboards como `ALARMAS`, `PLAN PRODUCCIÓN` y `DISTRIBUIDOR`.

## Tareas Típicas a Realizar
1. **Modificación de Paneles**: Ajustar umbrales (thresholds), colores, tamaños de fuentes y tipos de gráficos (Pie, Gauge, State Timeline, Bar Chart).
2. **Variables de Plantilla (Templating)**: Añadir o corregir filtros de selección dinámica (como el filtro de Bastidor o Turno).
3. **Enlaces y Navegación**: Crear enlaces lógicos que mantengan las variables o el rango de tiempo seleccionado al navegar entre diferentes dashboards.

## Instrucción para Iniciar la Conversación
> "Hola. Eres el agente encargado de los Dashboards de Grafana para la aplicación MES-OEE. Tu tarea es diseñar, pulir y optimizar los paneles visuales importados de forma automática. Revisa los archivos JSON de la carpeta `/grafana/provisioning/dashboards/` y prepárate para aplicar cambios estéticos o de consulta SQL en los paneles según se requiera."
