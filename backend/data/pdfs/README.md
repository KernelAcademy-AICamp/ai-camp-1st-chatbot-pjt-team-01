# PDF Documents

This directory contains PDF files for economic terms, glossaries, and educational materials.

## Files

Add your PDF files here with descriptions:

### Example:
- `economic_glossary.pdf` - Korean economic terminology glossary
- `finance_terms.pdf` - Financial market terminology reference

## Usage in Code

```python
import os
from pathlib import Path

# Get PDF directory path
PDF_DIR = Path(__file__).parent

# Access a specific PDF
pdf_path = PDF_DIR / "economic_glossary.pdf"
```

## Notes

- Keep file sizes reasonable (<10MB per file recommended)
- Use descriptive filenames
- Update this README when adding new files
