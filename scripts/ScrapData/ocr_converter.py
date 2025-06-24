# # scripts/ocr_converter.py
# import pytesseract
# from pdf2image import convert_from_path

# def extract_text_from_pdf(pdf_path):
#     images = convert_from_path(pdf_path)
#     full_text = ""
#     for img in images:
#         text = pytesseract.image_to_string(img)
#         full_text += text + "\n"
#     return full_text

import os
import pytesseract
from pdf2image import convert_from_path

INPUT_DIR = "data/raw/zoning_pdfs"
OUTPUT_DIR = "data/processed/ocr_text"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def ocr_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image) + "\n"
    return text

if __name__ == "__main__":
    for pdf_file in os.listdir(INPUT_DIR):
        if pdf_file.endswith(".pdf"):
            full_path = os.path.join(INPUT_DIR, pdf_file)
            output_file = os.path.join(OUTPUT_DIR, pdf_file.replace(".pdf", ".txt"))
            text = ocr_pdf(full_path)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"OCR complete: {output_file}")
