import json
import csv
# importing required libraries
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import patches
from pdf2image import convert_from_path
import os
from PIL import Image, ImageDraw
from shapely.geometry import Polygon

#Salva i dati dei plot dal json a csv (in certo ordine/format). Si potrebbe anche evitare questa funzione e convertire il json direttamente in txt
def jsonFigures2CSV():
    with open('./keras_frcnn/data/train.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["image_names", "cell_type", "xmin", "xmax", "ymin", "ymax"])

        ''''
        with open("./keras_frcnn/data/annotation_augmentation.txt","r") as f:
            augmentated_figures = f.read()
            augmentated_figures = augmentated_figures.split("\n")
            for i in range(len(augmentated_figures)-1):
                print(augmentated_figures[i])
                file_name = augmentated_figures[i].split(",")[0]
                xMinPlot = augmentated_figures[i].split(",")[1]
                yMinPlot = augmentated_figures[i].split(",")[2]
                xMaxPlot = xMinPlot + augmentated_figures[i].split(",")[3]
                yMaxPlot = yMinPlot + augmentated_figures[i].split(",")[4]
                category = augmentated_figures[i].split(",")[5]
                writer.writerow([file_name, category, xMinPlot, xMaxPlot, yMinPlot, yMaxPlot])
        '''
        plot_veri_json = "./resources/json/plotVeri_originali.json"
        with open(plot_veri_json) as json_file:
            plots = json.load(json_file)
            all_figures_json = "./resources/json/figureBboxInfo.json"
            print("All figures loaded")
            with open(all_figures_json) as all_figures:
                figures = json.load(all_figures)
                numberPlot = 0
                numberNonPlot = 0
                for i,figure in enumerate(figures):
                    #if numberNonPlot >= 15000 and numberPlot >= 9632:
                        #break
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
    train = pd.read_csv("./keras_frcnn/data/train.csv")
    print(train["cell_type"].value_counts())



#Converte csv in txt (Il txt verrà dato in ingresso al frcnn)
def csv2txt():
    # read the csv file using read_csv function of pandas
    train = pd.read_csv("./keras_frcnn/data/train.csv")
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



#Serve in trainB per fare il 5 fold cross validation
def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts]
             for i in range(wanted_parts) ]


#Prima utilizzo frcnn_data.py per estrarre 10K plo e 10K noPlot e li salvo in annotate.txt
#Dopodichè estraggo 8K plot e noPlot e li salvo in trainB.txt
def trainPuliti():
    with open("./keras_frcnn/data/annotate_puliti.txt", "r") as f:
        annotates = f.read()
        annotates = annotates.split("\n")
        testIndexes = split_list(range(10000), wanted_parts=5)
        print(len(annotates))


        plotTrain = ""
        noPlotTrain = ""
        for ann_number,annotate in enumerate(annotates):
            if annotate != "":
                if annotate.split(",")[5] == "plot":
                     plotTrain += annotate+"\n"
                else:
                     noPlotTrain += annotate+"\n"

        plotTrain = plotTrain.split("\n")
        noPlotTrain = noPlotTrain.split("\n")
        for i,_ in enumerate(testIndexes):
            print(testIndexes[i])
            n_Plot = 0
            n_noPlot = 0
            n_test = 0
            train = ""
            test = ""
            for j,plt in enumerate(plotTrain):
                if j not in testIndexes[i]:
                    train += plt + "\n"
                    n_Plot+=1
                else:
                    test += plt + "\n"
                    n_test += 1

            for k,plt in enumerate(noPlotTrain):
                if k not in testIndexes[i]:
                    train += plt + "\n"
                    n_noPlot+=1
                else:
                    test += plt + "\n"
                    n_test += 1

            print(n_Plot)
            print(n_noPlot)
            print(n_test)
            print("*" * 10)

            trainB_path = "./keras_frcnn/data/ffcv/trainB_"+str(i)+".txt"
            testB_path = "./keras_frcnn/data/ffcv/testB_"+str(i)+".txt"
            with open(trainB_path, "w") as fp:
                fp.write(train)
            with open(testB_path, "w") as fp:
                fp.write(test)


