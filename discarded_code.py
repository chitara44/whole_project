# # Configuración de la base de datos
# DB_HOST = "localhost"
# DB_NAME = "baloto"
# DB_USER = "postgres"
# DB_PASSWORD = "R1c4rd1t0%"
# DB_PORT = "5432"

# Crear conexión a la base de datos
# def get_db_connection():
#     connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
#     return create_engine(connection_string, connect_args={"client_encoding": "utf8"})

# Función para obtener la conexión a la base de datos
# def get_db_connection():
#     DATABASE_URL = "postgresql://postgres:Ar3qu1p3%@localhost:5432/sorteos_baloto"
#     return create_engine(DATABASE_URL)

# # Leer datos desde la base de datos
# def leer_datos_from_db(tipo_sorteo=None):
#     engine = get_db_connection()
#     query = """
#         SELECT  "IdSorteo", "FechaSorteo", "TipoSorteo", "Ganador", "Nuevo", "N1", "N2", "N3", "N4", "N5", "SB"
#         FROM public.sorteos
#     """
#     if tipo_sorteo:
#         query += f" WHERE \"TipoSorteo\" = '{tipo_sorteo}'"
#     try:
#         return pd.read_sql(query, engine)
#     except Exception as e:
#         print(f"Error al cargar datos: {e}")
#         return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error
    
# Leer datos desde la base de datos
# def leer_prospectos_from_db(tipo_sorteo=None):
#     engine = get_db_connection()
#     query = """
#         SELECT  "IdSorteo", "Posicion", "TipoSorteo", "TipoProspecto", "N1", "N2", "N3", "N4", "N5", "SB", "Peso"
#         FROM public.prospectos
#     """
#     if tipo_sorteo:
#         query += f" WHERE \"TipoSorteo\" = '{tipo_sorteo}'"
#     try:
#         return pd.read_sql(query, engine)
#     except Exception as e:
#         print(f"Error al cargar datos: {e}")
#         return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

# # Leer datos desde la base de datos
# def leer_resultados_comparacion_from_db(tipo_sorteo=None):
#     engine = get_db_connection()
#     query = """
#         SELECT  "IdSorteo", "TipoSorteo", "Numeros_Sorteo", "Numeros_Prospecto", "Aciertos", "Numeros_Acertados", "Numero_Superbalota", "Superbalota_Acertada"
#         FROM public.resultados_comparacion
#     """
#     if tipo_sorteo:
#         query += f" WHERE \"TipoSorteo\" = '{tipo_sorteo}'"
#     try:
#         return pd.read_sql(query, engine)
#     except Exception as e:
#         print(f"Error al cargar datos: {e}")
#         return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

