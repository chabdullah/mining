from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import sys, getopt
from PyPDF2 import PdfFileReader, PdfFileWriter
from subprocess import Popen, PIPE, STDOUT
import os


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
        fileExtension = pdf.split(".")[-1]
        if fileExtension == "pdf":
            fileName = pdfDir + pdf
            text = convert(fileName)  # get string of text content of pdf
            textFile = open(txtDir + pdf.split(".")[0] + '.txt', "w")  # make text file
            textFile.write(text)  # write text to text file
            textFile.close()


def main():

    pdfDir = "./"
    txtDir = "./txt/"
    convertMultiple(pdfDir, txtDir)

    return 0


if __name__ == '__main__':
    main()
