import json
import os
import re
from PIL import Image, ImageDraw


# disegna rettangoli rossi sulle annotazioni json (arancioni se sono figure)
def json_rects():
    jpeg_path = './resources/jpeg/'
    json_path = "./resources/json/samples.json"
    with open(json_path) as json_file:
        data = json.load(json_file)
        # scorre tutte le annotazioni
        for a in data['annotations']:

            # cerca il pdf pagina a cui si riferisce
            page_id = a['image_id']
            for im in data['images']:
                if page_id == im['id']:
                    file_name = im['file_name']
            file_path = jpeg_path + file_name
            bbox = a['bbox']
            # shape has the form ((x0, y0), (x1, y1))
            shape = ((bbox[0], bbox[1]), ((bbox[0] + bbox[2]), bbox[1] + bbox[3]))

            # carica l'immagine jpeg
            image = Image.open(file_path)
            if a['category_id'] == 5:
                ImageDraw.Draw(image).rectangle(shape, fill=None, outline="orange")
            else:
                ImageDraw.Draw(image).rectangle(shape, fill=None, outline="red")
            image.save(file_path)


# disegna rettangoli verdi sulle annotazioni xml
def xml_rects():
    jpeg_path = './resources/jpeg/'
    path_xml = "./resources/xml/xml_optimazed/"
    listaFile = os.listdir(path_xml)
    for i, fileXML in enumerate(listaFile):
        if fileXML.split('.')[-1] == 'xml':
            print('xml - inizio file: ' + fileXML)
            f = open(path_xml + fileXML)
            testo = (f.read())
            # ottengo tutte le bbox dei textbox
            textboxes = testo.split('</textbox>')
            for textbox in textboxes:
                if 'textbox' in textbox:
                    textbox = re.search('<textbox (.*)>', textbox).group(1)
                    textbox = re.search('bbox="(.*)"', textbox).group(1)
                    box = textbox.split(',')

                    image = Image.open(jpeg_path + fileXML.split('.')[0] + '.jpg')
                    height = int(image.size[1])
                    # shape nella forma ((x0, y0), (x1, y1))
                    shape = ((int(round(float(box[0]))), height - int(round(float(box[3])))),
                             (int(round(float(box[2]))), height - int(round(float(box[1])))))
                    ImageDraw.Draw(image).rectangle(shape, fill=None, outline="green")
                    image.save(jpeg_path + fileXML.split('.')[0] + '.jpg')


xml_rects()
json_rects()
