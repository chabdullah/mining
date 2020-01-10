from PIL import Image, ImageDraw
import json
import os
import re


def copy_json():
    json_path = "./resources/json/"
    json_name_original = 'samples.json'
    json_name_copy = 'modified_samples.json'
    with open(json_path + json_name_original) as json_file:
        data = json.load(json_file)
        with open(json_path + json_name_copy, 'w') as copy:
            json.dump(data, copy)


def modify_json():
    json_out_path = './resources/json/modified_samples.json'
    json_orig_path = './resources/json/samples.json'
    with open(json_orig_path, 'r') as json_orig_file:
        data = json.load(json_orig_file)
    with open(json_out_path, 'r') as json_out_file:
        final_data = json.load(json_out_file)
    # delete all annotations in the final file and create new structure
    final_data.pop('annotations', None)
    final_data['figures'] = []
    # search figures
    for a in data['annotations']:
        # if I find a figure look for caption
        if a['category_id'] == 5:
            min_dist = 10000
            caption_id = '0'
            figure_bbox = a['bbox']
            text_bbox = [0, 0, 0, 0]
            page_id = a['image_id']
            for ann in data['annotations']:
                # look for annotations on the same page of the figure
                if ann['image_id'] == page_id:
                    # check if annotation is a text (category_id == 1) and its position
                    if ann['category_id'] == 1:
                        text_bbox = ann['bbox']

                        # check position not right or left to the figure

                        if not (float(text_bbox[0]) + float(text_bbox[2]) <= float(figure_bbox[0])
                                and float(figure_bbox[0]) + float(figure_bbox[2] <= float(text_bbox[0]))):
                            # check if text is over the figure
                            if float(text_bbox[1]) + float(text_bbox[3]) <= float(figure_bbox[1]):
                                dist = float(figure_bbox[1]) - float(text_bbox[1]) - float(text_bbox[3])
                            # just to be sure... it should be below
                            elif float(figure_bbox[1]) + float(figure_bbox[3]) <= float(text_bbox[1]):
                                dist = float(text_bbox[1]) - float(figure_bbox[1]) - float(figure_bbox[3])

                            # update id of new closer text annotation
                            if dist < min_dist:
                                min_dist = dist
                                caption_id = ann['id']
                # find the selected caption
                for capt in data['annotations']:
                    if capt['id'] == caption_id:
                        text_bbox = capt['bbox']

            # save in new data structure
            final_data['figures'].append({
                'page_id': page_id,
                'figure_bbox': figure_bbox,
                'text_bbox': text_bbox,
                'id': a['id']
            })

    # save final_data
    with open(json_out_path, 'w') as json_out_file:
        json.dump(final_data, json_out_file)


def draw_captions():
    jpeg_path = './resources/jpeg/'
    json_path = "./resources/json/modified_samples.json"
    with open(json_path) as json_file:
        data = json.load(json_file)
    # scorre tutte le annotazioni
    for f in data['figures']:

        # cerca il pdf pagina a cui si riferisce
        page_id = f['page_id']
        for im in data['images']:
            if page_id == im['id']:
                file_name = im['file_name']
        file_path = jpeg_path + file_name
        figure_bbox = f['figure_bbox']
        caption_bbox = f['text_bbox']
        # shape has the form ((x0, y0), (x1, y1))
        figure_shape = ((figure_bbox[0], figure_bbox[1]), (figure_bbox[0] + figure_bbox[2]),
                        (figure_bbox[1] + figure_bbox[3]))
        caption_shape = ((caption_bbox[0], caption_bbox[1]), (caption_bbox[0] + caption_bbox[2]),
                         (caption_bbox[1] + caption_bbox[3]))

        # carica l'immagine jpeg
        image = Image.open(file_path)
        ImageDraw.Draw(image).rectangle(figure_shape, fill=None, outline="orange")
        ImageDraw.Draw(image).rectangle(caption_shape, fill=None, outline="red")
        image.save(file_path)


def find_caption_text():
    path_jpeg = './resources/jpeg/'
    path_xml = "./resources/xml/xml_optimazed/"
    path_json = './resources/json/modified_samples.json'
    with open(path_json) as json_file:
        data = json.load(json_file)

    for f in data['figures']:
        caption_bbox = f['text_bbox']
        page_id = f['page_id']
        file_name = 'NULL'
        caption_text = 'NULL'
        # get xml file name
        for p in data['images']:
            if p['id'] == page_id:
                file_name = p['file_name'].split('.')[0]

        file_xml = open(path_xml + file_name + '.xml')
        text_xml = file_xml.read()
        bboxes = text_xml.split('bbox="')[2:]
        # get page height
        page_height = float(text_xml.split('<pages>')[1].split('bbox="')[1].split('"')[0].split(',')[3])
        # find all bbox in the page
        dist = 10000
        for bbox in bboxes:
            box = bbox.split('"')[0].split(',')
            a = float(box[0])
            b = page_height - float(box[3])
            c = float(box[2]) - float(box[0])
            d = float(box[3]) - float(box[1])
            current_bbox = [a, b, c, d]
            current_dist = \
                           abs(current_bbox[0] - caption_bbox[0]) + \
                           abs(current_bbox[0] + current_bbox[2] - caption_bbox[0] - caption_bbox[2]) + \
                           abs(current_bbox[1] - caption_bbox[1]) + \
                           abs(current_bbox[1] + current_bbox[3] - caption_bbox[1] - caption_bbox[3]) 

            if current_dist < dist:
                dist = current_dist
                caption_text = bbox.split('>')[1].split('</textbox')[0]

        # create new element in json file
        f['text'] = caption_text
        print('text found for figure on page ' + file_name)

    with open(path_json, 'w') as json_file:
        json.dump(data, json_file)


find_caption_text()





