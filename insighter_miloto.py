import pandas as pd
import numpy as np
from itertools import combinations
from statistics import median
from requester_miloto import MilotoScraper 
from postgressdbutilMI import PostgressdbUtil


# Función para calcular intervalos
def calcular_intervalos(df, columnas):
    resultados = []
    
    # Unificar las columnas de números en una sola columna
    df_melted = df.melt(id_vars=['IdSorteo', 'TipoSorteo'], value_vars=columnas, var_name='Grupo', value_name='Numero')
    df_melted = df_melted.dropna().sort_values(by=['Numero', 'IdSorteo'])

    # Obtener el total de sorteos
    sorteos = df['IdSorteo'].unique()
    total_sorteos = len(sorteos)
    
    for num in df_melted['Numero'].unique():
        subset = df_melted[df_melted['Numero'] == num]
        apariciones = subset['IdSorteo'].values
        
        if len(apariciones) > 0:
            segmentos = [apariciones[0] - sorteos[0]] + [apariciones[i] - apariciones[i-1] for i in range(1, len(apariciones))]
            if apariciones[-1] < sorteos[-1]:
                segmentos.append(sorteos[-1] - apariciones[-1])

            promedio = sum(segmentos) / len(segmentos)
            med = median(segmentos)
            std_dev = np.std(segmentos) if len(segmentos) > 1 else 0
            ultimos_sorteos = sorteos[-1] - apariciones[-1]
            frecuencia = len(apariciones)

            # Cálculo de probabilidades individuales
            prob_avg = calcular_probabilidad_avg(ultimos_sorteos, promedio)
            prob_mediana = calcular_probabilidad_mediana(ultimos_sorteos, med)
            prob_fusion = calcular_probabilidad_fusion(prob_avg, prob_mediana)
            prob_std = calcular_probabilidad_std(ultimos_sorteos, promedio, std_dev)
            prob_recencia = calcular_probabilidad_recencia(ultimos_sorteos, total_sorteos)
            prob_frecuencia_inv = calcular_probabilidad_frecuencia_inversa(frecuencia, total_sorteos)
            prob_exp = calcular_probabilidad_exponencial(ultimos_sorteos)

            # Calcular probabilidad compuesta
            prob_compuesta = calcular_probabilidad_compuesta(
                prob_avg, prob_mediana, prob_fusion,
                prob_std, prob_recencia, prob_frecuencia_inv, prob_exp
            )

            resultados.append((
                num, segmentos, promedio, med, std_dev, ultimos_sorteos, frecuencia,
                prob_avg, prob_mediana, prob_fusion, prob_std, prob_recencia, prob_frecuencia_inv, prob_exp, prob_compuesta
            ))
    
    return pd.DataFrame(resultados, columns=[
        'Numero', 'Intervalos', 'Promedio', 'Mediana', 'DesviacionStd', 'UltimosSorteos', 'Frecuencia', 'Probabilidad_Avg', 'Probabilidad_Mediana', 'Probabilidad_Fusion',
        'Probabilidad_Std', 'Probabilidad_Recencia', 'Probabilidad_FrecuenciaInv', 'Probabilidad_Exponencial', 'Probabilidad_Compuesta'
    ])

