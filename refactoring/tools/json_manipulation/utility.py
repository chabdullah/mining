import json
import os


# copy json file
def copy_json(original_path, final_path):
    with open(original_path) as json_file:
        data = json.load(json_file)
    with open(final_path, 'w') as copy:
        json.dump(data, copy)


def find_sector(id_page, annotations):
    a = 0
    beginned = False
    index_first = 0
    index_last = 0
    for ann in annotations:
        if ann['image_id'] == id_page and not beginned:
            index_first = a
            beginned = True
        if ann['image_id'] != id_page and beginned:
            index_last = a
            beginned = False
            break
        a = a + 1
    # for the case of the last element
    if beginned:
        index_last = a

    return index_first, index_last


def find_figures(first, last, annotations):
    founded_figures_id_bbox = []
    for a in range(first, last):
        if annotations[a]['category_id'] == 5:
            founded_figures_id_bbox.append((annotations[a]['id'], annotations[a]['bbox']))

    return founded_figures_id_bbox


def create_figure_element_json(founded_figures_id_bbox, first, last, annotations):
    figures = []
    # create the jason data for each figure
    for id_bbox_figure in founded_figures_id_bbox:
        min_dist = 10000
        caption_pos = '-1'
        figure_bbox = id_bbox_figure[1]
        # look for its caption
        for a in range(first, last):
            # check only for texts
            if annotations[a]['category_id'] == 1:
                text_bbox = annotations[a]['bbox']

                # check the text is not the side text
                if not (float(text_bbox[0]) + float(text_bbox[2]) <= float(figure_bbox[0])
                        and float(figure_bbox[0]) + float(figure_bbox[2] <= float(text_bbox[0]))):
                    # check if text is over the figure
                    if float(text_bbox[1]) + float(text_bbox[3]) <= float(figure_bbox[1]):
                        dist = float(figure_bbox[1]) - float(text_bbox[1]) - float(text_bbox[3])
                    # just to be sure... it should be below
                    elif float(figure_bbox[1]) + float(figure_bbox[3]) <= float(text_bbox[1]):
                        dist = float(text_bbox[1]) - float(figure_bbox[1]) - float(figure_bbox[3])
                    else:
                        print('errore! distanza calcolata male')
                        dist = 1000

                    # update id of new closer text annotation
                    if dist < min_dist:
                        min_dist = dist
                        caption_pos = a

        # add this figure to final_data, id equal to its caption
        figure = {
            'id': annotations[caption_pos]['id'],
            'figure_bbox': id_bbox_figure[1],
            'caption_bbox': annotations[caption_pos]['bbox']
        }
        figures.append(figure)

    return figures


# if there are figures
def create_annotation_element_json_from_figs(first, last, figures, all_annotations):
    captions_id = [fig['id'] for fig in figures]
    annotations = []
    for a in range(first, last):
        if all_annotations[a]['category_id'] != 5 and (all_annotations[a]['id'] not in captions_id):
            annotation = {
                'id': all_annotations[a]['id'],
                'bbox': all_annotations[a]['bbox']
            }
            annotations.append(annotation)

    return annotations


# if there are not figures
def create_annotation_element_json(first, last, all_annotations):
    annotations = []
    for a in range(first, last):
        annotation = {
            'id': all_annotations[a]['id'],
            'bbox': all_annotations[a]['bbox']
        }
        annotations.append(annotation)

    return annotations


# create new json with our structure
def create_json(json_path):
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
    final_data = {'images': []}

    # group by images
    i = 0
    for im in data['images']:

        # identify the sector of the dataset with the wanted annotations
        index_first, index_last = find_sector(im['id'], data['annotations'])

        # look for figures and save id and bbox
        founded_figures_id_bbox = find_figures(index_first, index_last, data['annotations'])

        figures = []
        if len(founded_figures_id_bbox) != 0:
            # look for captions
            figures = create_figure_element_json(founded_figures_id_bbox, index_first, index_last, data['annotations'])

            # look for remained annotations
            annotations = create_annotation_element_json_from_figs(index_first, index_last, figures, data['annotations'])

        # all annotations are normal
        else:
            annotations = create_annotation_element_json(index_first, index_last, data['annotations'])

        image = {
            'file_name': im['file_name'],
            'height': im['height'],
            'width': im['width'],
            'figures': figures,
            'annotations': annotations
        }
        final_data['images'].append(image)

        i = i + 1

    return final_data


# TODO call this from external file
refactoring_path = os.path.dirname(os.path.dirname(os.getcwd()))
final = create_json(refactoring_path + '/resources/json/samples.json')
with open('data.json', 'w') as outfile:
    json.dump(final, outfile)


# TODO delete this
"""
def find_caption_block(json_path='./resources/json/restructured_samples.json'):
    with open(json_path, 'r') as json_orig_file:
        data = json.load(json_orig_file)
    final_data = data.copy()
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
    with open(json_path, 'w') as json_out_file:
        json.dump(final_data, json_out_file)
"""