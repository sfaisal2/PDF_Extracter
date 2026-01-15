from docling.document_converter import DocumentConverter
import os

files = ["apl2.pdf", "guardian1.pdf", "umr1.pdf"]#, "BCBS.pdf", "Delta.pdf", "Guardian.pdf", "UMR.pdf"]
converter = DocumentConverter()
for source in files:
  result = converter.convert(source)

  # Export to markdown
  markdown_content = result.document.export_to_markdown()

  base_name = os.path.splitext(os.path.basename(source))[0]
  output_file = f"{base_name}_converted.md"

  with open(output_file, 'w', encoding='utf-8') as f:
      f.write(markdown_content)

  print(f"Successfully converted {source} to {output_file}")