def calcular_intervalos_primera_vez(df, columnas):
    resultados = []
    
    # Unificar las columnas de números
    df_melted = df.melt(
        id_vars=['IdSorteo'],
        value_vars=columnas,
        var_name='Grupo',
        value_name='Numero'
    )
    df_melted = df_melted.dropna().sort_values(by=['Numero', 'IdSorteo'])

    # Obtener sorteos únicos
    sorteos = df['IdSorteo'].unique()
    total_sorteos = len(sorteos)
    
    for num in df_melted['Numero'].unique():
        subset = df_melted[df_melted['Numero'] == num]
        apariciones = subset['IdSorteo'].values
        
        if len(apariciones) > 0:
            # En el primer sorteo, no hay intervalos previos
            segmentos = [0]  # intervalo inicial es 0
            promedio = 0
            med = 0
            std_dev = 0
            ultimos_sorteos = 0
            frecuencia = 1  # primera aparición

            # Todas las probabilidades pueden partir de un valor neutro
            prob_avg = 0
            prob_mediana = 0
            prob_fusion = 0
            prob_std = 0
            prob_recencia = 1  # Recencia máxima (acaba de salir)
            prob_frecuencia_inv = 1 / total_sorteos
            prob_exp = 0
            prob_compuesta = 0

            resultados.append((
                num, segmentos, promedio, med, std_dev, ultimos_sorteos, frecuencia,
                prob_avg, prob_mediana, prob_fusion, prob_std, prob_recencia,
                prob_frecuencia_inv, prob_exp, prob_compuesta
            ))

    return pd.DataFrame(resultados, columns=[
        'Numero', 'Intervalos', 'Promedio', 'Mediana', 'DesviacionStd',
        'UltimosSorteos', 'Frecuencia', 'Probabilidad_Avg',
        'Probabilidad_Mediana', 'Probabilidad_Fusion', 'Probabilidad_Std',
        'Probabilidad_Recencia', 'Probabilidad_FrecuenciaInv',
        'Probabilidad_Exponencial', 'Probabilidad_Compuesta'
    ])

def calcular_probabilidad_std(ultimos_sorteos, promedio, desviacion):
    if desviacion == 0:
        return 0.0
    z = (ultimos_sorteos - promedio) / desviacion
    return min(max(1 / (1 + abs(z)), 0.0), 1.0)


def calcular_probabilidad_recencia(ultimos_sorteos, total_sorteos):
    if total_sorteos == 0:
        return 0.0
    score = ultimos_sorteos / total_sorteos
    return round(score, 2)


def calcular_probabilidad_frecuencia_inversa(frecuencia, total_sorteos):
    if total_sorteos == 0 or frecuencia == 0:
        return 1.0
    score = 1 - (frecuencia / total_sorteos)
    return round(score, 2)


def calcular_probabilidad_exponencial(ultimos_sorteos, base=1.05):
    return round(min(1.0, (base ** ultimos_sorteos) / 100), 2)

def calcular_probabilidad_compuesta(prob_avg, prob_mediana, prob_fusion, prob_std, prob_recencia, prob_frecuencia_inv, prob_exp, pesos=None):
    # Pesos por defecto si no se especifican (puedes ajustarlos a tus criterios)
    if pesos is None:
        pesos = {
            'avg': 0.15,
            'mediana': 0.15,
            'fusion': 0.20,
            'std': 0.15,
            'recencia': 0.10,
            'frecuencia_inv': 0.10,
            'exponencial': 0.15
        }

    # Cálculo ponderado
    probabilidad_total = (
        prob_avg * pesos['avg'] +
        prob_mediana * pesos['mediana'] +
        prob_fusion * pesos['fusion'] +
        prob_std * pesos['std'] +
        prob_recencia * pesos['recencia'] +
        prob_frecuencia_inv * pesos['frecuencia_inv'] +
        prob_exp * pesos['exponencial']
    )

    return round(probabilidad_total, 4)

def calcular_probabilidad_avg(ultimos_sorteos, promedio):
    if ultimos_sorteos == 0 or promedio == 0:
        # Si cualquiera de los dos valores es 0, retornar 0
        return 0
    else:
        # Calcular la probabilidad como el mínimo entre ambas divisiones
        return min(ultimos_sorteos / promedio, promedio / ultimos_sorteos)

def calcular_probabilidad_mediana(ultimos_sorteos, mediana):
    if ultimos_sorteos == 0 or mediana == 0:
        # Si cualquiera de los dos valores es 0, retornar 0
        return 0
    else:
        # Calcular la probabilidad como el mínimo entre ambas divisiones
        return min(ultimos_sorteos / mediana, mediana / ultimos_sorteos)
    
def calcular_probabilidad_fusion(probabilidad_avg, probabilidad_mediana):
    if probabilidad_avg == 0 or probabilidad_mediana == 0:
        # Si cualquiera de los dos valores es 0, retornar 0
        return 0
    else:
        # Calcular la probabilidad como el mínimo entre ambas divisiones
        return (probabilidad_avg + probabilidad_mediana) / 2


