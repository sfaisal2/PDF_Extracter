from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline
import os

def minimal_docling_test():
    
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=VlmPipeline,
            ),
        }
    )
    
    for pdf_file in ["ali.pdf"]:#, "apl.pdf", "BCBSAl.pdf", "Guardian.pdf", "umr.pdf"]:
        if os.path.exists(pdf_file):
            print(f"\nProcessing {pdf_file}...")
            try:
                result = converter.convert(source=pdf_file)
                output_file = pdf_file.replace('.pdf', '_docling.md')
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.document.export_to_markdown())
                
                print(f"Saved to: {output_file}")
            except Exception as e:
                print(f"Error: {e}")

# Run it
if __name__ == "__main__":
    minimal_docling_test()