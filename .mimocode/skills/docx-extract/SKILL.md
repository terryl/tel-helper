---
name: docx-extract
description: Extract text and structure from DOCX files using Node.js XML parsing. Handles Chinese documents, requirement specs, and API docs.
---

# DOCX Text Extraction

Extract readable text from `.docx` files by parsing the underlying OOXML (`word/document.xml`). Works on Windows without requiring Python or Office installations.

## When to Use

- User references a `.docx` file with `@path` syntax or asks to read one
- Need to extract text from requirement specs (需求规格说明书), API docs, or project templates
- PDF extraction skill is unavailable or the file is actually a DOCX

## Prerequisites

- Node.js (available at `C:\nvm4w\nodejs\node.exe`)
- No additional npm packages required (uses built-in `fs` and regex)

## Procedure

### Step 1: Unzip the DOCX

DOCX files are ZIP archives. Extract to a temp directory:

```bash
# PowerShell
$tempDir = "$env:TEMP\docx_extract_$(Get-Date -Format 'yyyyMMddHHmmss')"
New-Item -ItemType Directory -Path $tempDir -Force
Copy-Item "<path-to-docx>" "$tempDir\docx.zip"
Expand-Archive -Path "$tempDir\docx.zip" -DestinationPath "$tempDir\unpacked" -Force
```

### Step 2: Extract Text via Node.js

Read `word/document.xml` and extract all `<w:t>` text nodes:

```javascript
const fs = require('fs');
const xml = fs.readFileSync('<tempDir>/unpacked/word/document.xml', 'utf-8');

// Extract all text between <w:t> tags
const matches = xml.match(/<w:t[^>]*>([^<]+)<\/w:t>/g);
if (matches) {
    const text = matches.map(m => m.replace(/<\/?w:t[^>]*>/g, '')).join('');
    console.log(text);
} else {
    console.log('No text found in document');
}
```

### Step 3: Structure the Output

For requirement docs, parse the extracted text into structured sections:

```javascript
// Split by paragraph boundaries (w:p elements)
const paragraphs = xml.split(/<\/w:p>/);
const structured = paragraphs.map(p => {
    const texts = p.match(/<w:t[^>]*>([^<]+)<\/w:t>/g);
    if (texts) {
        return texts.map(t => t.replace(/<\/?w:t[^>]*>/g, '')).join('');
    }
    return '';
}).filter(t => t.trim());
```

### Step 4: Clean Up

```powershell
Remove-Item -Recurse -Force $tempDir
```

## One-Shot Script

Save as `extract-docx.js` and run with `node extract-docx.js <path-to-docx>`:

```javascript
const fs = require('fs');
const { execSync } = require('child_process');
const path = require('path');
const os = require('os');

const docxPath = process.argv[2];
if (!docxPath) {
    console.error('Usage: node extract-docx.js <path-to-docx>');
    process.exit(1);
}

const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'docx-'));
const zipPath = path.join(tempDir, 'docx.zip');
const unpackDir = path.join(tempDir, 'unpacked');

fs.copyFileSync(docxPath, zipPath);
execSync(`powershell.exe -Command "Expand-Archive -Path '${zipPath}' -DestinationPath '${unpackDir}' -Force"`);

const xmlPath = path.join(unpackDir, 'word', 'document.xml');
if (!fs.existsSync(xmlPath)) {
    console.error('No word/document.xml found - is this a valid DOCX?');
    process.exit(1);
}

const xml = fs.readFileSync(xmlPath, 'utf-8');

// Extract paragraph-by-paragraph
const paragraphs = xml.split(/<\/w:p>/);
const lines = paragraphs.map(p => {
    const texts = p.match(/<w:t[^>]*>([^<]+)<\/w:t>/g);
    if (texts) {
        return texts.map(t => t.replace(/<\/?w:t[^>]*>/g, '')).join('');
    }
    return '';
}).filter(t => t.trim());

console.log(lines.join('\n'));

// Cleanup
fs.rmSync(tempDir, { recursive: true, force: true });
```

## Key Notes

- The regex `/<w:t[^>]*>([^<]+)<\/w:t>/g` matches all text content in OOXML
- For Chinese documents, ensure UTF-8 encoding when reading the XML
- Table content is also in `<w:t>` tags but may need special ordering (cells are in `<w:tc>` elements)
- Headings use `<w:pStyle w:val="Heading1"/>` etc. in the `<w:pPr>` element before the text
- If the document has images, they are in `word/media/` and not extractable as text
