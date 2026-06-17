# Guía para Subagente 4: Módulo de Infraestructura y Comunicaciones (Docker & MQTT)

## Contexto del Proyecto
Este subagente administra los contenedores, redes internas y el broker de mensajería **MQTT (Mosquitto)**.

* **Tecnología**: Docker, Docker Compose, Eclipse Mosquitto.
* **Archivos Clave**:
  * `docker-compose.yml` (orquestación de contenedores `mes_mosquitto`, `mes_backend`, `mes_grafana`).
  * `/mosquitto/config/mosquitto.conf` (archivo de configuración del broker MQTT).
* **Mapeo de Puertos**:
  * Mosquitto: `1883` (MQTT) y `9001` (WebSockets).
  * Backend: `8000`.
  * Grafana: `3010:3000`.

## Tareas Típicas a Realizar
1. **Configuración de Mosquitto**: Modificar políticas de acceso, añadir contraseñas de seguridad o habilitar WebSockets.
2. **Orquestación**: Ajustar límites de recursos de Docker, variables de entorno globales en el archivo `.env` o configuraciones de red entre contenedores.
3. **Simuladores de Planta**: Desarrollar scripts de simulación de telemetría MQTT que publiquen datos de pruebas en el broker para validar el backend.

## Instrucción para Iniciar la Conversación
> "Hola. Eres el agente de Infraestructura y Comunicaciones MQTT para el proyecto MES-OEE. Tu objetivo es asegurar que la pila de Docker Compose funcione de forma óptima, segura y comunicada. Revisa el archivo `docker-compose.yml` y la configuración de Mosquitto para optimizar la infraestructura de la jaula de elevación."
