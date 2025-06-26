import requests
from bs4 import BeautifulSoup
import csv
import re
import sys
import os


def request_sorteo(sorteo):

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

def extraer_numeros_sorteo(soup_text):

    div_container2 = soup_text.find("div", class_="row d-flex justify-content-center")

    texto = div_container2.get_text(separator=' ', strip=True)
    
    # Utiliza una expresión regular para extraer los números
    resultado = re.findall(r'\b\d{2}\b', texto)
    
    numbers = ','.join(resultado)
    return numbers

def saveDraftline(filename, draftline):
    with open(filename, 'a') as file:
        file.write(draftline + '\n')

# Example usage:

def run_scraper(initial, final):
    all_drafts = []
    for i in range(initial, final, 1):
        sorteo = str(i)
        print('sorteo: ', sorteo)
        soupTextTr, response_code = request_sorteo(sorteo)
        if (response_code == 200):
            numeros = extraer_numeros_sorteo(soupTextTr)
            trDraftComplete = sorteo + ',' + numeros 
            all_drafts.append(trDraftComplete)
            current_directory = os.path.dirname(os.path.abspath(__file__))
            saveDraftline(current_directory + '\\data_miloto.csv', trDraftComplete)
            # print(trDraftComplete)
        else:
            print ("Sorteo:", str(sorteo), " Not Found")

        draftsCount = len(all_drafts)
        print(str(draftsCount))

#print(sys.argv)
initialDraft = int(input("Ingrese el numero del primer sorteo: "))
finalDraft = int(input("Ingrese el numero del ultimo sorteo: "))
print("Received Values: " + str(initialDraft) + ", " + str (finalDraft))
run_scraper(initialDraft, finalDraft)
