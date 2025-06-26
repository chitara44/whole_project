from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd

# Configurar la conexión a la base de datos PostgreSQL
DATABASE_URL = "postgresql+psycopg2://usuario:R1c4rd1t0%@localhost:5432/sorteos_baloto"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Definir el modelo de la tabla Sorteos
class Sorteo(Base):
    __tablename__ = 'sorteos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_sorteo = Column(Integer, nullable=False, unique=True)
    n1 = Column(Integer, nullable=False)
    n2 = Column(Integer, nullable=False)
    n3 = Column(Integer, nullable=False)
    n4 = Column(Integer, nullable=False)
    n5 = Column(Integer, nullable=False)
    sb = Column(Integer)  # Campo opcional para "super balota"

# Crear las tablas en la base de datos
Base.metadata.create_all(engine)

# Funciones para interactuar con la base de datos

def agregar_sorteo(datos_sorteo):
    """Agregar un sorteo a la base de datos."""
    nuevo_sorteo = Sorteo(**datos_sorteo)
    session.add(nuevo_sorteo)
    session.commit()


def obtener_sorteos():
    """Obtener todos los sorteos de la base de datos."""
    sorteos = session.query(Sorteo).all()
    return pd.DataFrame([{col.name: getattr(sorteo, col.name) for col in Sorteo.__table__.columns} for sorteo in sorteos])


def actualizar_sorteo(numero_sorteo, nuevos_datos):
    """Actualizar los datos de un sorteo existente."""
    sorteo = session.query(Sorteo).filter(Sorteo.numero_sorteo == numero_sorteo).first()
    if sorteo:
        for key, value in nuevos_datos.items():
            setattr(sorteo, key, value)
        session.commit()


def eliminar_sorteo(numero_sorteo):
    """Eliminar un sorteo de la base de datos."""
    sorteo = session.query(Sorteo).filter(Sorteo.numero_sorteo == numero_sorteo).first()
    if sorteo:
        session.delete(sorteo)
        session.commit()

# Ejemplo de uso
if __name__ == "__main__":
    # Agregar un sorteo
    agregar_sorteo({
        "numero_sorteo": 12345,
        "n1": 5,
        "n2": 12,
        "n3": 23,
        "n4": 34,
        "n5": 45,
        "sb": 7
    })

    # Obtener todos los sorteos y mostrarlos
    sorteos = obtener_sorteos()
    print(sorteos)

    # Actualizar un sorteo
    actualizar_sorteo(12345, {"n1": 10, "n2": 15})

    # Eliminar un sorteo
    eliminar_sorteo(12345)
