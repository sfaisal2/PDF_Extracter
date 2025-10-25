import pymupdf as fitz
import pymupdf4llm
from pypdf import PdfReader
import pdfplumber

doc = fitz.open('sample.pdf')
text = ""
for page in doc:
    text += page.get_text()
print(text)

extractors = [
    "pymupdf",
    "pymupdf4llm"
    "pypdf",
    "pdfplumber"
]

samples = [
    "sample.pdf",
    "sample2.pdf",
    "sample3.pdf"
]

def extraction():
    

def main():
