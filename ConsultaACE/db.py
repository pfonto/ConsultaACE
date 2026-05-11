from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings

class OracleConfig(BaseSettings):
    model_config = {"env_prefix": "ORACLE_"}
    
    # Defaults para desarrollo
    user: str = "IIBUSR"
    password: str = "Iibusr#826"
    dsn: str = "(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=VDW-FidelidadAIX.gdisco)(PORT=1521))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=IIB)))"
    
    @property
    def connection_url(self) -> str:
        # Formato: oracle+oracledb://user:password@host:port/?service_name=service
        # Nota: Ajustar según necesidad de DSN vs Host/Port
        return f"oracle+oracledb://{self.user}:{self.password}@vdw-fidelidadaix.gdisco:1521/?service_name=IIB"

cfg = OracleConfig()
engine = create_engine(cfg.connection_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
