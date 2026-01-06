from docling.document_converter import DocumentConverter

source = "samp.pdf"
converter = DocumentConverter()
result = converter.convert(source)

# Export to markdown
markdown_content = result.document.export_to_markdown()

# Save to file
output_file = "output.md"
with open(output_file, "w") as f:
  f.write(markdown_content)

print(f"Successfully converted {source} to {output_file}")
