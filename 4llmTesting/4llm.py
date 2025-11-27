import pymupdf4llm
import csv
import os

samples = [
    "BCBSAlwo.pdf"
]

def save_extracted_data(file: str, text: str):
    # Create a clean filename: extracted_{file}_pymupdf4llm.txt
    base_name = os.path.splitext(file)[0]  # Remove .pdf extension
    output_filename = f"extracted_{base_name}_pymupdf4llm.txt"
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        if text.startswith("EXTRACTION_ERROR"):
            f.write(f"EXTRACTION ERROR: {text}\n")
        elif not text.strip():
            f.write("NO TEXT EXTRACTED\n")
        else:
            f.write(text)
    
    return output_filename

def extraction(file: str):
    output = ""
    try:
        # pymupdf4llm with page limit to first 3 pages
        output = pymupdf4llm.to_markdown(file, pages=[0, 1, 2])
    except Exception as e:
        output = f"EXTRACTION_ERROR: {str(e)}"
        
    return output

def main():
    results = []
    
    for file in samples:
        if not os.path.exists(file):
            print(f"File not found: {file}, skipping...")
            continue
            
        print(f"Processing: {file}")
        
        try:
            print(f"  Extracting with pymupdf4llm...", end=" ", flush=True)
            
            extracted_text = extraction(file)
            
            # Calculate character count
            extracted_char_count = len(extracted_text) if not extracted_text.startswith("EXTRACTION_ERROR") else 0
            
            # Save extracted text to file
            output_filename = save_extracted_data(file, extracted_text)
            
            # Store results
            result = {
                'file': file,
                'extracted_chars': extracted_char_count,
                'output_file': output_filename
            }
            results.append(result)
            
            status = "SUCCESS" if not extracted_text.startswith("EXTRACTION_ERROR") else "FAILED"
            print(f"{status} | {extracted_char_count} chars | Saved to: {output_filename}")
            
        except Exception as e:
            print(f"FAILED: {str(e)}")
            
            # Save error to file anyway
            base_name = os.path.splitext(file)[0]
            output_filename = f"extracted_{base_name}_pymupdf4llm.txt"
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(f"EXTRACTION FAILED: {str(e)}")
            
            results.append({
                'file': file,
                'extracted_chars': 0,
                'output_file': output_filename
            })
    
    if results:
        csv_filename = "extraction_results.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['file', 'extracted_chars', 'output_file']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        print(f"\nResults saved to: {csv_filename}")

if __name__ == "__main__":
    main()