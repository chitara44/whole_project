from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DECIMAL

# Configuración de la conexión a la base de datos
DATABASE_URL = "postgresql://postgres:R1c4rd1t0%@localhost:5432/miloto"

# Crear el motor de conexión
engine = create_engine(DATABASE_URL)

# MetaData para almacenar información de las tablas
metadata = MetaData()

# Definición de la tabla 'sorteos'
sorteos_table = Table(
    'sorteos',
    metadata,
    Column('IdSorteo', Integer, primary_key=True, autoincrement=True),
    Column('FechaSorteo', String, nullable=False),
    Column('Ganador', String, nullable=True),
    Column('Nuevo', String, nullable=True),  # Opcional: "Y" o "N"
    Column('N1', Integer, nullable=False),
    Column('N2', Integer, nullable=False),
    Column('N3', Integer, nullable=False),
    Column('N4', Integer, nullable=False),
    Column('N5', Integer, nullable=False) 
)

# Definición de la tabla 'resultados_comparacion'
resultados_comparacion_table = Table(
    'resultados_comparacion',
    metadata,
    Column('IdSorteo', Integer, primary_key=True),
    Column('Numeros_Sorteo', String, nullable=False),  # Ejemplo: "5, 12, 23, 34, 45"
    Column('Numeros_Prospecto', String, nullable=False),  # Ejemplo: "4, 11, 22, 33, 44"
    Column('Aciertos', Integer, nullable=False),  # Número total de aciertos
    Column('Numeros_Acertados', String, nullable=True)  # Ejemplo: "5, 12"
)

# Definición de la tabla 'resultados_comparacion'
prospectos = Table(
    'prospectos',
    metadata,
    Column('IdSorteo', Integer, primary_key=True),
    Column('Posicion', Integer, primary_key=True),   # Ejemplo: Incremental Numerico
    Column('TipoSorteo', String, primary_key=True),  # Ejemplo: 'Tr' o 'Re'
    Column('TipoProspecto', String, primary_key=True),  # Ejemplo: "Mediana, Fusion, Promedio"
    Column('N1', Integer, nullable=False),  # Número 1
    Column('N2', Integer, nullable=False),  # Número 2
    Column('N3', Integer, nullable=False),  # Número 3
    Column('N4', Integer, nullable=False),  # Número 4
    Column('N5', Integer, nullable=False),  # Número 5
    Column('Peso', DECIMAL(10, 8), nullable=True),  # Precisión: 10 dígitos en total, 8 después del punto decimal
)


# Crear las tablas en la base de datos
def crear_tablas():
    metadata.create_all(engine)
    print("Tablas creadas exitosamente en la base de datos.")

# Ejecutar la función para crear las tablas
if __name__ == "__main__":
    crear_tablas()