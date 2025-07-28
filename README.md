# Adobe Hackathon: "Connecting the Dots" - Challenge 1A Solution

This repository contains the solution for **Round 1A: Understand Your Document**. The system is designed to extract a structured outline (Title, H1, H2, H3) from PDF documents efficiently and accurately, adhering to all specified constraints.

### 1. Approach and Methodology

Our solution employs a **hybrid extraction strategy** to maximize accuracy and performance. [cite_start]This approach avoids relying solely on font sizes, which can be unreliable across different PDF structures[cite: 317].

The logic follows two primary paths:

1.  **Table of Contents (ToC) First**: The extractor first inspects the PDF for an embedded ToC. If a valid ToC exists, it is used to generate a precise outline. This is the fastest and most reliable method.

2.  **Heuristic Fallback Engine**: If no ToC is found, the system falls back to a smart heuristic engine. This engine:
    * **Profiles Typography**: It performs a quick scan of the document to identify the distribution of font sizes, allowing it to distinguish between common body text and rarer, larger heading fonts.
    * **Analyzes Heading Candidates**: A line of text is classified as a heading based on a combination of factors, including its font size profile, bold styling, and whether it follows common numbering patterns (e.g., "1. Introduction", "2.1 Background").

[cite_start]This design ensures robustness and high performance, and the code is modular for easy reuse in Round 1B[cite: 320].

### 2. Libraries Used

* **`PyMuPDF` (`fitz`)**: This library was chosen for its exceptional speed and comprehensive feature set. It provides efficient access to text blocks, font information, and document metadata, which is essential for our hybrid extraction strategy.

### 3. Build and Run Instructions

The solution is containerized with Docker for consistent and isolated execution.

#### Build the Docker Image

[cite_start]Navigate to the project's root directory and use the official build command[cite: 286].

```bash
docker build --platform linux/amd64 -t pdf-solution:latest .# adobe-challenege1
