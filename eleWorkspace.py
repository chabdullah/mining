import re
import json
from PyPDF2 import PdfFileReader, PdfFileWriter


def split():
    # split pages pdf
    path = "./resources/pdf/PMC3576793.pdf"
    name_of_split = "PMC3576793_split"
    pdf = PdfFileReader(path)
    page = 1

    pdf_writer = PdfFileWriter()
    pdf_writer.addPage(pdf.getPage(page))

    output = f'{name_of_split}{page}.pdf'
    with open(output, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)


def write_json():
    data = {}
    data['people'] = []
    data['people'].append({
        'name': 'Scott',
        'website': 'stackabuse.com',
        'from': 'Nebraska'
    })
    data['people'].append({
        'name': 'Larry',
        'website': 'google.com',
        'from': 'Michigan'
    })
    data['people'].append({
        'name': 'Tim',
        'website': 'apple.com',
        'from': 'Alabama'
    })

    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)


def read_json():
    with open('data.json') as json_file:
        data = json.load(json_file)
        for p in data['people']:
            print('Name: ' + p['name'])
            print('Website: ' + p['website'])
            print('From: ' + p['from'])
            print('')


def find_middle_string():
    s = "cniernvbiinizionceirbn4krb4rfineerib3nhjefi3inizioenriubrbueffinecnierbf"
    start = "inizio"
    end = "fine"
    result = re.search('inizio(.*)fine', s)
    print(result.group(1))


def iterate():
    arr = [3, 4, 5, 6]
    for i in range(2, 4):
        print(i)
        if i == 5:
            break


def change_vals():
    a = 2
    b = a
    a = a + 1
    print('b:')
    print(b)
    print('a:')
    print(a)


change_vals()


"""
text = re.sub('<[^<]+>', "", open("./").read())
with open("/path/to/file", "w") as f:
    f.write(text)
"""