# Función para insertar registros desde un archivo CSV
def insertar_registros_sorteos_from_csv(ruta_csv, tabla_destino):


    # Leer el archivo CSV en un DataFrame
    df = pd.read_csv(
        ruta_csv, 
        header=None, 
        names=['IdSorteo', 'FechaSorteo', 'TipoSorteo', 'Ganador', 'Nuevo', 'N1', 'N2', 'N3', 'N4', 'N5', 'SB']
    )

    # Convertir fechas al formato correcto
    df['FechaSorteo'] = pd.to_datetime(df['FechaSorteo'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')

    # Crear conexión a la base de datos
    engine = get_db_connection()
    Session = sessionmaker(bind=engine)
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

# Función para insertar registros desde un archivo CSV
# def insertar_comparaciones_from_csv(ruta_csv, tabla_destino):
#     # Leer el archivo CSV en un DataFrame
#     df = pd.read_csv(
#         ruta_csv, 
#         header=None, 
#         names=['IdSorteo', 'Numeros_Sorteo', 'Numeros_Prospecto', 'Aciertos', 'Numeros_Acertados', 'Numero_Superbalota', 'Superbalota_Acertada']
#     )

#     # Crear conexión a la base de datos
#     engine = get_db_connection()
#     Session = sessionmaker(bind=engine)
#     session = Session()

#     # Consulta con manejo de conflicto para evitar errores en caso de registros duplicados
#     insert_query = f"""
#     INSERT INTO public.{tabla_destino} ("IdSorteo", "TipoSorteo", "Numeros_Sorteo", "Numeros_Prospecto", "Aciertos", "Numeros_Acertados", "Numero_Superbalota", "Superbalota_Acertada")
#     VALUES (:IdSorteo, :TipoSorteo, :Numeros_Sorteo, :Numeros_Prospecto, :Aciertos, :Numeros_Acertados, :Numero_Superbalota, :Superbalota_Acertada)
#     ON CONFLICT ("IdSorteo","TipoSorteo") DO NOTHING;
#     """

#     try:
#         for _, row in df.iterrows():
#             session.execute(
#                 text(insert_query),
#                 {
#                     "IdSorteo": int(row["IdSorteo"]),
#                     "TipoSorteo": row["TipoSorteo"],
#                     "Numeros_Sorteo": row["Numeros_Sorteo"],
#                     "Numeros_Prospecto": row["Numeros_Prospecto"],
#                     "Aciertos": row["Aciertos"],
#                     "Numeros_Acertados": row["Numeros_Acertados"],
#                     "Numero_Superbalota": row["Numero_Superbalota"],
#                     "Superbalota_Acertada": row["Superbalota_Acertada"]
#                 }
#             )
#             print(f"Registro {row['IdSorteo']} insertado correctamente en {tabla_destino}")
        
#         # Confirmar los cambios
#         session.commit()
#     except Exception as e:
#         session.rollback()  # Revertir cambios en caso de error
#         print(f"Error al insertar registros: {e}")
#     finally:
#         session.close()  # Cerrar la sesión




# def insertar_comparaciones_calculadas(datos, tabla_destino):

#     # Crear conexión a la base de datos
#     engine = get_db_connection()
#     Session = sessionmaker(bind=engine)
#     session = Session()

#     # Consulta con manejo de conflicto para evitar errores en caso de registros duplicados
#     insert_query = f"""
#     INSERT INTO public.{tabla_destino} (\"IdSorteo\", \"TipoSorteo\", \"Numeros_Sorteo\", \"Numeros_Prospecto\", \"Aciertos\", \"Numeros_Acertados\", \"Numero_Superbalota\", \"Superbalota_Acertada\")
#     VALUES (:IdSorteo, :TipoSorteo, :Numeros_Sorteo, :Numeros_Prospecto, :Aciertos, :Numeros_Acertados, :Numero_Superbalota, :Superbalota_Acertada)
#     ON CONFLICT ("IdSorteo", "TipoSorteo") DO NOTHING;
#     """

#     try:
#         session.execute(
#             text(insert_query),
#             {
#                 "IdSorteo": int(datos["IdSorteo"][0]),
#                 "Numeros_Sorteo": datos["Numeros_Sorteo"][0],
#                 "Numeros_Prospecto": datos["Numeros_Prospecto"][0],
#                 "Aciertos": int(datos["Aciertos"][0]),
#                 "Numeros_Acertados": datos["Numeros_Acertados"][0],
#                 "Numero_Superbalota": int(datos.get("Numero_Superbalota", [""])[0]),
#                 "Superbalota_Acertada": datos.get("Superbalota_Acertada", [""])[0],
#                 "TipoSorteo": datos.get("TipoSorteo", [""])[0]  # Valor por defecto si falta
#             }
#         )
        
#         # Confirmar los cambios
#         session.commit()
#         print(f"Registro {datos['IdSorteo'][0]} insertado correctamente en {tabla_destino}")

#     except Exception as e:
#         session.rollback()  # Revertir cambios en caso de error
#         print(f"Error al insertar registro: {e}")
#     finally:
#         session.close()  # Cerrar la sesión


# # Función para insertar registros de prospectos desde un archivo CSV
# def insertar_prospectos_en_db():
#     # Configurar la conexión a la base de datos
#     start=int(2487)
#     end=int(2488)
#     tipos_sorteo=['Tr', 'Re']
#     tipos_prospecto=['Promedio', 'Fusión', 'Mediana']
#     base_path="./"  # Cambia esto a la ruta donde están tus archivos CSV

#     # Crear conexión a la base de datos
#     engine = get_db_connection()
#     Session = sessionmaker(bind=engine)
#     session = Session()

#     print(str(type(start)) + ' - ' + str(type(end)))

#     # Iterar sobre IdSorteo, TipoSorteo y TipoProspecto
#     for id_sorteo in range(start, end):
#         for tipo_sorteo in tipos_sorteo:
#             for tipo_prospecto in tipos_prospecto:
#                 # Construir el nombre del archivo
#                 filename = f"{base_path}prospectos_{id_sorteo}_{tipo_sorteo}_{tipo_prospecto}.csv"
#                 try:
#                     # Leer el archivo CSV
#                     with open(filename, mode='r') as file:
#                         reader = csv.DictReader(file)
#                         fila = 1
#                         for row in reader:
#                             # Crear una consulta para insertar el registro
#                             insert_query = text("""
#                             INSERT INTO public.prospectos (\"IdSorteo\", \"Posicion\", \"TipoSorteo\", \"TipoProspecto\", \"N1\", \"N2\", \"N3\", \"N4\", \"N5\", \"SB\", \"Peso\")
#                             VALUES (:IdSorteo, :Posicion, :TipoSorteo, :TipoProspecto, :N1, :N2, :N3, :N4, :N5, :SB, :Peso)
#                             ON CONFLICT ("IdSorteo", "Posicion", "TipoSorteo", "TipoProspecto") DO NOTHING;
#                             """)
#                             session.execute(insert_query, {
#                                 'IdSorteo': int(id_sorteo),
#                                 'Posicion': int(fila),
#                                 'TipoSorteo': tipo_sorteo,
#                                 'TipoProspecto': tipo_prospecto,
#                                 'N1': int(row['N1']),
#                                 'N2': int(row['N2']),
#                                 'N3': int(row['N3']),
#                                 'N4': int(row['N4']),
#                                 'N5': int(row['N5']),
#                                 'SB': int(row['SB']),
#                                 'Peso': float(row['Peso']) if row['Peso'] else None
#                             })
#                             fila = fila + 1
#                     # Confirmar la transacción después de procesar cada archivo
#                     session.commit()
#                     print(f"Archivo procesado: {filename}")
#                 except FileNotFoundError:
#                     print(f"Archivo no encontrado: {filename}")
#                 except Exception as e:
#                     session.rollback()
#                     print(f"Error al procesar el archivo {filename}: {e}")
#     # Cerrar la sesión al final
#     session.close()



    # def leer_datos_from_db(self, tipo_sorteo=None):
    #     engine = self.get_db_connection()
    #     query = """
    #         SELECT  "IdSorteo", "FechaSorteo", "TipoSorteo", "Ganador", "Nuevo", "N1", "N2", "N3", "N4", "N5", "SB"
    #         FROM public.sorteos
    #     """
    #     if tipo_sorteo:
    #         query += f" WHERE \"TipoSorteo\" = '{tipo_sorteo}'"
    #     try:
    #         return pd.read_sql(query, engine)
    #     except Exception as e:
    #         print(f"Error al cargar datos: {e}")
    #         return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

    # def leer_prospectos_from_db(self, id_sorteo, tipo_sorteo=None, ):
    #     engine = self.get_db_connection()
    #     query = """
    #         SELECT  "IdSorteo", "Posicion", "TipoSorteo", "TipoProspecto", "N1", "N2", "N3", "N4", "N5", "SB", "Peso"
    #         FROM public.prospectos
    #     """
    #     if tipo_sorteo:
    #         query += f" WHERE \"TipoSorteo\" = '{tipo_sorteo}' AND \"IdSorteo\" = {id_sorteo}"
    #     try:
    #         return pd.read_sql(query, engine)
    #     except Exception as e:
    #         print(f"Error al cargar datos: {e}")
    #         return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error



    # def leer_resultados_comparacion_from_db(self, tipo_sorteo=None):
    #     engine = self.get_db_connection()
    #     query = """
    #         SELECT  "IdSorteo", "TipoSorteo", "Numeros_Sorteo", "Numeros_Prospecto", "Aciertos", "Numeros_Acertados", "Numero_Superbalota", "Superbalota_Acertada"
    #         FROM public.resultados_comparacion
    #     """
    #     if tipo_sorteo:
    #         query += f" WHERE \"TipoSorteo\" = '{tipo_sorteo}'"
    #     try:
    #         return pd.read_sql(query, engine)
    #     except Exception as e:
    #         print(f"Error al cargar datos: {e}")
    #         return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

    # Función para insertar registros desde un archivo CSV
    # def insertar_registros_sorteos_from_csv(self, tabla_destino):
    #     # Leer el archivo CSV en un DataFrame
    #     df = pd.read_csv(
    #         self.input_file, 
    #         header=None, 
    #         names=['IdSorteo', 'FechaSorteo', 'TipoSorteo', 'Ganador', 'Nuevo', 'N1', 'N2', 'N3', 'N4', 'N5', 'SB']
    #     )

    #     # Convertir fechas al formato correcto
    #     df['FechaSorteo'] = pd.to_datetime(df['FechaSorteo'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')

    #     if self.initial > 0:
    #         df = df[df['IdSorteo'] >= self.initial]

    #     # Crear conexión a la base de datos
    #     engine = self.get_db_connection()
    #     Session = sessionmaker(bind=engine)
    #     session = Session()

    #     # Consulta con manejo de conflicto para evitar errores en caso de registros duplicados
    #     insert_query = f"""
    #     INSERT INTO public.{tabla_destino} ("IdSorteo", "FechaSorteo", "TipoSorteo", "Ganador", "Nuevo", "N1", "N2", "N3", "N4", "N5", "SB")
    #     VALUES (:IdSorteo, :FechaSorteo, :TipoSorteo, :Ganador, :Nuevo, :N1, :N2, :N3, :N4, :N5, :SB)
    #     ON CONFLICT ("IdSorteo", "TipoSorteo") DO NOTHING;
    #     """

    #     try:
    #         for _, row in df.iterrows():
    #             session.execute(
    #                 text(insert_query),
    #                 {
    #                     "IdSorteo": int(row["IdSorteo"]),
    #                     "FechaSorteo": row["FechaSorteo"],
    #                     "TipoSorteo": row["TipoSorteo"],
    #                     "Ganador": row["Ganador"] if pd.notna(row["Ganador"]) else None,
    #                     "Nuevo": row["Nuevo"] if pd.notna(row["Nuevo"]) else None,
    #                     "N1": int(row["N1"]),
    #                     "N2": int(row["N2"]),
    #                     "N3": int(row["N3"]),
    #                     "N4": int(row["N4"]),
    #                     "N5": int(row["N5"]),
    #                     "SB": int(row["SB"]) if pd.notna(row["SB"]) else None,
    #                 }
    #             )
    #             print(f"Registro {row['IdSorteo']} insertado correctamente.")
            
    #         # Confirmar los cambios
    #         session.commit()
    #     except Exception as e:
    #         session.rollback()  # Revertir cambios en caso de error
    #         print(f"Error al insertar registros: {e}")
    #     finally:
    #         session.close()  # Cerrar la sesión


    # def insertar_comparaciones_from_csv(self, tabla_destino):
    #     # Leer el archivo CSV en un DataFrame
    #     df = pd.read_csv(
    #         self.input_file, 
    #         header=None, 
    #         names=['IdSorteo', 'Numeros_Sorteo', 'Numeros_Prospecto', 'Aciertos', 'Numeros_Acertados', 'Numero_Superbalota', 'Superbalota_Acertada']
    #     )

    #     # Crear conexión a la base de datos
    #     engine = self.get_db_connection()
    #     Session = sessionmaker(bind=engine)
    #     session = Session()

    #     # Consulta con manejo de conflicto para evitar errores en caso de registros duplicados
    #     insert_query = f"""
    #     INSERT INTO public.{tabla_destino} ("IdSorteo", "TipoSorteo", "Numeros_Sorteo", "Numeros_Prospecto", "Aciertos", "Numeros_Acertados", "Numero_Superbalota", "Superbalota_Acertada")
    #     VALUES (:IdSorteo, :TipoSorteo, :Numeros_Sorteo, :Numeros_Prospecto, :Aciertos, :Numeros_Acertados, :Numero_Superbalota, :Superbalota_Acertada)
    #     ON CONFLICT ("IdSorteo","TipoSorteo") DO NOTHING;
    #     """

    #     try:
    #         for _, row in df.iterrows():
    #             session.execute(
    #                 text(insert_query),
    #                 {
    #                     "IdSorteo": int(row["IdSorteo"]),
    #                     "TipoSorteo": row["TipoSorteo"],
    #                     "Numeros_Sorteo": row["Numeros_Sorteo"],
    #                     "Numeros_Prospecto": row["Numeros_Prospecto"],
    #                     "Aciertos": row["Aciertos"],
    #                     "Numeros_Acertados": row["Numeros_Acertados"],
    #                     "Numero_Superbalota": row["Numero_Superbalota"],
    #                     "Superbalota_Acertada": row["Superbalota_Acertada"]
    #                 }
    #             )
    #             print(f"Registro {row['IdSorteo']} insertado correctamente en {tabla_destino}")
            
    #         # Confirmar los cambios
    #         session.commit()
    #     except Exception as e:
    #         session.rollback()  # Revertir cambios en caso de error
    #         print(f"Error al insertar registros: {e}")
    #     finally:
    #         session.close()  # Cerrar la sesión


    #     # Crear conexión a la base de datos
    #     engine = self.get_db_connection()
    #     Session = sessionmaker(bind=engine)
    #     session = Session()

    #     # Consulta con manejo de conflicto para evitar errores en caso de registros duplicados
    #     insert_query = f"""
    #     INSERT INTO public.{tabla_destino} (\"IdSorteo\", \"TipoSorteo\", \"Numeros_Sorteo\", \"Numeros_Prospecto\", \"Aciertos\", \"Numeros_Acertados\", \"Numero_Superbalota\", \"Superbalota_Acertada\")
    #     VALUES (:IdSorteo, :TipoSorteo, :Numeros_Sorteo, :Numeros_Prospecto, :Aciertos, :Numeros_Acertados, :Numero_Superbalota, :Superbalota_Acertada)
    #     ON CONFLICT ("IdSorteo", "TipoSorteo") DO NOTHING;
    #     """

    #     try:
    #         session.execute(
    #             text(insert_query),
    #             {
    #                 "IdSorteo": int(datos["IdSorteo"][0]),
    #                 "Numeros_Sorteo": datos["Numeros_Sorteo"][0],
    #                 "Numeros_Prospecto": datos["Numeros_Prospecto"][0],
    #                 "Aciertos": int(datos["Aciertos"][0]),
    #                 "Numeros_Acertados": datos["Numeros_Acertados"][0],
    #                 "Numero_Superbalota": int(datos.get("Numero_Superbalota", [""])[0]),
    #                 "Superbalota_Acertada": datos.get("Superbalota_Acertada", [""])[0],
    #                 "TipoSorteo": datos.get("TipoSorteo", [""])[0]  # Valor por defecto si falta
    #             }
    #         )
            
    #         # Confirmar los cambios
    #         session.commit()
    #         print(f"Registro {datos['IdSorteo'][0]} insertado correctamente en {tabla_destino}")

    #     except Exception as e:
    #         session.rollback()  # Revertir cambios en caso de error
    #         print(f"Error al insertar registro: {e}")
    #     finally:
    #         session.close()  # Cerrar la sesión



    # def insertar_prospectos_en_db(self):
    #     # Configurar la conexión a la base de datos
    #     start=int(self.initial)
    #     end=int(self.final)
    #     tipos_sorteo=['Tr', 'Re']
    #     tipos_prospecto=['Promedio', 'Fusión', 'Mediana']
    #     base_path="./"  # Cambia esto a la ruta donde están tus archivos CSV

    #     # Crear conexión a la base de datos
    #     engine = self.get_db_connection()
    #     Session = sessionmaker(bind=engine)
    #     session = Session()

    #     print(str(type(start)) + ' - ' + str(type(end)))

    #     # Iterar sobre IdSorteo, TipoSorteo y TipoProspecto
    #     for id_sorteo in range(start, end):
    #         for tipo_sorteo in tipos_sorteo:
    #             for tipo_prospecto in tipos_prospecto:
    #                 # Construir el nombre del archivo
    #                 filename = f"{base_path}prospectos_{id_sorteo}_{tipo_sorteo}_{tipo_prospecto}.csv"
    #                 try:
    #                     # Leer el archivo CSV
    #                     with open(filename, mode='r') as file:
    #                         reader = csv.DictReader(file)
    #                         fila = 1
    #                         for row in reader:
    #                             # Crear una consulta para insertar el registro
    #                             insert_query = text("""
    #                             INSERT INTO public.prospectos (\"IdSorteo\", \"Posicion\", \"TipoSorteo\", \"TipoProspecto\", \"N1\", \"N2\", \"N3\", \"N4\", \"N5\", \"SB\", \"Peso\")
    #                             VALUES (:IdSorteo, :Posicion, :TipoSorteo, :TipoProspecto, :N1, :N2, :N3, :N4, :N5, :SB, :Peso)
    #                             ON CONFLICT ("IdSorteo", "Posicion", "TipoSorteo", "TipoProspecto") DO NOTHING;
    #                             """)
    #                             session.execute(insert_query, {
    #                                 'IdSorteo': int(id_sorteo),
    #                                 'Posicion': int(fila),
    #                                 'TipoSorteo': tipo_sorteo,
    #                                 'TipoProspecto': tipo_prospecto,
    #                                 'N1': int(row['N1']),
    #                                 'N2': int(row['N2']),
    #                                 'N3': int(row['N3']),
    #                                 'N4': int(row['N4']),
    #                                 'N5': int(row['N5']),
    #                                 'SB': int(row['SB']),
    #                                 'Peso': float(row['Peso']) if row['Peso'] else None
    #                             })
    #                             fila = fila + 1
    #                     # Confirmar la transacción después de procesar cada archivo
    #                     session.commit()
    #                     print(f"Archivo procesado: {filename}")
    #                 except FileNotFoundError:
    #                     print(f"Archivo no encontrado: {filename}")
    #                 except Exception as e:
    #                     session.rollback()
    #                     print(f"Error al procesar el archivo {filename}: {e}")
    #     # Cerrar la sesión al final
    #     session.close()





    # def guardar_prospectos_en_db(self, df, tipo_sorteo, metodo, id_sorteo):
    #     # Configurar la conexión a la base de datos
    #     engine = self.get_db_connection()
    #     Session = sessionmaker(bind=engine)
    #     session = Session()

    #     try:
    #         # Filtrar el DataFrame según los criterios especificados
    #         if not df.empty:
    #             print(df.columns)
    #             # (df['IdSorteo'] == int(id_sorteo)) &  (df['TipoSorteo'] == tipo_sorteo) & 
    #             filtro = (df['MetodoCalculo'] == metodo)
    #             df_filtrado = df[filtro]
    #             df_filtrado.shape()

    #             fila = 1
    #             for _, row in df_filtrado.iterrows():
    #                 # Crear una consulta para insertar el registro
    #                 insert_query = text("""
    #                 INSERT INTO public.prospectos (\"IdSorteo\", \"Posicion\", \"TipoSorteo\", \"TipoProspecto\", \"N1\", \"N2\", \"N3\", \"N4\", \"N5\", \"SB\", \"Peso\") 
    #                     VALUES ( :IdSorteo, :Posicion, :TipoSorteo, :TipoProspecto, :N1, :N2, :N3, :N4, :N5, :SB, :Peso )
    #                     ON CONFLICT ("IdSorteo", "Posicion", "TipoSorteo", "TipoProspecto") DO NOTHING;
    #                 """)

    #                 # Ejecutar la consulta con los datos de la fila
    #                 session.execute(insert_query, {
    #                     'IdSorteo': int(row['IdSorteo']),
    #                     'Posicion': fila,
    #                     'TipoSorteo': row['TipoSorteo'],
    #                     'TipoProspecto': row['TipoProspecto'],
    #                     'N1': int(row['N1']),
    #                     'N2': int(row['N2']),
    #                     'N3': int(row['N3']),
    #                     'N4': int(row['N4']),
    #                     'N5': int(row['N5']),
    #                     'SB': int(row['SB']),
    #                     'Peso': float(row['Peso']) if row['Peso'] else None
    #                 })

    #                 fila += 1

    #             # Confirmar la transacción después de cada lote
    #             session.commit()
    #             print(f"Datos procesados para IdSorteo: {id_sorteo}, TipoSorteo: {tipo_sorteo}, TipoProspecto: {metodo}")

    #     except Exception as e:
    #         session.rollback()
    #         print(f"Error al procesar los datos: {e}, Sorteo: {id_sorteo}, Tipo prospecto: {metodo}, Tipo sorteo: {tipo_sorteo}")
    #     finally:
    #         # Cerrar la sesión al final
    #         session.close()


# def guardar_prospectos_en_db(df, tipo_sorteo, metodo, id_sorteo):
#     # Configurar la conexión a la base de datos
#     engine = get_db_connection()
#     Session = sessionmaker(bind=engine)
#     session = Session()

#     try:
#         # Filtrar el DataFrame según los criterios especificados
#         if not df.empty:
#             print(df.columns)
#             # (df['IdSorteo'] == int(id_sorteo)) &  (df['TipoSorteo'] == tipo_sorteo) & 
#             filtro = (df['MetodoCalculo'] == metodo)
#             df_filtrado = df[filtro]
#             df_filtrado.shape()

#             fila = 1
#             for _, row in df_filtrado.iterrows():
#                 # Crear una consulta para insertar el registro
#                 insert_query = text("""
#                 INSERT INTO public.prospectos (\"IdSorteo\", \"Posicion\", \"TipoSorteo\", \"TipoProspecto\", \"N1\", \"N2\", \"N3\", \"N4\", \"N5\", \"SB\", \"Peso\") 
#                     VALUES ( :IdSorteo, :Posicion, :TipoSorteo, :TipoProspecto, :N1, :N2, :N3, :N4, :N5, :SB, :Peso )
#                     ON CONFLICT ("IdSorteo", "Posicion", "TipoSorteo", "TipoProspecto") DO NOTHING;
#                 """)

#                 # Ejecutar la consulta con los datos de la fila
#                 session.execute(insert_query, {
#                     'IdSorteo': int(row['IdSorteo']),
#                     'Posicion': fila,
#                     'TipoSorteo': row['TipoSorteo'],
#                     'TipoProspecto': row['TipoProspecto'],
#                     'N1': int(row['N1']),
#                     'N2': int(row['N2']),
#                     'N3': int(row['N3']),
#                     'N4': int(row['N4']),
#                     'N5': int(row['N5']),
#                     'SB': int(row['SB']),
#                     'Peso': float(row['Peso']) if row['Peso'] else None
#                 })

#                 fila += 1

#             # Confirmar la transacción después de cada lote
#             session.commit()
#             print(f"Datos procesados para IdSorteo: {id_sorteo}, TipoSorteo: {tipo_sorteo}, TipoProspecto: {metodo}")

#     except Exception as e:
#         session.rollback()
#         print(f"Error al procesar los datos: {e}, Sorteo: {id_sorteo}, Tipo prospecto: {metodo}, Tipo sorteo: {tipo_sorteo}")
#     finally:
#         # Cerrar la sesión al final
#         session.close()