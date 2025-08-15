import requests
from bs4 import BeautifulSoup
import os
import re
from postgressdbutilMI import PostgressdbUtil

class MilotoScraper:
    def __init__(self, initial, final):
        self.initial = initial
        self.final = final
        self.all_drafts = []

    def request_sorteo(self, sorteo):

        # Realizar una solicitud HTTP al sitio web
        url = 'https://www.baloto.com/miloto/resultados-miloto/' + str(sorteo)
        response = requests.get(url)

        # # Verifica que la solicitud sea exitosa
        if response.status_code == 200:
            # Process the response from url
            soup = BeautifulSoup(response.content, "html.parser")
        else:
            soup = ""
        return soup, response.status_code

    def extraer_numeros_sorteo(self, soup_text):
        div_container2 = soup_text.find("div", class_="row d-flex justify-content-center")
        texto = div_container2.get_text(separator=' ', strip=True)
        # Utiliza una expresión regular para extraer los números
        resultado = re.findall(r'\b\d{2}\b', texto)
        numbers = ','.join(resultado)
        return numbers

    def saveDraftline(self, filename, draftline):
        with open(filename, 'a') as file:
            file.write(draftline + '\n')

    def run(self):
        i = self.initial
        while True:
            sorteo = str(i)
            encontrado = False
            soup, status = self.request_sorteo(sorteo)
            if status == 200:
                encontrado = True
                numeros = self.extraer_numeros_sorteo(soup)
                postgres = PostgressdbUtil()
                postgres.insertar_registros_sorteos_db(sorteo, numeros)
            else:
                self.final = i - 1
                print(f"Sorteo: {sorteo} Not Found (status: {status})")
            if not encontrado:
                break
            i += 1
        
        print(f"Total drafts: {len(self.all_drafts)}")