def trainSporchi():
    with open("./keras_frcnn/data/annotate_sporchi.txt", "r") as f:
        annotates = f.read()
        annotates = annotates.split("\n")
        testIndexes = split_list(range(10000), wanted_parts=5)
        print(len(annotates))


        plotTrain = ""
        noPlotTrain = ""
        for ann_number,annotate in enumerate(annotates):
            if annotate != "":
                if annotate.split(",")[5] == "plot":
                     plotTrain += annotate+"\n"
                else:
                     noPlotTrain += annotate+"\n"

        plotTrain = plotTrain.split("\n")
        noPlotTrain = noPlotTrain.split("\n")
        for i,_ in enumerate(testIndexes):
            print(testIndexes[i])
            n_Plot = 0
            n_noPlot = 0
            train = ""
            for j,plt in enumerate(plotTrain):
                if j not in testIndexes[i]:
                    train += plt + "\n"
                    n_Plot+=1

            for k,plt in enumerate(noPlotTrain):
                if k not in testIndexes[i]:
                    train += plt + "\n"
                    n_noPlot+=1

            print(n_Plot)
            print(n_noPlot)
            print("*" * 10)

            trainB_path = "./keras_frcnn/data/ffcv/trainA_"+str(i)+".txt"
            testB_path = "./keras_frcnn/data/ffcv/testA_"+str(i)+".txt"
            with open(trainB_path, "w") as fp:
                fp.write(train)




#AUGMENTATION prima di fare training
def stamp_augmentation(category):
    widthLimit = 200
    with open("./resources/json/noPlot.txt", "r") as f:
        figures = f.read()
        figures = figures.split("\n")
        stamps = os.listdir("./resources/docFigure/data/training/" + category + "/")
        stamp_augmentation = ""

        count_stamps = 0
        i = 0
        for j, stamp in enumerate(stamps):
            stamp_img = Image.open('./resources/docFigure/data/training/' + category + '/' + stamp)
            width_plot, height_plot = stamp_img.size

            while i < len(figures):
                figure_name = figures[i].split(",")[0]
                if os.path.exists(figure_name):
                    background = Image.open(figure_name)
                    x_figure = int(float(figures[i].split(",")[1]))
                    y_figure = int(float(figures[i].split(",")[2]))
                    width_figure = int(float(figures[i].split(",")[3])) - x_figure
                    height_figure = int(float(figures[i].split(",")[4])) - y_figure
                    if width_figure < width_plot and height_figure < height_plot and width_figure != 0 and height_figure != 0 and (width_plot-width_figure) < widthLimit:
                        stamp_img = stamp_img.resize((width_figure, height_figure))
                        background.paste(stamp_img, (x_figure, y_figure))
                        if not stamp.endswith('.png'):
                            stamp += ".png"
                        background.save("./resources/jpg/stamps/"+stamp)
                        stamp_augmentation += "./resources/jpg/stamps/" + stamp + "," + str(
                            x_figure) + "," + str(y_figure) + "," + str(x_figure + width_figure) + "," + str(y_figure + height_figure) + "," + category + "\n"
                        print(category + " saved: ", j)
                        widthLimit = 200
                        count_stamps += 1
                        break
                i += 1
                if i == len(figures)-1:
                    i = 0
                    widthLimit += 100
            if count_stamps == 5412:
                break
        with open("./keras_frcnn/data/augmentation/stamp_"+category+"_augmentation.txt", "w") as fp:
            fp.write(stamp_augmentation)


