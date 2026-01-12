import re
from PIL import Image
import pytesseract

DOSAGE_PATTERN = re.compile(r'\b(\d+\s?(mg|ml|g|mcg|μg))\b', re.I)

def image_to_text(path):
    img = Image.open(path)
    text = pytesseract.image_to_string(img, lang='eng')
    return text

def parse_meds(text):
    meds=[]
    lines=[l.strip() for l in text.splitlines() if l.strip()]
    for ln in lines:
        if re.search(r'\b(mg|ml|tablet|tab|capsule|cap|inj|syrup)\b', ln, re.I):
            dose = DOSAGE_PATTERN.search(ln)
            meds.append({'raw': ln, 'dose': dose.group(0) if dose else ''})
    return meds
