# Adobe Hackathon: "Connecting the Dots" – Challenge 1A (Advanced PDF Outline Extractor)

This repository contains a robust and intelligent solution to **Challenge 1A – Understand Your Document**, designed for Adobe's "Connecting the Dots" Hackathon 2025. It extracts a structured outline (Title, H1, H2, H3) from PDF documents using a hybrid approach that combines heuristics, visual features, and clustering.

---

## 🔍 Problem Overview

Extract structured content from PDFs, focusing on:
- **Title**
- **Headings (H1, H2, H3)**
- **Page mapping**

The extractor should handle both well-structured documents (with ToC) and unstructured ones (without metadata or heading conventions).

---

## 💡 Solution Highlights

Our solution employs a **multi-phase hybrid extraction strategy**, inspired by academic principles from:
- "Layout-Aware PDF Content Extraction" (ACM DocEng 2021)
- "PDF Text Extraction with Deep Learning" (IEEE Access 2022)

### 📘 Strategy

1. **Phase 1: Table of Contents (ToC) Based Extraction**
   - If the PDF contains a built-in ToC, use it to extract headings directly (accurate and fast).

2. **Phase 2: Heuristic + Visual + Statistical Fallback**
   - Analyze font distributions using **DBSCAN clustering**
   - Detect heading candidates using:
     - Font size relative to body text
     - Bold/italic flags
     - Position on page (e.g., centered headings)
     - Title-case or uppercase detection
     - Common heading patterns (e.g., `1.1`, `A.`, `Section`, etc.)

3. **Title Extraction**
   - Metadata → First-page largest font → Fallback to file name

4. **Noise Resilience**
   - Uses bounding box and spatial context for robust classification
   - Deduplicates overlapping heading detections

---

## 🛠️ Technologies Used

| Component      | Tool/Library          |
|----------------|-----------------------|
| PDF Processing | `PyMuPDF (fitz)`      |
| ML Logic       | `DBSCAN (scikit-learn)` |
| Math & Stats   | `numpy`, `scipy`, `statistics` |
| Runtime Env    | Docker (containerized) |

---

## 🐳 Docker Setup

### 🔧 Build Image

```bash
docker build --platform linux/amd64 -t pdf-solution:latest .