def generar_prospectos_con_peso(resultados_numeros, metrica, metodo_calculo):
    if metrica not in resultados_numeros.columns:
        print(f"La métrica '{metrica}' no está disponible en los resultados. Se omite el método '{metodo_calculo}'.")
        return pd.DataFrame(columns=['N1', 'N2', 'N3', 'N4', 'N5', 'Peso', 'MetodoCalculo'])

    numeros_prospecto = resultados_numeros[resultados_numeros[metrica] > 0.75].sort_values(by=metrica, ascending=False).head(10)
    combinaciones = []

    for comb in combinations(numeros_prospecto['Numero'], 5):
        probabilidad_comb = (
            numeros_prospecto[numeros_prospecto['Numero'].isin(comb)][metrica].sum()
        )
        combinaciones.append((*sorted(comb), probabilidad_comb, metodo_calculo))
        print(f"Comb: {comb}, metodo_calculo: {metodo_calculo}, probabilidad_comb: {probabilidad_comb}")

    return pd.DataFrame(combinaciones, columns=['N1', 'N2', 'N3', 'N4', 'N5', 'Peso', 'MetodoCalculo'])



# Función para comparar los prospectos generados contra los resultados reales del siguiente sorteo
def comparar_prospectos_con_resultados(df_sorteo, df_prospectos, lastdraft):
    aciertos = 0
    numeros_acertados = []
    # numeros_ = ()
    numeros_sorteo = ()
    # superbalota_acertada = False

    # Consolidar todos los números de los prospectos
    # numeros_prospecto = set(df_prospectos[['N1', 'N2', 'N3', 'N4', 'N5']].values.flatten())
    numeros_prospecto = set(map(int, df_prospectos[['N1', 'N2', 'N3', 'N4', 'N5']].values.flatten()))
    
    if lastdraft == 0:
        # Comparar con los números del sorteo actual
        if not df_sorteo.empty:
            numeros_sorteo = set(map(int, df_sorteo[['N1', 'N2', 'N3', 'N4', 'N5']].values.flatten()))
            numeros_sorteo = set(map(int, df_sorteo.iloc[0][['N1', 'N2', 'N3', 'N4', 'N5']]))


        # numeros_sorteo = set(map(int, df_sorteo.iloc[0][['N1', 'N2', 'N3', 'N4', 'N5']]))

        # Identificar los números acertados
        aciertos_numeros = numeros_sorteo & numeros_prospecto
        aciertos += len(aciertos_numeros)
        numeros_acertados = list(aciertos_numeros)

    return {
        'IdSorteo': [lastdraft if lastdraft > 0 else df_sorteo['IdSorteo'].iloc[0]],  # Convertir en lista
        'Numeros_Sorteo': [str(tuple(numeros_sorteo))],  # Convertir a string para uniformidad
        'Numeros_Prospecto': [str(tuple(numeros_prospecto))],  # Convertir a string
        'Aciertos': [aciertos],  # Convertir en lista
        'Numeros_Acertados': [str(tuple(numeros_acertados))]  # Convertir a string
    }

# Función para comparar los prospectos generados contra los resultados reales del siguiente sorteo
def comparar_prospectos_con_resultados_vacios(df_sorteo, df_prospectos, sb, lastdraft):
    aciertos = 0
    numeros_acertados = []
    numeros_sorteo = set()
    numeros_prospecto = set()
    # superbalota_acertada = False

    # Validar si df_prospectos no está vacío antes de extraer valores
    if not df_prospectos.empty:
        numeros_prospecto = set(df_prospectos[['N1', 'N2', 'N3', 'N4', 'N5']].values.flatten())

    if lastdraft == 0 and not df_sorteo.empty:
        # Comparar con los números del sorteo actual si df_sorteo tiene datos
        numeros_sorteo = set(df_sorteo[['N1', 'N2', 'N3', 'N4', 'N5']].values.flatten())

        # Identificar los números acertados
        aciertos_numeros = numeros_sorteo & numeros_prospecto
        aciertos = len(aciertos_numeros)
        numeros_acertados = list(aciertos_numeros)

    return {
        'IdSorteo': lastdraft if lastdraft > 0 else df_sorteo['IdSorteo'].iloc[0] if not df_sorteo.empty else None,
        'Numeros_Sorteo': list(numeros_sorteo) if numeros_sorteo else [],
        'Numeros_Prospecto': list(numeros_prospecto) if numeros_prospecto else [],
        'Aciertos': aciertos,
        'Numeros_Acertados': numeros_acertados if numeros_acertados else []
    }

