import json
import csv
# importing required libraries
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import patches
from pdf2image import convert_from_path
import os
from PIL import Image


#Salva i dati dei plot dal json a csv (in certo ordine/format). Si potrebbe anche evitare questa funzione e convertire il json direttamente in txt
def jsonFigures2CSV():
    with open('../keras_frcnn/data/train.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["image_names", "cell_type", "xmin", "xmax", "ymin", "ymax"])
        plot_veri_json = "./resources/json/plotVeri.json"
        with open(plot_veri_json) as json_file:
            plots = json.load(json_file)
            all_figures_json = "./resources/json/figureBboxInfo.json"
            print("All figures loaded")
            with open(all_figures_json) as all_figures:
                figures = json.load(all_figures)
                numberPlot = 0
                numberNonPlot = 0
                for i,figure in enumerate(figures):
                    if numberNonPlot >= 15000 and numberPlot >= 14848:
                        break
                    file_name = figure["file_name"]
                    bbox = figure["bbox"]
                    xMin = bbox[0]
                    yMin = bbox[1]
                    xMax = xMin + bbox[2]
                    yMax = yMin + bbox[3]
                    found = False
                    for j, plot in enumerate(plots):
                        file_name_plot = plot["file_name"]
                        bboxPlot = plot["bbox"]
                        xMinPlot = bboxPlot[0]
                        yMinPlot = bboxPlot[1]
                        xMaxPlot = xMinPlot + bboxPlot[2]
                        yMaxPlot = yMinPlot + bboxPlot[3]
                        if file_name == file_name_plot and xMin == xMinPlot and yMin == yMinPlot and xMax == xMaxPlot and yMax == yMaxPlot:
                            found = True
                            break
                        #print("Searching: {:.2f}%".format((j/len(plots))*100))
                    if found:
                        writer.writerow([file_name, "plot", xMin, xMax, yMin, yMax])
                        numberPlot += 1
                    elif numberNonPlot < 15000:
                        writer.writerow([file_name, "noPlot", xMin, xMax, yMin, yMax])
                        numberNonPlot += 1
                    print("Progress (CSV): %4.2f %%. Plot: %5d, Noplot: %5d" % (((i/len(figures))*100),numberPlot,numberNonPlot))
    # Plot e non plot totali   -->   (Plot= 14848, Non Plot = 94444)
    # cell_type sono le diverse classi (ovvero, in questo caso, plot e noPlot)
    train = pd.read_csv("../keras_frcnn/data/train.csv")
    print(train["cell_type"].value_counts())




#Converte csv in txt (Il txt verrà dato in ingresso al frcnn)
def csv2txt():
    # read the csv file using read_csv function of pandas
    train = pd.read_csv("../keras_frcnn/data/train.csv")
    train.head()
    data = pd.DataFrame()
    data['format'] = train['image_names']

    # as the images are in train_images folder, add train_images before the image name
    for i in range(data.shape[0]):
        data['format'][i] = './resources/jpg/publaynet/train/' + data['format'][i]
        print("Progress (txt_1) : {:.2f}%".format((i / data.shape[0])*100))
    # add xmin, ymin, xmax, ymax and class as per the format required
    for i in range(data.shape[0]):
        data['format'][i] = data['format'][i] + ',' + str(train['xmin'][i]) + ',' + str(train['ymin'][i]) + ',' + str(train['xmax'][i]) + ',' + str(train['ymax'][i]) + ',' + train['cell_type'][i]
        print("Progress (txt_2) : {:.2f}%".format((i / data.shape[0])*100))
    data.to_csv('./keras_frcnn/data/annotate.txt', header=None, index=None, sep=' ')


# pdf2jpg per fare i test
def pdf2jpg():
    inputPath = "./keras_frcnn/data/test/pdf/"
    outputPath = "./keras_frcnn/data/test/jpg/"
    pdfs = os.listdir(inputPath)
    for pdf in pdfs:
        pdfPath = inputPath+pdf
        pages = convert_from_path(pdfPath, 500)
        pdfName = pdf.split(".")[0]
        for i,page in enumerate(pages):
            imgPath = outputPath+pdfName+"_"+str(i)+".jpg"
            page = page.resize((612,792), Image.ANTIALIAS)
            page.save(imgPath, 'JPEG')