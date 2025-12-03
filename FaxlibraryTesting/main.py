import os
import sys

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


def main():
    print("Testing OCRmyPDF")
    
    for file in samples:
        if not os.path.exists(file):
            print(f"File not found: {file}, skipping...")
            continue
            
        print(f"Processing: {file}")
        
        # Test OCRmyPDF
        print("  OCRmyPDF...", end=" ")
        ocr_result = test_ocrmypdf(file)
        print(ocr_result)
        
        print()

if __name__ == "__main__":
    main()