def filtrar_df_prospectos(df, id_min, tipoProspecto):
    filtro = (df['IdSorteo'] == int(id_min)) & (df['TipoProspecto'] == tipoProspecto)
    return df[filtro]

# Proceso principal
def proceso_completo(postgres):
    # Cargar a dataframes la informacion de las
    df_original = postgres.leer_datos_from_db()
    # df_resultados_db = postgres.leer_resultados_comparacion_from_db(tipo_sorteo)

    #Ordenar dataframes 
    df_sorteos_ordenados = df_original.sort_values(by='IdSorteo')

    metodos = ['Fusión', 'Avg', 'Mediana', 'Std', 'Recencia', 'FrecuenciaInv', 'Exponencial']
    nombres = ['Fusión', 'Promedio', 'Mediana', 'Standard', 'Recencia', 'FrecuenciaInv', 'Exponencial']

    zipped_methods = dict(zip(metodos, nombres))

    pos = 0

    for idx in range(sorteo_inicial_from_comparar, postgres.final + 1 ):
        # Obtener los sorteos hasta el sorteo anterior
        current_draft =int(idx)
        df_prospectos = postgres.leer_prospectos_from_db(current_draft )
        if not df_prospectos.empty:

            df_prospectos_ordenados = df_prospectos.sort_values(by=['IdSorteo', 'Posicion', 'TipoProspecto'])
            df_previos = df_sorteos_ordenados.iloc[:idx]
            registro_filtrado = df_sorteos_ordenados[df_sorteos_ordenados['IdSorteo'] == current_draft]

            # Calcular intervalos y generar prospectos basados en los sorteos previos
            resultados_numeros = calcular_intervalos(df_previos, ['N1', 'N2', 'N3', 'N4', 'N5'])

            prospectos = {}
            for metodo, nombre in zipped_methods.items():
                df_filtrado = filtrar_df_prospectos(
                    df_prospectos_ordenados, 
                    idx, 
                    nombre 
                )
                prospectos[metodo] = df_filtrado
        else:
            df_prospectos_ordenados = pd.DataFrame(columns = ["IdSorteo", "Posicion", "TipoProspecto", "N1", "N2", "N3", "N4", "N5", "Peso"])
            df_previos = pd.DataFrame(columns=['IdSorteo', 'N1', 'N2', 'N3', 'N4', 'N5'])
            resultados_numeros = calcular_intervalos_primera_vez(df_previos, ['N1', 'N2', 'N3', 'N4', 'N5'])
            registro_filtrado = df_sorteos_ordenados[df_sorteos_ordenados['IdSorteo'] == current_draft + 1]
            print(registro_filtrado)
        


        # df_prospectos_fusion, df_prospectos_promedio, df_prospectos_mediana 
        prospectos = generar_prospectos(df_prospectos_ordenados, resultados_numeros, current_draft, postgres, zipped_methods)

        # Combinar los prospectos generados
        df_prospectos = pd.concat(prospectos.values(), ignore_index=True)

        siguiente_sorteo = (df_sorteos_ordenados['IdSorteo'] == int(current_draft + 1))  

        # Obtener los resultados reales del siguiente sorteo
        pos += 1
                    
        # Comparar los prospectos con los resultados reales

        current = current_draft if current_draft == postgres.final else 0 
        resultado_comparacion = comparar_prospectos_con_resultados(registro_filtrado, df_prospectos, int(current))
        df_resultado_comparacion = pd.DataFrame(resultado_comparacion)
        if current == 0 : 
            postgres.insertar_comparaciones_calculadas(df_resultado_comparacion)
        else : 
            print(df_resultado_comparacion)

    # Retornar el DataFrame con todos los resultados de las comparaciones
    return df_resultado_comparacion

