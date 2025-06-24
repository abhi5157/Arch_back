# import os
# import re
# import PyPDF2
# import nltk
# from nltk.tokenize import sent_tokenize

# nltk.download('punkt')

# RAW_DIR = "data/raw"
# OUTPUT_DIR = "data/processed/clean_text"
# CHUNK_SIZE = 500  # characters

# os.makedirs(OUTPUT_DIR, exist_ok=True)

# def clean_text(text):
#     text = re.sub(r'\s+', ' ', text)
#     return text.strip()

# def chunk_text(text, chunk_size=CHUNK_SIZE):
#     sentences = sent_tokenize(text)
#     chunks, current_chunk = [], ""

#     for sentence in sentences:
#         if len(current_chunk) + len(sentence) <= chunk_size:
#             current_chunk += sentence + " "
#         else:
#             chunks.append(current_chunk.strip())
#             current_chunk = sentence + " "
#     if current_chunk:
#         chunks.append(current_chunk.strip())

#     return chunks

# def extract_text_from_pdf(pdf_path):
#     text = ""
#     try:
#         with open(pdf_path, "rb") as f:
#             reader = PyPDF2.PdfReader(f)
#             for page in reader.pages:
#                 text += page.extract_text() or ""
#     except Exception as e:
#         print(f"❌ Error reading {pdf_path}: {e}")
#     return text

# def process_file(file_path, filename_base):
#     if file_path.endswith(".pdf"):
#         raw_text = extract_text_from_pdf(file_path)
#     elif file_path.endswith(".txt"):
#         with open(file_path, "r", encoding="utf-8") as f:
#             raw_text = f.read()
#     else:
#         return  # unsupported file

#     if not raw_text.strip():
#         print(f"⚠️ Skipped empty file: {file_path}")
#         return

#     clean = clean_text(raw_text)
#     chunks = chunk_text(clean)

#     for idx, chunk in enumerate(chunks):
#         out_path = os.path.join(OUTPUT_DIR, f"{filename_base}_chunk{idx}.txt")
#         with open(out_path, "w", encoding="utf-8") as f:
#             f.write(chunk)
#         print(f"✅ Chunk saved: {out_path}")

# if __name__ == "__main__":
#     for subdir, _, files in os.walk(RAW_DIR):
#         for file in files:
#             if file.endswith(".pdf") or file.endswith(".txt"):
#                 file_path = os.path.join(subdir, file)
#                 filename_base = os.path.splitext(file)[0]
#                 process_file(file_path, filename_base)


import os
import re
import PyPDF2
import nltk
import pandas as pd
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

RAW_DIR = "data/raw"
CSV_PATH = os.path.join(RAW_DIR, "Real Estate Data V21.csv")
OUTPUT_DIR = "data/processed/clean_text"
CHUNK_SIZE = 500  # characters

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ========== Helpers ==========
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, chunk_size=CHUNK_SIZE):
    sentences = sent_tokenize(text)
    chunks, current_chunk = [], ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"❌ Error reading {pdf_path}: {e}")
    return text

def process_text_chunks(text, filename_base):
    clean = clean_text(text)
    chunks = chunk_text(clean)
    for idx, chunk in enumerate(chunks):
        out_path = os.path.join(OUTPUT_DIR, f"{filename_base}_chunk{idx}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(chunk)
        print(f"✅ Chunk saved: {out_path}")

# ========== PDF / TXT ==========
def process_raw_files():
    for subdir, _, files in os.walk(RAW_DIR):
        for file in files:
            if file.endswith(".pdf") or file.endswith(".txt"):
                file_path = os.path.join(subdir, file)
                filename_base = os.path.splitext(file)[0]

                if file.endswith(".pdf"):
                    raw_text = extract_text_from_pdf(file_path)
                else:
                    with open(file_path, "r", encoding="utf-8") as f:
                        raw_text = f.read()

                if raw_text.strip():
                    process_text_chunks(raw_text, filename_base)
                else:
                    print(f"⚠️ Skipped empty file: {file_path}")




                    

# ========== Property CSV ==========
def process_property_csv():
    if not os.path.exists(CSV_PATH):
        print("❌ No CSV property file found.")
        return

    df = pd.read_csv(CSV_PATH)
    for idx, row in df.iterrows():
        desc = (
            f"City: {row.get('city', '')}\n"
            f"Type: {row.get('property_type', '')}\n"
            f"Config: {row.get('bedrooms', '')} BHK\n"
            f"Price: ₹{row.get('price', '')}\n"
            f"Area: {row.get('area', '')} sqft\n"
            f"Location: {row.get('locality', '')}\n"
            f"Posted Date: {row.get('posted_date', '')}\n"
            f"Description: {row.get('description', '')}\n"
        )
        filename_base = f"property_{idx}"
        process_text_chunks(desc, filename_base)

# ========== Main ==========
if __name__ == "__main__":
    print("📄 Processing PDFs and TXTs...")
    process_raw_files()
    
    print("\n🏘️ Processing Property CSV...")
    process_property_csv()

    print("\n✅ All chunks prepared in:", OUTPUT_DIR)
