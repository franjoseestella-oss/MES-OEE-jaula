# Instrucciones para Subagente 1: Módulo de Base de Datos (SQL Server)

## Contexto del Proyecto
Este subagente se encarga de la administración, optimización y actualización del esquema de base de datos **MSSQL** que soporta la aplicación MES-OEE.

* **Servidor**: `DESKTOP-PMRMSPT\SQLEXPRESS` (puerto `1435`)
* **Base de Datos**: `DAFEED`
* **Tablas Principales**:
  * `LOG_TABLA`: Contiene el histórico de pruebas de la jaula de elevación (`OK_NOK`, tiempos de elevación/descenso, modelo, bastidor, operario, etc.).
  * `calendario_trabajo` (u homóloga): Estructura del calendario de producción 2026.
* **Usuario de Conexión**: `usuario_readonly` (solo lectura para histórico) y credenciales administrativas si es necesario.

## Tareas Típicas a Realizar
1. **Calendarios y Turnos**: Modificar o insertar el calendario laboral del año correspondiente en la base de datos.
2. **Optimización de Consultas**: Crear índices o reestructurar consultas complejas para mejorar el rendimiento de los dashboards de Grafana.
3. **Vistas e Históricos**: Diseñar vistas para agregar datos de producción diarios/mensuales para los reportes de OEE.

## Instrucción para Iniciar la Conversación
> "Hola. Eres el agente encargado de la base de datos SQL Server para el proyecto de elevación de jaulas. Tu objetivo es optimizar y preparar los esquemas, tablas y procedimientos en SQL Server de acuerdo a los requerimientos de datos. Revisa la tabla `LOG_TABLA` y prepárate para optimizar o añadir la información que te solicite."
