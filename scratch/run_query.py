import os
import sys
from dotenv import load_dotenv

# Add backend directory to path to use backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from config import get_settings
from sqlalchemy import create_engine, text

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))
settings = get_settings()

engine = create_engine(settings.sqlalchemy_url)

query = """
SELECT *
FROM dbo.REFERENCIA_EN_CICLO;
"""

with engine.connect() as conn:
    result = conn.execute(text(query))
    columns = result.keys()
    for row in result:
        print(dict(zip(columns, row)))
