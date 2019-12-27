from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import os
import sys, getopt
from PyPDF2 import PdfFileReader, PdfFileWriter
from subprocess import Popen, PIPE, STDOUT




#def calcolateCoordinates():



# converts pdf, returns its text content as a string
def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text


def convertMultiple(pdfDir, txtDir):
    if pdfDir == "":
        pdfDir = os.getcwd() + "\\"  # if no pdfDir passed in
    for pdf in os.listdir(pdfDir):  # iterate through pdfs in pdf directory
        fileExtension = pdf.split(".")
        if fileExtension == "pdf":
            #text = convert(pdfFilename)  # get string of text content of pdf
            page = 2
            x = 50
            y = 257
            width = 240
            height = 43
            command = 'java -jar ./PDF/extract.jar ./PDF/IJOTO2014-835790.pdf '+str(page)+' '+str(x)+' '+str(y)+' '+str(width)+' '+str(height)+'  > '+txtDir+pdf+'.txt'
            os.system(command)
            #textFilename = txtDir + pdf + ".txt"
            #textFile = open(textFilename, "w")  # make text file
            #textFile.write(text)  # write text to text file
            #textFile.close


#Crop PDF
# reader = PdfFileReader('./PDF/sample.pdf','r')
# page = reader.getPage(0)
#
# writer = PdfFileWriter()
# page.mediaBox.setLowerLeft((180,0))
# page.mediaBox.setUpperRight((380,500))
# print(page.extractText())
#
# writer.addPage(page)
#
# outstream = open('./PDF/cropped/sample_cropped.pdf', 'wb')
# writer.write(outstream)
# outstream.close()
#
pdfDir = "./PDF/"
txtDir = "./txt/"
convertMultiple(pdfDir, txtDir)




#Per ora non servono
#reader = PdfFileReader('./PDF/sample.pdf','r')
#pdfPages = reader.getNumPages()
#page = reader.getPage(0)
