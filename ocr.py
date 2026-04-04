import pytesseract
import cv2
import re
from tkinter import Tk, filedialog

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

Tk().withdraw()
path = filedialog.askopenfilename(
    title="Select Aadhaar Image",
    filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
)

if not path:
    print("No file selected.")
else:
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
    gray = cv2.medianBlur(gray, 3)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    
    raw_text = pytesseract.image_to_string(thresh, lang='eng')


    lines = raw_text.split('\n')
    lines = [l.strip() for l in lines if l.strip()]  

    name = None
    dob = None
    aadhaar = None

    # Aadhaar number
    for line in lines:
        match = re.search(r'\b(\d{4}[\s\-]?\d{4}[\s\-]?\d{4})\b', line)
        if match:
            aadhaar = match.group(1).replace(' ', '').replace('-', '')
            aadhaar = f"{aadhaar[:4]} {aadhaar[4:8]} {aadhaar[8:]}"  
            break

    # DOB: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY 
    for line in lines:
        match = re.search(r'\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b', line)
        if match:
            dob = match.group(1)
            break



    for i, line in enumerate(lines):
        # Case 1: line contains "Name:" or just "Name" followed by value
        if re.search(r'\bName\b', line, re.IGNORECASE):
            # value might be on same line after colon, or on next line
            parts = re.split(r'[:\-]', line, maxsplit=1)
            if len(parts) > 1 and parts[1].strip():
                name = parts[1].strip()
            elif i + 1 < len(lines):
                name = lines[i + 1].strip()
            break

    # Fallback: look for a line that looks like a proper name
    # (2-4 words, each starting with capital, no digits)
    if not name:
        for line in lines:
            if re.fullmatch(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3}', line):
                name = line
                break

    # --- Output ---
    print("\n========== Extracted Info ==========")
    print(f"Name     : {name    or 'Not found'}")
    print(f"DOB      : {dob     or 'Not found'}")
    print(f"Aadhaar  : {aadhaar or 'Not found'}")
    print("====================================")