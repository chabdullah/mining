import re
import os
from os import path
import utility, downloadPDFs

# Download dei pdf a partire dai nomi dei file JPG
downloadPDFs.downloadPDFs()
# Conversione dei pdf in xml "grezzi"
utility.pdf2xml()
# Ottimizzazione dei file xml in modo da togliere l'informazione superflua (Es. bbox di ogni singolo carattere)
pathXML = "./resources/xml/"
pathXML_optimazed = "./resources/xml/xml_optimazed/"
listaFile = os.listdir(pathXML)
for j,fileXML in enumerate(listaFile):
    if path.isfile(pathXML+fileXML):
        f = open(pathXML+fileXML)
        testo = (f.read())

        attributes = re.search('<textline (.*)>', testo)

        blocchiLine = testo.split("</textline>")
        attributes = re.search('<textline (.*)>', blocchiLine[0])
        splitLine2 = blocchiLine[0].split("<textline " + attributes.group(1) + ">")
        txtFinale = ""
        for i,splitLine in enumerate(blocchiLine):
            attributes = re.search('<textline(.*)>', splitLine)
            if attributes is not None:
                splitLine2 = splitLine.split("<textline"+attributes.group(1)+">")
                blocchiCarattere = splitLine2[1].split("</text>")
                parola = ""
                for carattere in blocchiCarattere:
                    attributes = re.search('<text(.*)>', carattere)
                    if attributes is not None:
                        splitCarattere = carattere.split("<text"+attributes.group(1)+">")
                        parola += splitCarattere[1]
                txtFinale += (splitLine2[0]+parola)

        g = open(pathXML_optimazed+fileXML.split(".")[0]+".xml","w")
        g.write(txtFinale)
        f.close()
        g.close()
        print("XML " + fileXML + " optimazed: {:.2f}%".format((j / len(listaFile)) * 100))

