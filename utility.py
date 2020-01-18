import os
import re
import json
from PyPDF2 import PdfFileReader, PdfFileWriter
import cv2
import torchvision
from PIL import Image
import json
import torch
from NnModel import NnModel
import operator
import numpy as np
from os import listdir
from os.path import isfile, join
import pandas as pd
import itertools




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


def testFigure():
    img_size = (128,128)
    dim_descrittore = 1024
    kernel_size = 5
    #plots = [2, 3, 5, 11, 13, 17, 19, 21, 23]
    plots = [0]
    image_dataset = torchvision.datasets.ImageFolder(
        root='./resources/docFigure/data/training',
        transform=torchvision.transforms.Compose([
            torchvision.transforms.Resize(img_size),
            torchvision.transforms.ToTensor(),
        ])
    )
    #print("Train: Detected Classes are: ", image_dataset.class_to_idx)
    key_list_classes = list(image_dataset.class_to_idx.keys())
    val_list_classes = list(image_dataset.class_to_idx.values())
    image_dataset = torchvision.datasets.ImageFolder(
        root='./resources/docFigure/data/test',
        transform=torchvision.transforms.Compose([
            torchvision.transforms.Resize(img_size),
            torchvision.transforms.ToTensor(),
        ])
    )
    #print("Image's labels are: ", image_dataset.class_to_idx)
    key_list_imageLabes = list(image_dataset.class_to_idx.keys())
    val_list_imageLabes = list(image_dataset.class_to_idx.values())
    image_loader = torch.utils.data.DataLoader(
        image_dataset,
        batch_size=1,
        num_workers=0,
        shuffle=True
    )
    network = NnModel(dim_descrittore, kernel_size)
    network.load_state_dict(torch.load('./resources/docFigure/pesi/model128_2_classi.pth'))
    #print("\n"*4)

    #plotsFigures = []
    image, label = next(iter(image_loader))
    imageLabel = str(key_list_imageLabes[val_list_imageLabes.index(label.item())])
    #print("Image label: "+ imageLabel)
    predictions = {}
    for i in range(20):
        risultato = network(image)
        pred = risultato.data.max(1, keepdim=True)[1]
        pred = pred.item()
        if pred in predictions.keys():
            predictions[pred] += 1
        else:
            predictions[pred] = 1
    prediction = key_list_classes[val_list_classes.index(max(predictions.items(), key=operator.itemgetter(1))[0])]
    #print("Prediction: ",prediction)
    if max(predictions.items(), key=operator.itemgetter(1))[0] in plots:
        #print("It's a plot!")
        #plotsFigures.append({'file_name': imageLabel})
        isPlot = True
    else:
        isPlot = False
    #print("Progress: {:.2f}%".format((j / len(image_loader)) * 100))
    #print("*"*100)
    return isPlot


def extractImagesInfoIntoJson():
    pathJson = './resources/json/labels/publaynet/trainSlim.json'
    with open(pathJson, 'r') as fp:
        samples = json.load(fp)
        print("Json loaded!")

    images = []
    #numberImages = 500
    #topImages = itertools.islice(samples['images'], numberImages)
    topImages = samples['images']
    numberImages = len(samples['images'])

    for j, image in enumerate(topImages):
        for k, ann in enumerate(samples['annotations']):
            if ann['image_id'] == image['id']:
                images.append({'id': ann['image_id'], 'file_name': image['file_name'], 'bbox': ann['bbox']})
        print("Finding figures: {:.2f}%".format((j/numberImages)*100))
    print("Figures found: ",len(images))
    with open('./resources/json/figureBboxInfo.json', 'w') as fp:
        json.dump(images, fp)


