from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # SQL Server — servidor real: DESKTOP-PMRMSPT\SQLEXPRESS  |  BD: DAFEED
    sql_server_host: str = r"DESKTOP-PMRMSPT\SQLEXPRESS"
    sql_server_port: int = 1433
    sql_server_database: str = "DAFEED"
    sql_server_user: str = "sa"
    sql_server_password: str = ""
    sql_server_driver: str = "ODBC Driver 18 for SQL Server"
    sql_server_trust_cert: str = "yes"

    # Tabla histórica de App 1 (solo lectura)
    app1_log_table: str = "dbo.LOG_TABLA"

    # MQTT
    mqtt_broker_host: str = "mosquitto"
    mqtt_broker_port: int = 1883
    mqtt_client_id: str = "mes_oee_backend"
    mqtt_username: str = ""
    mqtt_password: str = ""
    mqtt_topic_prefix: str = "planta/linea1/MAQ-01"

    # OEE
    ideal_cycle_time_seconds: float = 30.0
    shift_duration_hours: float = 8.0
    oee_snapshot_interval_seconds: int = 60

    # Backend
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    # Claude
    anthropic_api_key: str = ""

    # Grafana
    gf_security_admin_user: str = "admin"
    gf_security_admin_password: str = "admin123"

    @property
    def sqlalchemy_url(self) -> str:
        trust = "yes" if self.sql_server_trust_cert.lower() == "yes" else "no"
        conn = (
            f"mssql+pyodbc://{self.sql_server_user}:{self.sql_server_password}"
            f"@{self.sql_server_host}:{self.sql_server_port}/{self.sql_server_database}"
            f"?driver={self.sql_server_driver.replace(' ', '+')}"
            f"&TrustServerCertificate={trust}"
        )
        return conn

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
