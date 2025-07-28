import fitz
import re
import json
import os
import time
import numpy as np
from sklearn.cluster import DBSCAN
from collections import defaultdict, Counter
from scipy.spatial import distance
import statistics

class RobustOutlineExtractor:
    """
    Advanced PDF outline extraction using hybrid ML approach
    Combines PDF metadata, structural analysis, and visual features
    Based on principles from:
    - "Layout-Aware PDF Content Extraction" (ACM DocEng 2021)
    - "PDF Text Extraction with Deep Learning" (IEEE Access 2022)
    """
    
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        try:
            self.doc = fitz.open(pdf_path)
            self.toc = self.doc.get_toc()
            self.metadata = self.doc.metadata
            self.font_profiles = self._analyze_fonts()
        except Exception as e:
            raise RuntimeError(f"Failed to open PDF: {str(e)}")

    def _clean_text(self, text):
        """Normalize text with advanced cleaning"""
        if not text:
            return ""
        # Remove special characters and normalize whitespace
        text = re.sub(r'[^\w\s.,:;!?()-]', '', text)
        return re.sub(r'\s+', ' ', text).strip()

    def _analyze_fonts(self):
        """Create comprehensive font profile with clustering"""
        font_data = []
        for page in self.doc:
            blocks = page.get_text("dict", sort=True).get("blocks", [])
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            font_data.append({
                                "size": round(span["size"]),
                                "font": span["font"],
                                "flags": span["flags"],
                                "bbox": span["bbox"],
                                "text": span["text"]
                            })
        
        if not font_data:
            return {}
        
        # Cluster font sizes to identify heading sizes
        sizes = np.array([d["size"] for d in font_data]).reshape(-1, 1)
        clustering = DBSCAN(eps=0.5, min_samples=5).fit(sizes)
        size_clusters = defaultdict(list)
        for i, label in enumerate(clustering.labels_):
            if label >= 0:  # Ignore noise
                size_clusters[label].append(font_data[i]["size"])
        
        # Find body text (most common cluster)
        body_cluster = max(size_clusters, key=lambda k: len(size_clusters[k]))
        body_size = statistics.median(size_clusters[body_cluster])
        
        # Identify heading clusters (significantly larger than body)
        heading_clusters = {
            k: statistics.median(v) 
            for k, v in size_clusters.items()
            if statistics.median(v) > body_size * 1.2
        }
        
        # Sort heading sizes and map to levels
        sorted_sizes = sorted(heading_clusters.values(), reverse=True)
        size_map = {}
        if sorted_sizes:
            size_map["H1"] = sorted_sizes[0]
            size_map["H2"] = sorted_sizes[1] if len(sorted_sizes) > 1 else sorted_sizes[0]
            size_map["H3"] = sorted_sizes[2] if len(sorted_sizes) > 2 else sorted_sizes[-1]
        
        # Analyze font styles
        font_styles = Counter()
        for d in font_data:
            flags = d["flags"]
            style = ""
            if flags & 2**0: style += "bold|"
            if flags & 2**1: style += "italic|"
            if flags & 2**2: style += "serif|"
            if flags & 2**3: style += "mono|"
            font_styles[style] += 1
        
        return {
            "body_size": body_size,
            "size_map": size_map,
            "font_styles": font_styles,
            "raw_data": font_data
        }

    def _get_title(self):
        """Extract title using multi-source approach"""
        # 1. Try PDF metadata
        if self.metadata and self.metadata.get('title'):
            clean_title = self._clean_text(self.metadata['title'])
            if clean_title:
                return clean_title
        
        # 2. Extract from first page's largest text
        try:
            page = self.doc[0]
            blocks = page.get_text("dict", sort=True)["blocks"]
            candidate = None
            max_size = 0
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if span["size"] > max_size:
                                max_size = span["size"]
                                candidate = span["text"]
            if candidate:
                return self._clean_text(candidate)
        except:
            pass
        
        # 3. Fallback to filename
        return os.path.basename(self.pdf_path).replace('.pdf', '')

    def _extract_from_toc(self):
        """Extract structured outline from PDF's ToC"""
        outline = []
        for level, title, page in self.toc:
            if 1 <= level <= 3:
                outline.append({
                    "level": f"H{level}",
                    "text": self._clean_text(title),
                    "page": max(0, page - 1)  # Convert to 0-based
                })
        return outline

    def _is_heading_candidate(self, text, font_size, font_flags, position, page_width):
        """ML-inspired heading detection using multiple features"""
        size_ratio = font_size / self.font_profiles["body_size"] if self.font_profiles["body_size"] > 0 else 1
        is_bold = bool(font_flags & 2**0)
        
        heading_pattern = re.compile(
            r'^(chapter|section|appendix|part|article|^\d+(\.\d+)*|^[A-Z]\.?)\b', 
            re.IGNORECASE
        )
        has_numbering = bool(heading_pattern.match(text))
        
        is_centered = (position[0] > page_width * 0.3 and 
                       position[1] < page_width * 0.7)
        
        is_title_case = text.istitle() or text.isupper()
        
        score = 0
        score += min(3, size_ratio) * 1.5
        score += 1.0 if is_bold else 0
        score += 0.8 if has_numbering else 0
        score += 0.6 if is_centered else 0
        score += 0.5 if is_title_case else 0
        score += 0.4 if len(text) < 80 else -0.2
        
        return score > 3.0

    def _extract_headings_heuristic(self):
        """Advanced heading extraction using visual and positional features"""
        if not self.font_profiles:
            return []
        
        outline = []
        size_map = self.font_profiles.get("size_map", {})
        
        for p_num, page in enumerate(self.doc):
            page_width = page.rect.width
            blocks = page.get_text("dict", sort=True).get("blocks", [])
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        max_size = 0
                        font_flags = 0
                        bbox = line["bbox"]
                        
                        for span in line["spans"]:
                            line_text += span["text"]
                            if span["size"] > max_size:
                                max_size = span["size"]
                                font_flags = span["flags"]
                        
                        clean_text = self._clean_text(line_text)
                        if not clean_text or len(clean_text) < 3:
                            continue
                        
                        center_x = (bbox[0] + bbox[2]) / 2
                        
                        if self._is_heading_candidate(
                            clean_text, 
                            max_size, 
                            font_flags, 
                            (center_x, page_width),
                            page_width
                        ):
                            level = "H3"
                            for lvl, size in size_map.items():
                                if abs(max_size - size) < 0.5:
                                    level = lvl
                                    break
                            
                            outline.append({
                                "level": level,
                                "text": clean_text,
                                "page": p_num
                            })
        
        seen = set()
        return [item for item in outline 
                if not (item["text"] in seen or seen.add(item["text"]))]

    def get_structured_outline(self):
        """Generate final structured outline"""
        title = self._get_title()
        if self.toc:
            outline = self._extract_from_toc()
        else:
            outline = self._extract_headings_heuristic()
        
        return {
            "title": title,
            "outline": outline
        }


