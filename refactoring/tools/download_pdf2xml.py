import os

import downloadPDFs
import utility

# Download dei pdf a partire dai nomi dei file JPG
downloadPDFs.downloadPDFs()
# Divide i pdf per pagina secondo quelle che sono sul json
utility.extract_pages_pdf()
# Conversione dei pdf in xml "grezzi"
utility.pdf2xml()
# Ottimizzazione dei file xml in modo da togliere l'informazione superflua (Es. bbox di ogni singolo carattere)
utility.optimizeXML()
