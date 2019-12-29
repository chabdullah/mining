import requests
import os
import urllib.request, urllib.error, urllib.parse
from urllib.error import URLError, HTTPError


directoryPDF = "./resources/pdf/"


# Per tenere traccia di tutti i pdf che non vengono scaricati
with open(directoryPDF+"pdfNonTrovati.txt", "w") as f:
    f.write("Pdf non trovati:\n")


listaFile = os.listdir("./resources/examples")
for i,file in enumerate(listaFile):
    fileName = file.split("_")[0]
    fileExtention = file.split(".")[1]
    if fileExtention == "jpg":
        goodUrl = False
        try:
            url = "http://europepmc.org/backend/ptpmcrender.fcgi?accid=" + fileName + "&blobtype=pdf" #Primo URL per cercare i PDF
            response = urllib.request.urlopen(url)
            goodUrl = True
        except:
            print("Document "+fileName+" does not exist in http://europepmc.org")
            try:
                print("Try https://www.ncbi.nlm.nih.gov")
                # Purtroppo se provo a fare una richiesta http (come sopra) vengo bloccato e non mi da alcuna rispota (viene lanciata un'eccezione)
                # TODO: O non si fa niente o si trova un altro modo per scaricare questo documento che non era presente nel primo url
            except:
                print("Document " + fileName + " does not exist in https://www.ncbi.nlm.nih.gov")
        #Scarica solo se è stato trovato un buon URL da dove scaricare il PDF
        if goodUrl:
            webContent = response.read()
            f = open(directoryPDF + fileName + ".pdf", "wb")
            f.write(webContent)
            f.close()
            print("Download: {:.2f}%".format(i / len(listaFile)))
        else:
            print("Document "+fileName+" not found")
            with open(directoryPDF+"pdfNonTrovati.txt","a") as f:
                f.write(fileName+"\n")
print("Done")