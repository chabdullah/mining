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
from os import listdir
from os.path import isfile, join
import pandas as pd



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
    plots = [2, 3,5, 11, 13, 17, 19, 21, 23]
    image_dataset = torchvision.datasets.ImageFolder(
        root='./resources/docFigure/data/training',
        transform=torchvision.transforms.Compose([
            torchvision.transforms.Resize(img_size),
            torchvision.transforms.ToTensor(),
        ])
    )
    print("Train: Detected Classes are: ", image_dataset.class_to_idx)
    key_list_classes = list(image_dataset.class_to_idx.keys())
    val_list_classes = list(image_dataset.class_to_idx.values())
    image_dataset = torchvision.datasets.ImageFolder(
        root='./resources/docFigure/data/test',
        transform=torchvision.transforms.Compose([
            torchvision.transforms.Resize(img_size),
            torchvision.transforms.ToTensor(),
        ])
    )
    print("Image's labels are: ", image_dataset.class_to_idx)
    key_list_imageLabes = list(image_dataset.class_to_idx.keys())
    val_list_imageLabes = list(image_dataset.class_to_idx.values())
    image_loader = torch.utils.data.DataLoader(
        image_dataset,
        batch_size=1,
        num_workers=0,
        shuffle=True
    )
    network = NnModel(dim_descrittore, kernel_size)
    network.load_state_dict(torch.load('./resources/docFigure/pesi/model128_2.pth'))
    print("\n"*4)
    for image, label in image_loader:
        print("Image label: "+str(key_list_imageLabes[val_list_imageLabes.index(label.item())]))
        predictions = {}
        for i in range(100):
            risultato = network(image)
            pred = risultato.data.max(1, keepdim=True)[1]
            pred = pred.item()
            if pred in predictions.keys():
                predictions[pred] += 1
            else:
                predictions[pred] = 1
        prediction = key_list_classes[val_list_classes.index(max(predictions.items(), key=operator.itemgetter(1))[0])]
        print("Prediction: ",prediction)
        if max(predictions.items(), key=operator.itemgetter(1))[0] in plots:
            print("It's a plot!")
        print("*"*100)


def extractImagesFromJpg():
    pathJson = './resources/json/labels/publaynet/trainSlim.json'
    with open(pathJson, 'r') as fp:
        samples = json.load(fp)
        print("Json loaded!")

    images = []
    for j, image in enumerate(samples['images']):
        for ann in samples['annotations']:
            if ann['image_id'] == image['id']:
                if ann['category_id'] == 5:
                    images.append({'id': ann['image_id'], 'file_name': image['file_name'], 'bbox': ann['bbox']})
                    #del
        print("Image progress: {:.2f}%".format((j/len(samples["images"]))*100))
    pathJpg = './resources/jpg/train/'
    for i, image in enumerate(images):
        pathFile = pathJpg + image['file_name']
        if os.path.isfile(pathFile):
            img = cv2.imread(pathFile)
            x = int(image['bbox'][0])
            y = int(image['bbox'][1])
            width = int(image['bbox'][2])
            height = int(image['bbox'][3])
            crop_img = img[y:y + height, x:x + width]
            name = image["file_name"].split("_")[0]
            pathFile = "./resources/docFigure/data/test/"+name+"/"
            if not os.path.exists(pathFile):
                os.makedirs(pathFile)
            pathFile += image['file_name']
            cv2.imwrite(pathFile, crop_img)
            print("Cropping progress: {:.2f}%".format((i / len(images)) * 100))

    with open('./resources/json/figureBboxInfo.json', 'w') as fp:
        json.dump(images, fp)


def slimJson():
    pathJson = './resources/examples/samples.json'
    with open(pathJson, 'r') as fp:
        samples = json.load(fp)
        for key in samples["annotations"]:
            del key["segmentation"]
            del key["iscrowd"]
            del key["id"]
            del key["area"]
        with open('./resources/json/magro.json', 'w') as fp:
            json.dump(samples, fp)


#extractImagesFromJpg()
#testFigure()

#pathJson = './resources/json/labels/publaynet/'
#df = pd.read_json (r'./resources/json/labels/publaynet/train.json')

#files = [f for f in listdir("./resources/jpg/train/") if isfile(join("./resources/jpg/train/", f))]
#print(files)

pathJson = './resources/examples/samples.json'
with open(pathJson, 'r') as fp:
    samples = json.load(fp)
    annotation = samples["annotations"]
    print(len(annotation))
    print(annotation)
    for i,obj in enumerate(annotation):
        del samples[obj]
    print(annotation)
    #print(samples)