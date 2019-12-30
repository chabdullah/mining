import os


def pdf2xml():
    listaFile = os.listdir("./resources/pdf")
    for i,pdf in enumerate(listaFile):
        pdfName, pdfExtension = pdf.split(".")
        if pdfExtension == "pdf":
            command = "pdf2txt.py -t xml ./resources/pdf/"+pdf+" > ./resources/xml/"+pdfName+".xml"
            os.system(command)
            print("Pdf " + pdfName + " converted into XML: {:.2f}%".format((i / len(listaFile)) * 100))