def process_pdf(input_pdf, output_json):
    """Process PDF and save outline to JSON with error handling"""
    try:
        extractor = RobustOutlineExtractor(input_pdf)
        result = extractor.get_structured_outline()
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error processing {input_pdf}: {str(e)}")
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump({
                "title": "Extraction Failed",
                "outline": [],
                "error": str(e)
            }, f, indent=2)
        return False


if __name__ == "__main__":
    INPUT_DIR = os.getenv("INPUT_DIR", "/app/input")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/output")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.chmod(OUTPUT_DIR, 0o777)
    
    processed_count = 0
    start_time = time.time()
    
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith('.pdf'):
            input_path = os.path.join(INPUT_DIR, filename)
            output_path = os.path.join(
                OUTPUT_DIR, 
                f"{os.path.splitext(filename)[0]}.json"
            )
            
            print(f"Processing '{filename}'...")
            file_start = time.time()
            
            success = process_pdf(input_path, output_path)
            elapsed = time.time() - file_start
            
            if success:
                print(f"✓ Created '{os.path.basename(output_path)}' in {elapsed:.2f}s")
                processed_count += 1
            else:
                print(f"✗ Failed to process '{filename}'")
    
    total_time = time.time() - start_time
    print(f"\nProcessed {processed_count} files in {total_time:.2f} seconds")
