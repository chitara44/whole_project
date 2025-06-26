import requests
from bs4 import BeautifulSoup
import re
from postgressdbutil import Baloto

class BalotoScraper:
    def __init__(self, initial, final):
        self.initial = initial
        self.final = final
        self.all_drafts = []

    def switch_case_months(self, argument):
        text_month = re.sub(r'[^A-Za-z]', '', argument)
        cases = {
            'Enero': '01', 'Febrero': '02', 'Marzo': '03',
            'Abril': '04', 'Mayo': '05', 'Junio': '06',
            'Julio': '07', 'Agosto': '08', 'Septiembre': '09',
            'Octubre': '10', 'Noviembre': '11', 'Diciembre': '12'
        }
        return cases.get(text_month, '')

    def request_sorteo(self, sorteo, tipo):
        url = f'https://www.baloto.com/resultados-{"baloto" if tipo == "Tr" else "revancha"}/{sorteo}'
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
        else:
            soup = ""
        return soup, response.status_code
    

    def extraer_fecha_sorteo(self, soup_text):
        div = soup_text.find("div", class_="mt-2 mobile-without-margin lh30 border-left-blue ps-3")
        elem = div.find(class_="gotham-medium dark-blue")
        text = elem.text.replace(' de ', '/')
        parts = text.split("/")
        if len(parts) < 3:
            return ''
        parts[1] = self.switch_case_months(text)
        clean_text = '/'.join(parts)
        return re.sub(r'[^0-9/]', '', clean_text)
    

    def is_a_winner(self, soup_text):
        row = soup_text.find("tr", class_="br-header-left br-header-right")
        td = row.find("td", class_="dark-blue")
        texto = row.find_next().text.replace('\n\n\n\n\n\n ', ',')
        texto2 = td.text.replace('\n\n\n\n\n\n ', ',')
        res1 = re.sub(r'[^0-9,+$]', '', texto)
        res2 = re.sub(r'[^0-9,+$]', '', texto2)
        if res1 + res2 == "5+$0":
            return "NO,SI"
        return "SI,SI"

    def extraer_numeros_sorteo(self, soup_text):
        container = soup_text.find("div", class_="container-balls-results")
        text = container.find_next().text.replace('\n\n\n\n\n\n ', ',')
        resultado = re.sub(r'[^0-9,]', '', text)
        return resultado

    def save_draftline(self, line):
        with open(self.output_file, 'a') as file:
            file.write(line + '\n')

    def run(self):
        i = self.initial
        while True:
            sorteo = str(i)
            encontrado = False
            for tipo in ['Tr', 'Re']:
                soup, status = self.request_sorteo(sorteo, tipo)
                if status == 200:
                    encontrado = True
                    fecha = self.extraer_fecha_sorteo(soup)
                    ganador = self.is_a_winner(soup)
                    numeros = self.extraer_numeros_sorteo(soup)
                    postgres = Baloto()
                    postgres.insertar_registros_sorteos_db(sorteo, fecha, tipo, ganador, numeros)
                else:
                    self.final = i - 1
                    print(f"Sorteo: {sorteo} tipo {tipo} Not Found (status: {status})")
            if not encontrado:
                break
            i += 1
        
        print(f"Total drafts: {len(self.all_drafts)}")