def extractCroppedFigures():
    with open('./resources/json/figureBboxInfo.json', 'r') as fp:
        figures = json.load(fp)
        pathJpg = './resources/jpg/publaynet/train/'
        plots = []
        for i, figure in enumerate(figures):
            pathFile = pathJpg + figure['file_name']
            if os.path.isfile(pathFile) and  os.path.exists(pathFile):
                img = cv2.imread(pathFile)
                x = int(figure['bbox'][0])
                y = int(figure['bbox'][1])
                width = int(figure['bbox'][2])
                height = int(figure['bbox'][3])
                crop_img = img[y:y + height, x:x + width]
                name = figure["file_name"].split(".")[0]
                pathFile = "./resources/docFigure/data/test/"+name+"/"
                if not os.path.exists(pathFile):
                    os.makedirs(pathFile)
                pathFile += figure['file_name']
                #print(pathFile)
                try:
                    cv2.imwrite(pathFile, crop_img)
                    #print("Testing figure....")
                    isPlot = testFigure()
                    if isPlot:
                        plots.append(figure)
                    command = "rm -r ./resources/docFigure/data/test/"
                    os.system(command)
                    print("Figures tested: {:.2f}%".format((i / len(figures)) * 100))
                except:
                    command = "rm -r ./resources/docFigure/data/test/"
                    os.system(command)
                    print("Figures tested (not found): {:.2f}%".format((i / len(figures)) * 100))
        with open('./resources/json/plotVeri.json', 'w') as fp:
            json.dump(plots, fp)



def slimJson():
    pathJson = './resources/examples/samples.json'
    with open(pathJson, 'r') as fp:
        samples = json.load(fp)
        for i,key in enumerate(samples["annotations"]):
            if key["category_id"] == 5:
                del key["segmentation"]
                del key["iscrowd"]
                del key["id"]
                del key["area"]
                del key["category_id"]
            else:
                del key["segmentation"]
                del key["iscrowd"]
                del key["id"]
                del key["area"]
                del key["image_id"]
                del key["bbox"]
                del key["category_id"]
        newAnnotations = {"annotations":[i for i in samples["annotations"] if i]}
        del samples["annotations"]
        samples = {**samples, **newAnnotations}
        with open('./resources/json/magro.json', 'w') as fp:
            json.dump(samples, fp)


#Non più necessario al momento
def testResults():
    with open('./resources/json/plotsFigures.json', 'r') as fp:
        plots = json.load(fp)
        for i, plot in enumerate(plots):
            command = "cp ./resources/docFigure/data/test/"+plot['file_name']+"/"+plot['file_name']+".jpg ./resources/jpg/predictedPlots"
            os.system(command)
            print("Copying the result of the predictions: {:.2f}%".format((i/len(plots))))


def showPlotsPages():
    with open('./resources/json/plotVeri.json', 'r') as fp:
        plots = json.load(fp)
        # for i, plot in enumerate(plots):
        #     command = "cp ./resources/jpg/publaynet/train/"+plot['file_name']+" ./resources/jpg/predictedPages/"
        #     os.system(command)
        #     print("Copying the result of the predictions: {:.2f}%".format((i/len(plots))*100))
        with open('./resources/json/figureBboxInfo.json', 'r') as f:
            figures = json.load(f)
            for i, figure in enumerate(figures):
                command = "cp ./resources/jpg/publaynet/train/"+figure['file_name']+" ./resources/jpg/otherPages/"
                os.system(command)
                print("Copying other images: {:.2f}%".format((i/len(plots))*100))
            for i, plot in enumerate(plots):
                command = "rm ./resources/jpg/otherPages/" + plot['file_name']
                os.system(command)
                print("Cleaning: {:.2f}%".format((i / len(plots)) * 100))


def blackPixelTreshold():
    pixelTreshold = 1500
    jpgPath = "./resources/examples/sbiancate/"
    images = os.listdir(jpgPath)

    for img in images:
        imgPath = jpgPath + img
        image = cv2.imread(imgPath)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Set threshold level
        threshold_level = 200

        # Find coordinates of all pixels below threshold
        coords = np.column_stack(np.where(gray < threshold_level))

        # print(len(coords))
        if len(coords) > pixelTreshold:
            # Create mask of all pixels lower than threshold level
            mask = gray < threshold_level

            # Color the pixels in the mask
            image[mask] = (204, 119, 0)

            cv2.imshow('image', image)
            cv2.waitKey()



#slimJson()
#extractImagesInfoIntoJson()
#extractCroppedFigures()
#testResults()
#showPlotsPages()

