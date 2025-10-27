import time
import pymupdf as fitz
import pymupdf4llm
from pypdf import PdfReader
import pdfplumber

extractors = [
    "pymupdf",
    "pymupdf4llm",
    "pypdf",
    "pdfplumber"
]

samples = [
    "sample.pdf",
    "sample2.pdf",
    "sample3.pdf"
]

def extraction(file: str, extractor: str):
    output = ""
    if extractor == "pymupdf":
        doc = fitz.open(file)
        text = ""
        for page in doc:
            text += page.get_text()
        output += text
        output += "\n\n"
    elif extractor == "pymupdf4llm":
        output = pymupdf4llm.to_markdown(file)
    elif extractor == "pypdf":
        reader = PdfReader(file)
        pages = reader.pages
        for page in pages:
            text = page.extract_text()
            output += text
            output += "\n\n"
    elif extractor == "pdfplumber":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                output += page.extract_text()
                output += "\n\n"
    else: 
        raise ValueError(f"Invalid extractor: {extractor}")
    return output

def main():
    for file in samples:
        for extractor in extractors:
            start_time = time.time()
            print (f"\nExtracting {file}")
