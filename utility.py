import os
import re
import json
from PyPDF2 import PdfFileReader, PdfFileWriter


def pdf2xml():
    pdf_path = "./resources/pdf/pdf_estratti/"
    listaFile = os.listdir(pdf_path)
    for i, pdf in enumerate(listaFile):
        pdfName, pdfExtension = pdf.split(".")
        if pdfExtension == "pdf":
            command = "pdf2txt.py -t xml " + pdf_path + pdf+" > ./resources/xml/"+pdfName+".xml"
            os.system(command)
            print("Pdf " + pdfName + " converted into XML: {:.2f}%".format((i / len(listaFile)) * 100))


def optimizeXML():
    pathXML = "./resources/xml/"
    pathXML_optimazed = "./resources/xml/xml_optimazed/"
    listaFile = os.listdir(pathXML)
    for j, fileXML in enumerate(listaFile):

        if fileXML.split('.')[-1] == 'xml':
            f = open(pathXML + fileXML)
            testo = (f.read())

            attributes = re.search('<textline (.*)>', testo)

            blocchiLine = testo.split("</textline>")
            attributes = re.search('<textline (.*)>', blocchiLine[0])
            splitLine2 = blocchiLine[0].split("<textline " + attributes.group(1) + ">")
            txtFinale = ""
            for i, splitLine in enumerate(blocchiLine):
                attributes = re.search('<textline(.*)>', splitLine)
                if attributes is not None:
                    splitLine2 = splitLine.split("<textline" + attributes.group(1) + ">")
                    blocchiCarattere = splitLine2[1].split("</text>")
                    parola = ""
                    for carattere in blocchiCarattere:
                        attributes = re.search('<text(.*)>', carattere)
                        if attributes is not None:
                            splitCarattere = carattere.split("<text" + attributes.group(1) + ">")
                            parola += splitCarattere[1]
                    txtFinale += (splitLine2[0] + parola)

            g = open(pathXML_optimazed + fileXML.split(".")[0] + ".xml", "w")
            g.write(txtFinale)
            f.close()
            g.close()
            print("XML " + fileXML + " optimazed: {:.2f}%".format((j / len(listaFile)) * 100))


def extract_pages_pdf():
    json_path = './resources/json/samples.json'
    separate_pdf_path = './resources/pdf/pdf_estratti/'
    with open(json_path) as json_file:
        data = json.load(json_file)
        for im in data['images']:
            # prende il nome del pdf e il numero di pagina
            image_name = im['file_name']
            pdf_name = image_name.split('_')[0]
            page_name = image_name.split('_')[-1].split('.')[0]
            page_number = int(page_name)

            # salva la pagina selezionata dal pdf selezionato
            name_of_split = pdf_name + '_' + page_name
            pdf_path = './resources/pdf/' + pdf_name + '.pdf'
            pdf = PdfFileReader(pdf_path)
            pdf_writer = PdfFileWriter()
            pdf_writer.addPage(pdf.getPage(page_number))
            output = f'{name_of_split}.pdf'
            with open(separate_pdf_path+output, 'wb') as output_pdf:
                pdf_writer.write(output_pdf)