#Unisce annotate.txt (pulito o sporco) con l'augmentation dei plot e noPlot
def final_annotation():
    #with open("./keras_frcnn/data/annotate_puliti.txt", "r") as f1:
    with open("./keras_frcnn/data/annotate.txt", "r") as f1:
        with open("./keras_frcnn/data/augmentation_pulito/stamp_plot_augmentation.txt", "r") as f2:
            with open("./keras_frcnn/data/augmentation_pulito/stamp_noPlot_augmentation.txt", "r") as f3:
                all = f1.read()
                plot_augmentation = f2.read()
                noPlot_augmentation = f3.read()
                all = all.split("\n")
                plot_augmentation = plot_augmentation.split("\n")
                noPlot_augmentation = noPlot_augmentation.split("\n")

                final_annotation = ""
                for figure in all:
                    final_annotation += figure + "\n"
                for figure in plot_augmentation:
                    final_annotation += figure + "\n"
                for figure in noPlot_augmentation:
                    final_annotation += figure + "\n"
                with open("./keras_frcnn/data/augmentation_sporco/annotate_augmentated_sporchi.txt", "w") as f:
                    f.write(final_annotation)


def split_final_annotation():
    with open("./keras_frcnn/data/augmentation_sporco/annotate_augmentated_sporchi.txt", "r") as f:
        documents = f.read()
        documents = documents.split("\n")
        n_test_plot = 0
        n_test_noPlot = 0
        test = ""
        train = ""

        for document in documents:
            if n_test_noPlot <= 2000 and document.split(",")[5] == "noPlot":
                test += document + "\n"
                n_test_noPlot += 1
            elif n_test_plot <= 2000 and document.split(",")[5] == "plot":
                test += document + "\n"
                n_test_plot += 1
            else:
                train += document + "\n"
        with open("./keras_frcnn/data/augmentation_sporco/annotate_augmentated_train.txt", "w") as f2:
            f2.write(train)
        with open("./keras_frcnn/data/augmentation_sporco/annotate_augmentated_test.txt", "w") as f2:
            f2.write(test)



#TODO Le funzioni sotto per fare augmentation sono molto "sporche" e potrebbero essere eliminate
#Estrae informazioni dei bbox delle figure predette come no plot dalla prima rete
def extractNoPlots():
    with open('./keras_frcnn/data/annotate.txt','r') as f:
        data = f.read()
        data = data.split("\n")
        noPlot = ""
        for i in range(len(data)-1):
            info = data[i].split(",")[5]
            if info ==  "noPlot":
                noPlot += data[i] + "\n"
        with open("./resources/json/noPlot.txt", "w") as fp:
            fp.write(noPlot)


def annotation_augmentation():
    with open("./resources/json/noPlot.txt", "r") as f:
        data = f.read()
        data = data.split("\n")
        plots = os.listdir("./resources/docFigure/data/training/Graph_plots")
        annotation_augmentation = ""
        j=0
        i=0
        while (i != len(plots) - 1):
            backgroundPath = data[j].split(",")[0]
            x = float(data[j].split(",")[1])
            y = float(data[j].split(",")[2])
            width = float(data[j].split(",")[3]) - x
            height = float(data[j].split(",")[4]) - y
            if os.path.exists(backgroundPath):
                background = Image.open(backgroundPath)
                plot = Image.open('./resources/docFigure/data/training/Graph_plots/'+plots[i])
                widthPlot, heightPlot = plot.size
                x = int(x)
                y = int(y)
                width = int(width)
                height = int(height)
                #print("Width: ",width," Height: ",height)
                if width < widthPlot and height < heightPlot and width!=0 and height!=0:
                    plot = plot.resize((width,height))
                    background.paste(plot, (x, y))
                    background.save("./resources/jpg/frcnn_augmentation/"+str(i)+".png")
                    annotation_augmentation += "./resources/jpg/frcnn_augmentation/"+str(i)+".png,"+str(x)+","+str(y)+","+str(x+width)+","+str(y+height)+",plot\n"
                    print("Images saved: ",i)
                else:
                    i-=1
            else:
                i-=1
            j+=1
            i+=1
            if j==len(data)-1:
                j=0
        with open("./keras_frcnn/data/annotation_augmentation.txt","w") as fp:
            fp.write(annotation_augmentation)



def newPlotVeri():
    with open("./resources/json/plotVeri_origianli.json","r") as f:
        plot_originali = json.load(f)
        plotVeri_nuovi = []
        for plot in plot_originali:
            plot_name = plot["file_name"]
            path = "./resources/jpg/networkPredictions/predictedPagesAnnotated/"+plot_name
            if os.path.exists(path):
                plotVeri_nuovi.append(plot)
            else:
                print(plot_name)
        with open("./resources/json/plotVeri.json","w") as fp:
            json.dump(plotVeri_nuovi,fp)


