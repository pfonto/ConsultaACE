from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

class Aplicacion(Base):
    __tablename__ = "APLICACIONES"
    
    IdApp = Column("IDAPP", Integer, primary_key=True)
    App = Column("APP", String(50), unique=True)
    VersionActual = Column("VERSIONACTUAL", String(20))
    DescApp = Column("DESCAPP", String(255))
    DescDato1 = Column("DESCDATO1", String(50))
    DescDato2 = Column("DESCDATO2", String(50))
    DescDato3 = Column("DESCDATO3", String(50))
    
    eventos = relationship("Evento", back_populates="aplicacion")

class Version(Base):
    __tablename__ = "VERSIONES"
    
    IdApp = Column("IDAPP", Integer, ForeignKey("APLICACIONES.IDAPP"), primary_key=True)
    Version = Column("VERSION", String(20), primary_key=True)
    FechaHora = Column("FECHAHORA", TIMESTAMP)
    DesplegadoPor = Column("DESPLEGADOPOR", String(40))

class Evento(Base):
    __tablename__ = "EVENTOS"
    
    IdEvento = Column("IDEVENTO", Integer, primary_key=True)
    IdApp = Column("IDAPP", Integer, ForeignKey("APLICACIONES.IDAPP"))
    Version = Column("VERSION", String(20))
    FechaHora = Column("FECHAHORA", TIMESTAMP)
    Dato1 = Column("DATO1", String(100))
    Dato2 = Column("DATO2", String(100))
    Dato3 = Column("DATO3", String(100))
    
    aplicacion = relationship("Aplicacion", back_populates="eventos")
    detalles = relationship("EventoDetalle", back_populates="evento")

class EventoDetalle(Base):
    __tablename__ = "EVENTOSDETALLES"
    
    IdEvento = Column("IDEVENTO", Integer, ForeignKey("EVENTOS.IDEVENTO"), primary_key=True)
    DescDato = Column("DESCDATO", String(50), primary_key=True)
    Dato = Column("DATO", String(300))
    
    evento = relationship("Evento", back_populates="detalles")
