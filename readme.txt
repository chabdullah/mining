- downloadPDFs.py
Scarica i pdf degli articoli del dataset PublayNet e li converte in file .xml
Tutti i dati vengono memorizzati nelle rispettive cartelle all''interno di /resources

- train.py
Addestra la prima rete CNN utilizzata sul dataset docFigure (/resources/docFigure) a riconoscere 
i line plot e a discriminarli dalle altre tipologie di plot

- train_frcnn.py
Per avviare l'addestramento della seconda rete (Faster RCNN), si utilizza l'istruzione:
python train_frcnn.py -o simple -p /keras_frcnn/data/annotate.txt

- test_frcnn.py
Per calcolare i bbox su test set (i valori vengono salvati nel file bboxTrovati.txt)
python test_frcnn.py -p keras_frcnn/data/augmentation_sporco/annotate_augmentated_test.txt

- frcnn_data.py
Per calcolare e visualizzare l'accuratezza:

Gli altri file sono di utility


Dataset utilizzati:
resources/docFigure per la prima rete (CNN)
resources/jpg/publaynet per la seconda rete (Faster RCNN). Le immagini si trovano tutte nella cartella "train" ma in realtà vengono divise successivamente nel dataset di training, valdation e test
 
