import pandas as pd
import numpy as np
import csv
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from datetime import datetime


# Configuración de la base de datos
DB_HOST = "localhost"
DB_NAME = "baloto"
DB_USER = "postgres"
DB_PASSWORD = "R1c4rd1t0%"
DB_PORT = "5432"

class Baloto:

    def __init__(self ):
        self.initial = None
        self.final = None
        self.prospect_initial = None
        self.input_file = None
        self.all_drafts = []
        self.connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        self.engine = create_engine(self.connection_string, connect_args={"client_encoding": "utf8"}) 

    def set_initial_values(self, initial, final, initial_prospect):
        self.initial = initial
        self.final = final
        self.prospect_initial = initial_prospect
        # self.input_file = input_file

    # Crear conexión a la base de datos
    # def get_db_connection(self):
    #     connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    #     return    

    # Leer datos desde la base de datos
    def leer_datos_from_db(self, tipo_sorteo=None):
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            # Llamar a la función en lugar del procedimiento
            query = "SELECT * FROM leer_sorteos_fn(:tipo_sorteo);"
            result = session.execute(text(query), 
                {
                    "tipo_sorteo": tipo_sorteo
                }
            )
            # Convertir los resultados a un DataFrame
            columns = ["IdSorteo", "FechaSorteo", "TipoSorteo", "Ganador", "Nuevo", "N1", "N2", "N3", "N4", "N5", "SB"]
            data = result.fetchall()
            session.commit()

            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            session.rollback()
            print(f"Error al cargar datos: {e}")
            return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error
        finally:
            session.close()



    def leer_prospectos_from_db(self, id_sorteo, tipo_sorteo=None):
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            # Llamar a la función en lugar del procedimiento
            query = "SELECT * FROM leer_prospectos_fn(:id_sorteo, :tipo_sorteo);"
            result = session.execute(
                text(query), 
                {
                    "id_sorteo": id_sorteo,
                    "tipo_sorteo": tipo_sorteo
                }
            )
            # Convertir los resultados a un DataFrame
            columns = ["IdSorteo", "Posicion", "TipoSorteo", "TipoProspecto", 
                       "N1", "N2", "N3", "N4", "N5", "SB", "Peso"]
            data = result.fetchall()
            session.commit()

            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            session.rollback()
            print(f"Error al cargar datos: {e}")
            return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error
        finally:
            session.close()



    # Leer datos desde la base de datos
    def leer_resultados_comparacion_from_db(self, tipo_sorteo=None):
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            # Llamar a la función en lugar del procedimiento
            query = "SELECT * FROM leer_resultados_comparacion_fn(:tipo_sorteo);"
            result = session.execute(
                text(query), 
                {"tipo_sorteo": tipo_sorteo}
            )
            # Convertir los resultados a un DataFrame
            columns = ["IdSorteo", "TipoSorteo", "Numeros_Sorteo", 
                       "Numeros_Prospecto", "Aciertos", 
                       "Numeros_Acertados", "Numero_Superbalota", 
                       "Superbalota_Acertada"]
            data = result.fetchall()
            session.commit()

            return pd.DataFrame(data, columns=columns)
        except Exception as e:
            session.rollback()
            print(f"Error al cargar datos: {e}")
            return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error
        finally:
            session.close()



    # Función para insertar registros desde un archivo CSV
    def insertar_comparaciones_from_csv(self, tabla_destino, batch_size=500):
        # Leer el archivo CSV en un DataFrame
        df = pd.read_csv(
            self.input_file, 
            header=None, 
            names=['IdSorteo', 'TipoSorteo', 'Numeros_Sorteo', 
                   'Numeros_Prospecto', 'Aciertos', 
                   'Numeros_Acertados', 'Numero_Superbalota', 
                   'Superbalota_Acertada']
        )

        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            filas = []
            for _, row in df.iterrows():
                filas.append({
                    "IdSorteo": int(row["IdSorteo"]),
                    "TipoSorteo": row["TipoSorteo"],
                    "Numeros_Sorteo": row["Numeros_Sorteo"],
                    "Numeros_Prospecto": row["Numeros_Prospecto"],
                    "Aciertos": int(row["Aciertos"]),
                    "Numeros_Acertados": row["Numeros_Acertados"],
                    "Numero_Superbalota": int(row["Numero_Superbalota"]) if pd.notna(row["Numero_Superbalota"]) else None,
                    "Superbalota_Acertada": row["Superbalota_Acertada"]
                })

                # Insertar en batch
                if len(filas) == batch_size:
                    self._insertar_batch(session, filas, tabla_destino)
                    filas.clear()

            # Insertar las filas restantes
            if filas:
                self._insertar_batch(session, filas, tabla_destino)

            session.commit()
            print(f"Registros insertados correctamente en {tabla_destino}")
        except Exception as e:
            session.rollback()
            print(f"Error al insertar registros: {e}")
        finally:
            session.close()

    def _insertar_batch(self, session, filas, tabla_destino):
        # Convertir las filas a JSON para enviar al SP
        json_data = json.dumps(filas)
        session.execute(
            text("CALL insertar_comparaciones_batch(:json_data);"),
            {"json_data": json_data}
        )

    def insertar_comparaciones_calculadas(self, datos):
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            superbalota_acertada = str(bool(datos.get("Superbalota_Acertada", [False])[0])).lower()
            
            session.execute(
                text("""
                    CALL insertar_comparaciones_calculadas(
                        :IdSorteo, :TipoSorteo, :Numeros_Sorteo, 
                        :Numeros_Prospecto, :Aciertos, 
                        :Numeros_Acertados, :Numero_Superbalota, 
                        :Superbalota_Acertada
                    )
                """),
                {
                    "IdSorteo": int(datos["IdSorteo"][0]),
                    "TipoSorteo": datos.get("Tipo_Sorteo", [""])[0],
                    "Numeros_Sorteo": datos["Numeros_Sorteo"][0],
                    "Numeros_Prospecto": datos["Numeros_Prospecto"][0],
                    "Aciertos": int(datos["Aciertos"][0]),
                    "Numeros_Acertados": datos["Numeros_Acertados"][0],
                    "Numero_Superbalota": int(datos.get("Numero_Superbalota", ["0"])[0]),
                    "Superbalota_Acertada": superbalota_acertada  # Convertido a 'true' o 'false'
                }
            )
            session.commit()
            print(f"Registro {datos['IdSorteo'][0]} comparaciones insertadas correctamente.")
        except Exception as e:
            session.rollback()
            print(f"Error al insertar registro: {e}")
        finally:
            session.close()

    
    def insertar_prospectos_en_db(self, initial, final, base_path="./"):
        Session = sessionmaker(bind=self.engine)
        session = Session()

        tipos_sorteo = ['Tr', 'Re']
        tipos_prospecto = ['Promedio', 'Fusión', 'Mediana']

        for id_sorteo in range(initial, final):
            for tipo_sorteo in tipos_sorteo:
                for tipo_prospecto in tipos_prospecto:
                    filename = f"{base_path}prospectos_{id_sorteo}_{tipo_sorteo}_{tipo_prospecto}.csv"
                    try:
                        with open(filename, mode='r') as file:
                            reader = csv.DictReader(file)
                            records = []

                            for fila, row in enumerate(reader, start=1):
                                records.append((
                                    id_sorteo, fila, tipo_sorteo, tipo_prospecto,
                                    int(row['N1']),
                                    int(row['N2']),
                                    int(row['N3']),
                                    int(row['N4']),
                                    int(row['N5']),
                                    int(row['SB']) if row['SB'] else None,
                                    float(row['Peso']) if row['Peso'] else None
                                ))

                            if records:
                                values_str = ", ".join( str(record) for record in records )
                                
                                query = f"""
                                INSERT INTO public.prospectos 
                                ("IdSorteo", "Posicion", "TipoSorteo", "TipoProspecto",
                                 "N1", "N2", "N3", "N4", "N5", "SB", "Peso")
                                VALUES {values_str}
                                ON CONFLICT ("IdSorteo", "Posicion", "TipoSorteo", "TipoProspecto") 
                                DO NOTHING;
                                """
                                session.execute(text(query))
                        session.commit()
                        print(f"Archivo procesado: {filename}")
                    except FileNotFoundError:
                        print(f"Archivo no encontrado: {filename}")
                    except Exception as e:
                        session.rollback()
                        print(f"Error al procesar el archivo {filename}: {e}")

        session.close()

    def guardar_prospectos_en_db(self, df, tipo_sorteo, metodo, id_sorteo):
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            if not df.empty:
                # Filtrar el DataFrame según el método de cálculo
                df_filtrado = df[df['MetodoCalculo'] == metodo]

                fila = 1
                for _, row in df_filtrado.iterrows():
                    # Llamar al SP directamente
                    session.execute(text("""
                        CALL guardar_prospectos_en_db(:IdSorteo, :Posicion, :TipoSorteo, :TipoProspecto, 
                            :N1, :N2, :N3, :N4, :N5, :SB, :Peso );
                    """), {
                        'IdSorteo': int(id_sorteo),
                        'Posicion': int(fila),
                        'TipoSorteo': tipo_sorteo,
                        'TipoProspecto': metodo,
                        'N1': int(row['N1']),
                        'N2': int(row['N2']),
                        'N3': int(row['N3']),
                        'N4': int(row['N4']),
                        'N5': int(row['N5']),
                        'SB': int(row['SB']) if pd.notna(row['SB']) else None,
                        'Peso': float(row['Peso']) if pd.notna(row['Peso']) else None
                    })

                    fila += 1

                session.commit()
                print(f"Datos procesados para IdSorteo: {id_sorteo}, TipoSorteo: {tipo_sorteo}, TipoProspecto: {metodo}")

        except Exception as e:
            session.rollback()
            print(f"Error al procesar los datos: {e}")
        finally:
            session.close()


    def guardar_prospectos_en_db_batch(self, df, tipo_sorteo, metodo, id_sorteo, batch_size=500):
        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            if not df.empty:
                # Filtrar el DataFrame según el método de cálculo
                df_filtrado = df[df['MetodoCalculo'] == metodo]
                
                # Verificar si el DataFrame tiene datos después del filtro
                if df_filtrado.empty:
                    print("No hay datos para insertar.")
                    return

                filas = []
                for idx, row in df_filtrado.iterrows():
                    filas.append({
                        'IdSorteo': int(row['IdSorteo']),
                        'Posicion': int(idx + 1),
                        'TipoSorteo': tipo_sorteo,
                        'TipoProspecto': metodo,
                        'N1': int(row['N1']),
                        'N2': int(row['N2']),
                        'N3': int(row['N3']),
                        'N4': int(row['N4']),
                        'N5': int(row['N5']),
                        'SB': int(row['SB']) if pd.notna(row['SB']) else None,
                        'Peso': float(row['Peso']) if pd.notna(row['Peso']) else None
                    })

                    # Realizar la inserción en batch al alcanzar el tamaño definido
                    if len(filas) == batch_size:
                        self._insertar_batch(session, filas)
                        filas.clear()  # Limpiar el batch después de insertar

                # Insertar las filas restantes si hay alguna
                if filas:
                    self._insertar_batch(session, filas)

                session.commit()
                print(f"Datos procesados para IdSorteo: {id_sorteo}, TipoSorteo: {tipo_sorteo}, TipoProspecto: {metodo}")

        except Exception as e:
            session.rollback()
            print(f"Error al procesar los datos: {e}")
        finally:
            session.close()

    def _insertar_batch(self, session, filas):
        # Construir el batch de ejecución para el SP
        session.execute(text("""
            CALL guardar_prospectos_en_db(
                :IdSorteo, :Posicion, :TipoSorteo, :TipoProspecto, 
                :N1, :N2, :N3, :N4, :N5, :SB, :Peso
            );
        """), filas)

    

    def insertar_registros_sorteos_from_csv(self, tabla_destino):
        # Leer el archivo CSV en un DataFrame
        df = pd.read_csv(
            self.input_file, 
            header=None, 
            names=['IdSorteo', 'FechaSorteo', 'TipoSorteo', 'Ganador', 'Nuevo', 'N1', 'N2', 'N3', 'N4', 'N5', 'SB']
        )

        # Convertir fechas al formato correcto
        df['FechaSorteo'] = pd.to_datetime(df['FechaSorteo'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')

        if self.initial > 0:
            df = df[df['IdSorteo'] >= self.initial]

        # Crear conexión a la base de datos
        # engine = self.get_db_connection()
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Consulta con manejo de conflicto para evitar errores en caso de registros duplicados
        insert_query = f"""
        INSERT INTO public.{tabla_destino} ("IdSorteo", "FechaSorteo", "TipoSorteo", "Ganador", "Nuevo", "N1", "N2", "N3", "N4", "N5", "SB")
        VALUES (:IdSorteo, :FechaSorteo, :TipoSorteo, :Ganador, :Nuevo, :N1, :N2, :N3, :N4, :N5, :SB)
        ON CONFLICT ("IdSorteo", "TipoSorteo") DO NOTHING;
        """

        try:
            for _, row in df.iterrows():
                session.execute(
                    text(insert_query),
                    {
                        "IdSorteo": int(row["IdSorteo"]),
                        "FechaSorteo": row["FechaSorteo"],
                        "TipoSorteo": row["TipoSorteo"],
                        "Ganador": row["Ganador"] if pd.notna(row["Ganador"]) else None,
                        "Nuevo": row["Nuevo"] if pd.notna(row["Nuevo"]) else None,
                        "N1": int(row["N1"]),
                        "N2": int(row["N2"]),
                        "N3": int(row["N3"]),
                        "N4": int(row["N4"]),
                        "N5": int(row["N5"]),
                        "SB": int(row["SB"]) if pd.notna(row["SB"]) else None,
                    }
                )
                print(f"Registro {row['IdSorteo']} insertado correctamente.")
            
            # Confirmar los cambios
            session.commit()
        except Exception as e:
            session.rollback()  # Revertir cambios en caso de error
            print(f"Error al insertar registros: {e}")
        finally:
            session.close()  # Cerrar la sesión


    def insertar_registros_sorteos_db(self, sorteo, fecha, tipo, ganador, numeros):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        try:
            ganador_parts = ganador.split(',')
            nuevo = ganador_parts[1] if len(ganador_parts) > 1 else None
            nums = list(map(int, numeros.split(',')))
            data = {
                "IdSorteo": int(sorteo),
                "FechaSorteo": datetime.strptime(fecha, '%d/%m/%Y').strftime('%Y-%m-%d'),
                "TipoSorteo": tipo,
                "Ganador": ganador_parts[0],
                "Nuevo": nuevo,
                "N1": nums[0], "N2": nums[1], "N3": nums[2], "N4": nums[3], "N5": nums[4],
                "SB": nums[5] if len(nums) > 5 else None
            }
            query = text("""
                INSERT INTO sorteos (
                    "IdSorteo", "FechaSorteo", "TipoSorteo", "Ganador", "Nuevo",
                    "N1", "N2", "N3", "N4", "N5", "SB"
                ) VALUES (
                    :IdSorteo, :FechaSorteo, :TipoSorteo, :Ganador, :Nuevo,
                    :N1, :N2, :N3, :N4, :N5, :SB
                ) ON CONFLICT ("IdSorteo", "TipoSorteo") DO NOTHING;
            """)
            session.execute(query, data)
            session.commit()
            print(f"Registro {sorteo} {tipo} insertado correctamente.")
        except Exception as e:
            session.rollback()
            print(f"Error al insertar sorteo {sorteo} tipo {tipo}: {e}")
        finally:
            session.close()

    def obtener_ultimo_idsorteo(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        try:
            result = session.execute(
                text("SELECT obtener_ultimo_idsorteo()")

            )
            ultimo_id = result.scalar()
            print(f"Último IdSorteo insertado: {ultimo_id}")
            return ultimo_id
        except Exception as e:
            print(f"Error al consultar el último IdSorteo: {e}")
            return None
        finally:
            session.close()


    def obtener_ultimo_idprospecto(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        try:
            result = session.execute(
                text("SELECT obtener_ultimo_idprospecto()")

            )
            ultimo_id = result.scalar()
            print(f"Último IdProspecto insertado: {ultimo_id}")
            return ultimo_id
        except Exception as e:
            print(f"Error al consultar el último IdProspecto: {e}")
            return None
        finally:
            session.close()




    def obtener_ultimo_id_resultado_comparacion(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        try:
            result = session.execute(
                text("SELECT obtener_ultimo_id_resultados_comparacion()")

            )
            ultimo_id = result.scalar()
            print(f"Último Id resultado comparacion insertado: {ultimo_id}")
            return ultimo_id
        except Exception as e:
            print(f"Error al consultar el último Id resultado comparacion: {e}")
            return None
        finally:
            session.close()