# Genera y guarda los prospectos según los métodos especificados.
def generar_prospectos(df_prospectos_ordenados, resultados_numeros,  id_sorteo, postgres, metodos):

    prospectos = {}    

    for metodo, nombre in metodos.items():
        df_filtrado = df_prospectos_ordenados[
            df_prospectos_ordenados['TipoProspecto'] == metodo
        ]

        if df_filtrado.empty:
            # Nombre de la métrica según el método
            metrica = f'Probabilidad_{metodo}'
            df_prospectos_new = generar_prospectos_con_peso(resultados_numeros, metrica, metodo)
            postgres.guardar_prospectos_en_db(df_prospectos_new, metodo, id_sorteo)
            prospectos[metodo] = df_prospectos_new
        else:
            prospectos[metodo] = df_filtrado

    return prospectos


def generar_secuencia(inicio, deltas, limite=43):
    # Genera una secuencia de números dentro del rango 1-43 siguiendo los deltas dados.

    secuencia = [inicio]
    actual = inicio
    for delta in deltas:
        siguiente = (actual + delta - 1) % limite + 1  # Mantiene el ciclo 1-43
        secuencia.append(siguiente)
        actual = siguiente
    return secuencia


def generar_figuras(deltas, limite=43):
    #Genera todas las posibles figuras a partir de un conjunto de deltas.

    figuras = []
    for inicio in range(1, limite + 1):
        figura = generar_secuencia(inicio, deltas, limite)
        figuras.append(figura)
    return figuras


def figuresByDelta():
    deltas = [3, 4, 5, 6]  # Puedes cambiar estos valores
    figuras = generar_figuras(deltas)
    
    print(f"Figuras generadas con deltas {deltas}:")
    for figura in figuras:
        print(figura)





# Ejecución
if __name__ == "__main__":
    # insertar data desde la web 
    initial = 1 #int(input("Ingrese el número de sorteo inicial: "))  ##inicio de los sorteos 2081

    postgres = PostgressdbUtil()
    most_recent_inserted = postgres.obtener_ultimo_idsorteo()
    most_recent_scrapped = 0

    scrap_initial =  most_recent_inserted + 1 #int(input("Ingrese el número de scrapping inicial ó 0 para omitir: "))  ##sorteo inicial para scrapping de los sitios
    if(scrap_initial > 0):
        scrapper = MilotoScraper(scrap_initial, most_recent_inserted)
        scrapper.run()
        most_recent_scrapped = scrapper.final
        final = scrapper.final +1

    postgres.set_initial_values(initial, final, scrap_initial)

    sorteo_inicial_from_csv = scrap_initial # Numero superior al ultimo valor en la tabla de BD

    postgres.obtener_ultimo_idprospecto()
    prospecto_inicial = postgres.obtener_ultimo_idprospecto() #int(input("Ingrese el prospecto para ingresar a la Tabla Prospectos: ")) 
    sorteo_inicial_from_comparar = postgres.obtener_ultimo_id_resultado_comparacion() #int(input("Ingrese el sorteo inicial para comparar(CSV - DB): ")) 
    # if(sorteo_inicial_from_csv > 0):
        # postgres.insertar_registros_sorteos_from_csv('sorteos')


    # Numero superior al ultimo valor en la tabla de BD o numero mas alto de los csv
    # if(prospecto_inicial > 0):    
    #     postgres.insertar_prospectos_en_db(prospecto_inicial, final)

    # insertar prospectos calculados previamente
    # figuresByDelta()

    # Ejecutar el proceso completo para sorteos 'Tr'
    df_resultados_comparacion = proceso_completo(postgres)
    df_resultados_comparacion.to_csv('resultados_miloto.csv', index=False)

    # # Ejecutar el proceso completo para sorteos 'Re'
    # tipo_sorteo = 'Re'
    # df_resultados_comparacion_re = proceso_completo(tipo_sorteo, postgres)
    # df_resultados_comparacion_re.to_csv('resultados_comparacion_re2.csv', index=False)
