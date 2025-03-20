from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

Base = declarative_base()

class Jugador(Base):
    __tablename__ = 'jugadores_campeones'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    pais = Column(String(100), nullable=False)
    ano = Column(Integer, nullable=False)
    posicion = Column(String(50), nullable=False)
    equipo = Column(String(100), nullable=False)

# Conectar con la base de datos
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
