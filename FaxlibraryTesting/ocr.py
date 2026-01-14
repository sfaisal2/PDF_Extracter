import os
import sys

samples = [
    "umr.pdf"
]

def test_ocrmypdf(file: str):
    try:
        output_file = f"ocr_{file}"
        
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