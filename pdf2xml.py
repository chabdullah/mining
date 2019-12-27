import re

#text = re.sub('<textline>', "", open("./conversion.xml").read())
f = open("./conversion.xml")
testo = (f.read())

attributes = re.search('<textline (.*)>', testo)

blocchiLine = testo.split("</textline>")
attributes = re.search('<textline (.*)>', blocchiLine[0])
splitLine2 = blocchiLine[0].split("<textline " + attributes.group(1) + ">")
txtFinale = ""
for i,splitLine in enumerate(blocchiLine):
    attributes = re.search('<textline(.*)>', splitLine)
    if attributes is not None:
        splitLine2 = splitLine.split("<textline"+attributes.group(1)+">")
        blocchiCarattere = splitLine2[1].split("</text>")
        parola = ""
        for carattere in blocchiCarattere:
            attributes = re.search('<text(.*)>', carattere)
            if attributes is not None:
                splitCarattere = carattere.split("<text"+attributes.group(1)+">")
                parola += splitCarattere[1]
        txtFinale += (splitLine2[0]+parola)

f = open("./conversion_optimazed.xml","w")
f.write(txtFinale)
f.close()

