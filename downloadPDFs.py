import requests
import os
import urllib.request, urllib.error, urllib.parse
from urllib.error import URLError, HTTPError

def downloadPDFs():
    directoryPDF = "./resources/pdf/"
    # Questo serve come un'autenticazione, altrimenti mi vede come un BOT e non mi permette di scaricare in maniera automatizzata da alcuni url
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0'}

    # Per tenere traccia di tutti i pdf che non vengono scaricati
    with open(directoryPDF+"pdfNonTrovati.txt", "w") as f:
        f.write("Pdf non trovati:\n")


    listaFile = os.listdir("./resources/jpeg")
    for i, file in enumerate(listaFile):
        fileName = file.split("_")[0]
        fileExtention = file.split(".")[-1]
        # Lista degli url da cui si proverà a scaricare il PDF
        # TODO capire come scaricare pdf non corretti per elena
        urls = ["http://europepmc.org/backend/ptpmcrender.fcgi?accid=" + fileName + "&blobtype=pdf",
                "https://www.ncbi.nlm.nih.gov/pmc/articles/" + fileName + "/pdf"]

        if fileExtention == "jpg":
            goodUrl = False
            for url in urls:
                try:
                    result = requests.get(url, headers=headers)
                    if result.status_code == 200:
                        goodUrl = True
                        break
                except:
                    pass
            # Salva solo se ha trovato un buon url da cui scaricare il PDF
            if goodUrl:
                f = open(directoryPDF + fileName + ".pdf", "wb")
                f.write(result.content)
                f.close()
                print("Download "+fileName+": {:.2f}%".format((i / len(listaFile))*100))
            else:
                print("Document "+fileName+" not found")
                # Memorizza i PDF che non trova
                with open(directoryPDF+"pdfNonTrovati.txt", "a") as f:
                    f.write(fileName+"\n")
    print("Done!")
