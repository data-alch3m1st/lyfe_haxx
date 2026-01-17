### PDF OCR (for scanned PDFs) ###

import pdfplumber
import easyocr
from PIL import Image
import io
import os
import sys

# Initialize EasyOCR reader (English only for now; you can add more)
reader = easyocr.Reader(['en'], verbose=False)

# Path to your PDF file
pdf_path = './input/sample_scanned.pdf'

# List to store extracted text per page
all_text = []

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages):
        # First try extracting using pdfplumber (text layer)
        text = page.extract_text()
        
        if text and text.strip():
            print(f"Text layer found on page {page_num+1}, using pdfplumber.")
        else:
            print(f"No text layer on page {page_num+1}, using OCR fallback.")
            
            # Convert pdfplumber page to image (RGB PIL image)
            pil_image = page.to_image(resolution=300).original.convert("RGB")

            # Convert to bytes for easyocr
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Run OCR with EasyOCR
            result = reader.readtext(img_byte_arr, detail=0, paragraph=True)
            text = "\n".join(result)
        
        all_text.append(f"\n\n--- PAGE {page_num+1} ---\n\n{text}")

# Join all text into a single string
final_text = "\n".join(all_text)

# Extract base name (without extension) and add suffix
base_name = os.path.splitext(os.path.basename(pdf_path))[0]
output_filename = f"{base_name}_OCRd_2Text.txt"

# Save to file
with open(output_filename, "w", encoding="utf-8") as f:
    f.write(final_text)

# Preview first few characters
print(final_text[:1000])