#Unisce annotation_augmenttion.txt a annotate.txt
def augmentAnnotationTxt():
    with open("./keras_frcnn/data/annotate.txt", "a") as f:
        with open("./keras_frcnn/data/annotation_augmentation.txt", "r") as fp:
            augmentations = fp.read()
            augmentations = augmentations.split("\n")
            for augmentation in augmentations:
                f.write(augmentation+"\n")




### Five Fold Cross Validation ###

#Serve in trainB per fare il 5 fold cross validation
def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts]
             for i in range(wanted_parts) ]


#Prima utilizzo frcnn_data.py per estrarre 10K plo e 10K noPlot e li salvo in annotate.txt
#Dopodichè estraggo 8K plot e noPlot e li salvo in trainB.txt
def trainPuliti():
    with open("./keras_frcnn/data/annotate.txt", "r") as f:
        annotates = f.read()
        annotates = annotates.split("\n")
        plotTrain=""
        plotTest=""
        noPlotTrain=""
        noPlotTest=""
        n_Plot = 0
        n_noPlot = 0
        testIndexes = split_list(range(10000), wanted_parts=5)

        for i,_ in enumerate(testIndexes):
            for annotate in annotates:
                if annotate != "":
                    if annotate.split(",")[5] == "plot":
                        if n_Plot in testIndexes[i]:
                            plotTrain += annotate+"\n"
                            n_Plot+=1
                        else:
                            plotTest += annotate+"\n"

                    else:
                        if n_noPlot in testIndexes[i]:
                            noPlotTrain += annotate+"\n"
                            n_noPlot+=1
                        else:
                            noPlotTest += annotate+"\n"
            trainB_path = "./keras_frcnn/data/ffcv/trainB_"+str(i)+".txt"
            testB_path = "./keras_frcnn/data/ffcv/testnB_"+str(i)+".txt"
            with open(trainB_path, "w") as fp:
                fp.write(plotTrain)
                fp.write(noPlotTrain)
            with open(testB_path, "w") as fp:
                fp.write(plotTest)
                fp.write(noPlotTest)


#### TEST ####
# pdf2jpg per fare i test con il frcnn
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




#https://stackoverflow.com/questions/25349178/calculating-percentage-of-bounding-box-overlap-for-image-detector-evaluation
def calculate_iou(box_1, box_2):
    poly_1 = Polygon(box_1)
    poly_2 = Polygon(box_2)
    #iou = poly_1.intersection(poly_2).area / poly_1.union(poly_2).area
    iou = poly_1.intersection(poly_2).area / poly_1.area
    return iou


def overlappingBbox():
    draw = Image.new('RGB', (1080, 720))

    xMin = 55
    yMin = 87
    xMax = 296
    yMax = 226

    box_1 = [[xMin, yMin], [xMax, yMin], [xMax, yMax], [xMin, yMax]]
    ImageDraw.Draw(draw).rectangle(((xMin, yMin), (xMax, yMax)), fill=None, outline="red")

    xMin = 65
    yMin = 81
    xMax = 522
    yMax = 261

    box_2 = [[xMin, yMin], [xMax, yMin], [xMax, yMax], [xMin, yMax]]
    ImageDraw.Draw(draw).rectangle(((xMin, yMin), (xMax, yMax)), fill=None, outline="blue")

    draw.show()

    print(calculate_iou(box_1, box_2))



def prepareTestJPG():
    with open("./keras_frcnn/data/ffcv/testB_0.txt", "r") as f:
        testFiles = f.read()
        testFiles = testFiles.split("\n")
        for file in testFiles:
            fileSrc = file.split(",")[0]
            if fileSrc != "":
                command = "cp "+fileSrc + " ./keras_frcnn/data/test/jpg/"
                os.system(command)


