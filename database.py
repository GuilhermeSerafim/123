"""
Configuração do Banco de Dados PostgreSQL
"""
import os
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

# URL do banco de dados
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://unificador_de_emergencia_user:sxAXTa8xXZlMMOcZFrET0LlNukpcgguk@dpg-d3upgkjipnbc7394ohvg-a.oregon-postgres.render.com/unificador_de_emergencia"
)

# Criar engine do SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Modelo de Chamada
class Call(Base):
    __tablename__ = "calls"
    
    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    transcript = Column(Text)
    category = Column(String, index=True)
    confidence = Column(Integer)
    urgency_level = Column(String, nullable=True)
    reasoning = Column(Text)
    region = Column(String, nullable=True, index=True)


# Criar todas as tabelas
def init_db():
    """Inicializa o banco de dados criando todas as tabelas"""
    Base.metadata.create_all(bind=engine)


# Função para obter sessão do banco
def get_db():
    """Retorna uma sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Função para testar conexão
def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        with engine.connect() as connection:
            print("✅ Conexão com banco de dados estabelecida com sucesso!")
            return True
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return False


if __name__ == "__main__":
    # Testar conexão e criar tabelas
    if test_connection():
        print("🔧 Criando tabelas no banco de dados...")
        init_db()
        print("✅ Tabelas criadas com sucesso!")
