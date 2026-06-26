import sys
import os
from sqlalchemy import text
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from database.session import get_db

with get_db() as db:
    query = """
    DECLARE @ActiveDate VARCHAR(8);
    SET @ActiveDate = CONVERT(varchar(8), CAST(GETDATE() AS DATE), 112);

    IF NOT EXISTS (SELECT 1 FROM JAULA_ERP WHERE fecha_montaje = @ActiveDate)
    BEGIN
        SET @ActiveDate = COALESCE(
            (SELECT TOP 1 CONVERT(varchar(8), FECHA_MONTAJE, 112) FROM LOG_TABLA WHERE TRY_CAST(FECHA_HORA_INICIO_SEC AS DATE) = CAST(GETDATE() AS DATE) ORDER BY id DESC),
            (SELECT MIN(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje >= @ActiveDate),
            (SELECT MAX(fecha_montaje) FROM JAULA_ERP WHERE fecha_montaje <= @ActiveDate),
            (SELECT MAX(fecha_montaje) FROM JAULA_ERP)
        );
    END;

    SELECT @ActiveDate AS ActiveDate;
    """
    res = db.execute(text(query)).scalar()
    print("Resolved ActiveDate:", res)
