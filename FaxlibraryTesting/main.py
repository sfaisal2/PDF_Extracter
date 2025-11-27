import os
import docling_core

samples = [
    "ali.pdf",
    "apl.pdf", 
    "BCBSAl.pdf",
    "Guardian.pdf",
    "umr.pdf"
]

def test_ocrmypdf(file: str):
    """Test OCRmyPDF by running it on the file"""
    try:
        # Create output filename
        output_file = f"ocr_{file}"
        
        # Run OCRmyPDF using os.system
        command = f'ocrmypdf --force-ocr "{file}" "{output_file}"'
        return_code = os.system(command)
        
        if return_code == 0:
            return f"SUCCESS: {output_file}"
        else:
            return f"OCR_FAILED: return code {return_code}"
            
    except Exception as e:
        return f"OCR_ERROR: {str(e)}"

def test_docling(file: str):
    """Test Docling extraction"""
    try:
        # Initialize Docling converter
        converter = docling.pipeline.PdfToDocumentPipeline()
        
        # Process the PDF (first 3 pages)
        result = converter.convert(file, max_pages=3)
        
        # Extract text
        text = result.document.plain_text
        
        # Save to file
        output_file = f"docling_{os.path.splitext(file)[0]}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
            
        return f"SUCCESS: {output_file} ({len(text)} chars)"
        
    except Exception as e:
        return f"DOCLING_ERROR: {str(e)}"

def main():
    print("Testing OCRmyPDF and Docling\n")
    
    for file in samples:
        if not os.path.exists(file):
            print(f"File not found: {file}, skipping...")
            continue
            
        print(f"Processing: {file}")
        
        # Test OCRmyPDF
        print("  OCRmyPDF...", end=" ")
        ocr_result = test_ocrmypdf(file)
        print(ocr_result)
        
        # Test Docling  
        print("  Docling...", end=" ")
        docling_result = test_docling(file)
        print(docling_result)
        
        print()

if __name__ == "__main__":
    main()
