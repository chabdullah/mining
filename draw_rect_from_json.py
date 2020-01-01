import json
from PIL import Image, ImageDraw


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
        shape = ((bbox[0], bbox[1]), ((bbox[0]+bbox[2]), bbox[1]+bbox[3]))

        # carica l'immagine jpeg
        image = Image.open(file_path)
        ImageDraw.Draw(image).rectangle(shape, fill=None, outline="red")
        image.save(file_path)


