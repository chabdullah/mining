import os

import downloadPDFs
import utility

# Download dei pdf a partire dai nomi dei file JPG
#downloadPDFs.downloadPDFs()
# TODO dividere i pdf per pagina
utility.extract_pages_pdf()
# TODO creare xml dai pdf separati e non interi
# Conversione dei pdf in xml "grezzi"
utility.pdf2xml()
# Ottimizzazione dei file xml in modo da togliere l'informazione superflua (Es. bbox di ogni singolo carattere)
utility.optimizeXML()
