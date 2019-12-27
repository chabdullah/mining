import re

#text = re.sub('<textline>', "", open("./conversion.xml").read())
f = open("./conversion.xml")
testo = (f.read())

attributes = re.search('<text (.*)>', testo)

split = testo.split("<text "+attributes.group(1)+">")
#splitEnd = split[1].split("</textline>")
print(split[0])
print(split[1])
#finalText = split[0]+splitEnd[0]+splitEnd[1]
#print(finalText)

