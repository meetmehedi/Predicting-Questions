# Raw Data Ingestion Directory

This folder is designated for storing raw examination papers prior to parsing and digitization:

## Recommended Folder Hierarchy:
```
data/raw/
├── pdfs/
│   ├── HSC/
│   │   ├── 2023/
│   │   │   ├── HSC_2023_Dhaka_Physics_1st.pdf
│   │   │   └── ...
│   └── SSC/
│       ├── 2023/
│       └── ...
├── ocr_outputs/
│   ├── hsc_2023_dhaka_phy1_raw.json
│   └── ...
└── figures/
    ├── hsc_2023_dha_phy1_q2.png
    └── ...
```

## Standard Naming Convention:
`{EXAM}_{YEAR}_{BOARD}_{SUBJECT}_{PAPER}_{SET}.pdf`
Example: `HSC_2023_Dhaka_Physics_1st_Ka.pdf`

## Supported OCR Tools:
- **Tesseract OCR (Bengali traineddata):** `tesseract scan.png output -l ben`
- **Docling / Marker / PyMuPDF:** For extracting layout, embedded images, and markdown tables.
