import time
import pymupdf as fitz
import pymupdf4llm
from pypdf import PdfReader
import pdfplumber
import csv
import os
from datetime import datetime

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
    try:
        if extractor == "pymupdf":
            doc = fitz.open(file)
            for page in doc:
                output += page.get_text()
            doc.close()
            
        elif extractor == "pymupdf4llm":
            output = pymupdf4llm.to_markdown(file)
            
        elif extractor == "pypdf":
            reader = PdfReader(file)
            for page in reader.pages:
                output += page.extract_text() or ""
            
        elif extractor == "pdfplumber":
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    output += page.extract_text() or ""
                
        else: 
            raise ValueError(f"Invalid extractor: {extractor}")
            
    except Exception as e:
        output = f"EXTRACTION_ERROR: {str(e)}"
        
    return output

def main():
    results = []
    
    print("🚀 Starting PDF Extraction Benchmark")
    print("=" * 50)
    
    for file in samples:
        if not os.path.exists(file):
            print(f"⚠️  File not found: {file}, skipping...")
            continue
            
        print(f"\n📄 Processing: {file}")
        
        for extractor in extractors:
            try:
                print(f"   Testing {extractor:15}...", end=" ", flush=True)
                
                start_time = time.time()
                extracted_text = extraction(file, extractor)
                end_time = time.time()
                
                time_taken = round(end_time - start_time, 3)
                
                # Store results - only the 3 required columns
                result = {
                    'file': file,
                    'extractor': extractor,
                    'time_taken': time_taken
                }
                results.append(result)
                
                print(f"✅ {time_taken}s")
                
            except Exception as e:
                print(f"❌ FAILED: {str(e)}")
                # Record error with time_taken as 0
                results.append({
                    'file': file,
                    'extractor': extractor,
                    'time_taken': 0
                })
    
    # Save to CSV
    if results:
        csv_filename = "extraction_results.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['file', 'extractor', 'time_taken']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        print(f"\n✅ Results saved to: {csv_filename}")
        
        # Print simple summary
        print("\n📊 SUMMARY")
        print("=" * 50)
        for extractor in extractors:
            extractor_times = [r['time_taken'] for r in results if r['extractor'] == extractor and r['time_taken'] > 0]
            if extractor_times:
                avg_time = sum(extractor_times) / len(extractor_times)
                print(f"{extractor:15} - Average: {avg_time:.3f}s")
            else:
                print(f"{extractor:15} - No successful extractions")
    
    else:
        print("❌ No results to save!")

if __name__ == "__main__":
    main()