def frcnnTestAccuracy(results_imgs):
    sum_accuracy = 0
    n_pages = 0
    with open("./keras_frcnn/data/test/"+results_imgs+"/bboxTrovati.txt", "r") as f1:
        with open("./keras_frcnn/data/ffcv/testB_0.txt", "r")as f2:
            bbox_trovati = f1.read()
            bbox_trovati = bbox_trovati.split("\n")
            bbox_trovati.pop(-1)

            test_pages = f2.read()
            test_pages = test_pages.split("\n")

            i = 0
            while len(test_pages) != 0:
                try:
                    if test_pages[i] != "" and test_pages[i].split(",")[5] == "plot":
                        test_name = test_pages[i].split(",")[0].split("/")[5]
                        #try:
                            #draw = Image.open("./resources/jpg/publaynet/train/"+test_name)
                        #except:
                        draw = Image.new('RGB', (1080, 720))
                        xMin = int(float(test_pages[i].split(",")[1]))
                        yMin = int(float(test_pages[i].split(",")[2]))
                        xMax = int(float(test_pages[i].split(",")[3]))
                        yMax = int(float(test_pages[i].split(",")[4]))
                        test_pages.pop(0)
                        box = [[xMin, yMin], [xMax, yMin], [xMax, yMax], [xMin, yMax]]
                        poly_1 = Polygon(box)
                        ImageDraw.Draw(draw).rectangle(((xMin, yMin), (xMax, yMax)), fill=None, outline="green", width=2)
                        #print("Page: ", test_name)
                        #print("First poly area: ", poly_1.area)

                        for j, other_test_page in enumerate(test_pages):
                            if other_test_page != "" and test_name == other_test_page.split(",")[0].split("/")[5] and other_test_page.split(",")[5] == "plot":
                                xMin_ous = int(float(other_test_page.split(",")[1]))
                                yMin_ous = int(float(other_test_page.split(",")[2]))
                                xMax_ous = int(float(other_test_page.split(",")[3]))
                                yMax_ous = int(float(other_test_page.split(",")[4]))
                                box = [[xMin_ous, yMin_ous], [xMax_ous, yMin_ous], [xMax_ous, yMax_ous], [xMin_ous, yMax_ous]]
                                poly_ous = Polygon(box)
                                ImageDraw.Draw(draw).rectangle(((xMin_ous, yMin_ous), (xMax_ous, yMax_ous)), fill=None, outline="green", width=2)
                                poly_1 = poly_1.union(poly_ous)

                        poly_2 = Polygon([[0, 0], [0, 0], [0, 0], [0, 0]])
                        for j, page in enumerate(bbox_trovati):
                            name_ous = page.split(",")[0].split(".")[0]+".jpg"
                            if test_name == name_ous:
                                xMin_ous = int(page.split(",")[1])
                                yMin_ous = int(page.split(",")[2])
                                xMax_ous = int(page.split(",")[3])
                                yMax_ous = int(page.split(",")[4])
                                box = [[xMin_ous, yMin_ous], [xMax_ous, yMin_ous], [xMax_ous, yMax_ous], [xMin_ous, yMax_ous]]
                                poly_ous = Polygon(box)
                                ImageDraw.Draw(draw).rectangle(((xMin_ous, yMin_ous), (xMax_ous, yMax_ous)), fill=None, outline="red", width=2)
                                poly_2 = poly_2.union(poly_ous)
                                print("Trovato")

                        draw.save("./keras_frcnn/data/test/" + results_imgs + "/bbox/" + test_name)
                        #print("Predicted Area: ", poly_1.area)
                        #print("True Area: ", poly_2.area)
                        accuracy = poly_1.intersection(poly_2).area / poly_1.union(poly_2).area
                        print("Accuracy: ", accuracy)
                        sum_accuracy += accuracy
                        n_pages += 1
                    else:
                        i+=1
                except:
                    break

    final_accuracy = sum_accuracy/n_pages
    print("Total accuracy: ",final_accuracy)



#jsonFigures2CSV()
#csv2txt()
#trainPuliti()
#trainSporchi()
#final_annotation()
#split_final_annotation()
#prepareTestJPG()
frcnnTestAccuracy("results_imgs_trainB_0")
