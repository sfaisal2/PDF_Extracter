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

def get_baseline_char_count(file: str):
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
            text = ""
            for page in doc:
                text += page.get_text()
            output = text
            doc.close()
            
        elif extractor == "pymupdf4llm":
            output = pymupdf4llm.to_markdown(file)
            
        elif extractor == "pypdf":
            reader = PdfReader(file)
            pages = reader.pages
            text = ""
            for page in pages:
                text += page.extract_text() or ""
            output = text
            
        elif extractor == "pdfplumber":
            with pdfplumber.open(file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                output = text
                
        else: 
            raise ValueError(f"Invalid extractor: {extractor}")
            
    except Exception as e:
        output = f"EXTRACTION_ERROR: {str(e)}"
        
    return output

def analyze_extraction_quality(text):
    if text.startswith("EXTRACTION_ERROR"):
        return 0, 0, 0, 0
    
    lines = text.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    
    # Calculate quality metrics
    total_lines = len(lines)
    meaningful_lines = len(non_empty_lines)
    avg_line_length = sum(len(line) for line in non_empty_lines) / meaningful_lines if meaningful_lines > 0 else 0
    total_chars = len(text)
    
    # Simple quality score (0-100)
    if total_chars == 0:
        quality_score = 0
    else:
        # Based on line structure, content density, etc.
        line_quality = (meaningful_lines / total_lines * 100) if total_lines > 0 else 0
        density_quality = min(100, avg_line_length / 2)  # Assuming good lines are 50+ chars
        quality_score = (line_quality + density_quality) / 2
    
    return quality_score, total_chars, meaningful_lines, avg_line_length

def save_to_csv(results, csv_filename="extraction_results.csv"):
    """Save results to CSV file"""
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'file', 'extractor', 'time_taken', 'quality_score', 
                     'total_chars', 'meaningful_lines', 'avg_line_length', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    print(f"\n✅ Results saved to: {csv_filename}")

def main():
    results = []
    
    print("🚀 Starting PDF Extraction Benchmark")
    print("=" * 60)
    
    for file in samples:
        # Check if file exists
        if not os.path.exists(file):
            print(f"⚠️  File not found: {file}, skipping...")
            continue
            
        print(f"\n📄 Processing: {file}")
        print("-" * 40)
        
        for extractor in extractors:
            try:
                print(f"   Testing {extractor:15}...", end=" ", flush=True)
                
                start_time = time.time()
                extracted_text = extraction(file, extractor)
                end_time = time.time()
                
                time_taken = end_time - start_time
                
                # Analyze extraction quality
                if extracted_text.startswith("EXTRACTION_ERROR"):
                    quality_score, total_chars, meaningful_lines, avg_line_length = 0, 0, 0, 0
                    status = "ERROR"
                else:
                    quality_score, total_chars, meaningful_lines, avg_line_length = analyze_extraction_quality(extracted_text)
                    status = "SUCCESS"
                
                # Store results
                result = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'file': file,
                    'extractor': extractor,
                    'time_taken': round(time_taken, 3),
                    'quality_score': round(quality_score, 2),
                    'total_chars': total_chars,
                    'meaningful_lines': meaningful_lines,
                    'avg_line_length': round(avg_line_length, 2),
                    'status': status
                }
                results.append(result)
                
                print(f"✅ {time_taken:.3f}s | Quality: {quality_score:.1f}% | Chars: {total_chars}")
                
                # Save sample of extracted text to individual files
                sample_filename = f"extracted_{os.path.splitext(file)[0]}_{extractor}.txt"
                with open(sample_filename, 'w', encoding='utf-8') as f:
                    f.write(extracted_text[:5000] + "\n\n...[truncated]..." if len(extracted_text) > 5000 else extracted_text)
                    
            except Exception as e:
                print(f"❌ FAILED: {str(e)}")
                # Record error in results
                results.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'file': file,
                    'extractor': extractor,
                    'time_taken': 0,
                    'quality_score': 0,
                    'total_chars': 0,
                    'meaningful_lines': 0,
                    'avg_line_length': 0,
                    'status': f"ERROR: {str(e)}"
                })
    
    # Save all results to CSV
    if results:
        save_to_csv(results)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        
        # Group by extractor for summary
        extractor_stats = {}
        for result in results:
            extractor = result['extractor']
            if extractor not in extractor_stats:
                extractor_stats[extractor] = {'count': 0, 'total_time': 0, 'total_quality': 0, 'successes': 0}
            
            extractor_stats[extractor]['count'] += 1
            extractor_stats[extractor]['total_time'] += result['time_taken']
            extractor_stats[extractor]['total_quality'] += result['quality_score']
            if result['status'] == 'SUCCESS':
                extractor_stats[extractor]['successes'] += 1
        
        print(f"\n{'Extractor':15} {'Success Rate':12} {'Avg Time':10} {'Avg Quality':12}")
        print("-" * 60)
        for extractor, stats in extractor_stats.items():
            success_rate = (stats['successes'] / stats['count']) * 100
            avg_time = stats['total_time'] / stats['count']
            avg_quality = stats['total_quality'] / stats['count']
            print(f"{extractor:15} {success_rate:10.1f}% {avg_time:8.3f}s {avg_quality:11.1f}%")
    
    else:
        print("❌ No results to save!")

if __name__ == "__main__":
    main()