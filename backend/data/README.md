# Data Directory

This directory contains data files and resources for the backend application.

## Structure

```
data/
├── pdfs/           # PDF documents for economic terms and reference materials
│   └── README.md
└── README.md       # This file
```

## PDF Files (`pdfs/`)

Store economic terminology documents, glossaries, and reference PDFs here.

### Usage

PDF files in this directory can be accessed by backend services for:
- Text extraction and processing
- AI-powered document recommendations
- Economic term lookup and definitions
- Educational resource generation

### Naming Convention

Use descriptive, snake_case filenames:
- `economic_glossary_korean.pdf`
- `finance_terminology.pdf`
- `market_indicators_guide.pdf`

## Adding New Files

1. Place PDF files in the `pdfs/` subdirectory
2. Update this README with file descriptions
3. Ensure files are properly gitignored if they contain sensitive data
