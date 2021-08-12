from numpy.lib.function_base import extract
import pytesseract
import cv2 
import re 
import pandas as pd
import sys

if len(sys.argv) < 2:
     sys.exit('Not enough arguments. Enter an image to verify.')

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

NOT_FOUND = 'Not found'
path = 'images/' + sys.argv[1]

img = cv2.imread(path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

raw_text = pytesseract.image_to_string(img)



drug_list = ['amoxicillin', 'HCTZ', 'Ferrous Sulfate', 'Lisinopril', 'Ampicilin', 'Amoxicillin', 'Potassiam permanganate', 'Norco', 'TMP/SMX DS', 'Ampicillin']

def get_contact_info(text_):
    reg = re.compile('(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
    contact_info = reg.findall(text_)
    if len(contact_info) == 0:
        contact_info = ['N/A', 'N/A']
    elif len(contact_info) == 1:
        contact_info.append('N/A')
    return contact_info

def get_doctor(text_):
    #print(text_)
    s = text_.split('\n')
    for l in s:
        if 'MD' in l:
            return l
        if l.find('Dr.') != -1:
            return l
    return NOT_FOUND

def get_drug(text_):
    s = text_.split('\n')
    for l in s:
        for d in drug_list:
            if d in l:
                return d
    return NOT_FOUND

def get_date(text_):
    reg = re.compile('^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]|(?:Jan|Mar|May|Jul|Aug|Oct|Dec)))\1|(?:(?:29|30)(\/|-|\.)(?:0?[1,3-9]|1[0-2]|(?:Jan|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)(?:0?2|(?:Feb))\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9]|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|July))|(?:1[0-2]|(?:Oct|Nov|Dec)))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$')
    date = reg.findall(text_)
    if len(date) < 1:
        for l in text_.split('\n'):
            lower = l.lower()
            if 'date' in lower:
                if len(l.split('Date')) > 1:
                    return l.split('Date')[1]
        return NOT_FOUND
    return date

def get_ndc(dn):
    df = pd.read_csv('drug-names/national-drug-code-dir.csv')
    if dn == 'TMP/SMX DS':
        drugn_ = 'Sulfamethoxazole TMP DS'
    else:
        drugn_ = dn.strip()
    record = df[df["NONPROPRIETARYNAME"] == drugn_]
    if len(record) < 1:
        record = df[df["PROPRIETARYNAME"] == drugn_]
    if len(record) < 1:
        return NOT_FOUND
    return record["PRODUCTNDC"].values[0]

def verify(e_data):
    if e_data[1] == NOT_FOUND:
        return False
    if e_data[2] == NOT_FOUND:
        return False
    if e_data[3] == NOT_FOUND:
        return False
    if e_data[4] == NOT_FOUND:
        return False
    return True

info = get_contact_info(raw_text)
doc = get_doctor(raw_text)
drug = get_drug(raw_text)
date = get_date(raw_text)
ndc = get_ndc(drug)

extracted_data = [info, doc, drug, date, ndc]

print('Provider: ' + doc)
print('Phone: %s \nFax: %s' % (info[0],info[1]))
print('Drug: ' + drug)
print('Date: ' + date)
print('NDC: ' + ndc)

print('Verified: ' + str(verify(extracted_data)))

# detecting words & drawing boxes 
hImg, wImg,_ = img.shape
boxes = pytesseract.image_to_data(img)
for x,b in enumerate(boxes.splitlines()):
    if x!=0:
        b = b.split()
        if len(b)==12:
            x,y,w,h = int(b[6]),int(b[7]),int(b[8]),int(b[9])
            cv2.rectangle(img,(x,y),(w+x,h+y),(0,0,255),1)

cv2.imshow('Result', img)
cv2.waitKey(0)

