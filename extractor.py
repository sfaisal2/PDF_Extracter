import time
import pymupdf as fitz
import pymupdf4llm
from pypdf import PdfReader
import pdfplumber
import csv
import os

extractors = [
    "pymupdf",
    "pymupdf4llm",
    "pypdf",
    "pdfplumber"
]

samples = [
    "sample.pdf",
    "sample2.pdf"
]

def save_extracted_data(file: str, extractor: str, text: str):
    """Save extracted text to a separate file for each combination"""
    # Create a clean filename: extracted_{file}_{extractor}.txt
    base_name = os.path.splitext(file)[0]  # Remove .pdf extension
    output_filename = f"extracted_{base_name}_{extractor}.txt"
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        if text.startswith("EXTRACTION_ERROR"):
            f.write(f"EXTRACTION ERROR: {text}\n")
        elif not text.strip():
            f.write("NO TEXT EXTRACTED\n")
        else:
            f.write(text)
    
    return output_filename

def get_baseline_char_count(file: str):
    """Get baseline char count using pymupdf (most reliable)"""
    try:
        doc = fitz.open(file)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return len(text)
    except:
        return 0

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
    
    # First, get baseline char counts for each file
    baseline_chars = {}
    for file in samples:
        if os.path.exists(file):
            baseline_chars[file] = get_baseline_char_count(file)
            print(f"📊 {file}: Baseline = {baseline_chars[file]} chars")
    
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
                
                # Calculate if all chars were extracted
                extracted_char_count = len(extracted_text) if not extracted_text.startswith("EXTRACTION_ERROR") else 0
                baseline = baseline_chars.get(file, 0)
                
                if baseline > 0 and extracted_char_count > 0:
                    # Consider it "all chars extracted" if within 95% of baseline
                    all_chars_extracted = (extracted_char_count >= baseline * 0.95)
                    chars_status = "ALL_EXTRACTED" if all_chars_extracted else "PARTIAL_EXTRACTION"
                else:
                    chars_status = "UNKNOWN"  # Can't determine without baseline
                
                # Save extracted text to separate file
                output_filename = save_extracted_data(file, extractor, extracted_text)
                
                # Store results
                result = {
                    'file': file,
                    'extractor': extractor,
                    'time_taken': time_taken,
                    'chars_status': chars_status,
                    'extracted_chars': extracted_char_count,
                    'baseline_chars': baseline,
                    'output_file': output_filename
                }
                results.append(result)
                
                status_icon = "✅" if chars_status == "ALL_EXTRACTED" else "⚠️"
                print(f"{status_icon} {time_taken}s | {chars_status} | Saved to: {output_filename}")
                
            except Exception as e:
                print(f"❌ FAILED: {str(e)}")
                
                # Save error to file anyway
                base_name = os.path.splitext(file)[0]
                output_filename = f"extracted_{base_name}_{extractor}.txt"
                with open(output_filename, 'w', encoding='utf-8') as f:
                    f.write(f"EXTRACTION FAILED: {str(e)}")
                
                results.append({
                    'file': file,
                    'extractor': extractor,
                    'time_taken': 0,
                    'chars_status': 'EXTRACTION_FAILED',
                    'extracted_chars': 0,
                    'baseline_chars': baseline_chars.get(file, 0),
                    'output_file': output_filename
                })
    
    # Save to CSV
    if results:
        csv_filename = "extraction_results.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['file', 'extractor', 'time_taken', 'chars_status', 'extracted_chars', 'baseline_chars', 'output_file']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        print(f"\n✅ Results saved to: {csv_filename}")
        
        # Print simple summary
        print("\n📊 SUMMARY")
        print("=" * 50)
        for extractor in extractors:
            extractor_results = [r for r in results if r['extractor'] == extractor]
            successful = [r for r in extractor_results if r['chars_status'] == 'ALL_EXTRACTED']
            times = [r['time_taken'] for r in successful if r['time_taken'] > 0]
            
            if times:
                avg_time = sum(times) / len(times)
                print(f"{extractor:15} - Avg: {avg_time:.3f}s | Complete: {len(successful)}/{len(extractor_results)}")
            else:
                print(f"{extractor:15} - No complete extractions")
    
    else:
        print("❌ No results to save!")

if __name__ == "__main__":
    main()