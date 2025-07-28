import os
import json
import time
from src.processor import OutlineExtractor

# Use absolute paths from environment variables (Docker will set these up)
INPUT_DIR = os.getenv("INPUT_DIR", "input")
import os
import json
import time
import sys
from src.processor import OutlineExtractor

# Use absolute paths from environment variables (Docker will set these up)
INPUT_DIR = os.getenv("INPUT_DIR", "input")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

def process_all_pdfs():
    """
    Main processing loop with improved error handling and permission management.
    """
    # Ensure output directory exists with proper permissions
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.chmod(OUTPUT_DIR, 0o777)  # Ensure writable by all

    try:
        pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    except PermissionError:
        print(f"Permission denied reading input directory: {INPUT_DIR}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Input directory not found: {INPUT_DIR}")
        sys.exit(1)

    for pdf_file in pdf_files:
        start_time = time.time()
        
        input_path = os.path.join(INPUT_DIR, pdf_file)
        output_filename = os.path.splitext(pdf_file)[0] + '.json'
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        print(f"Processing '{input_path}'...")

        try:
            extractor = OutlineExtractor(input_path)
            result = extractor.get_structured_outline()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            
            # Set permissions on the output file
            os.chmod(output_path, 0o666)
            
            processing_time = time.time() - start_time
            print(f"-> Successfully created '{output_path}' in {processing_time:.2f} seconds.")

        except Exception as e:
            print(f"-> Error processing {pdf_file}: {e}", file=sys.stderr)

if __name__ == "__main__":
    process_all_pdfs()
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

def process_all_pdfs():
    """
    Main processing loop.
    Iterates through PDF files in the input directory, extracts their outlines,
    and saves the results as JSON files in the output directory. [cite: 292]
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    try:
        pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    except PermissionError:
        print(f"Permission denied reading input directory: {INPUT_DIR}")
        return

    for pdf_file in pdf_files:
        start_time = time.time()
        
        input_path = os.path.join(INPUT_DIR, pdf_file)
        output_filename = os.path.splitext(pdf_file)[0] + '.json'
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        print(f"Processing '{input_path}'...")

        try:
            extractor = OutlineExtractor(input_path)
            result = extractor.get_structured_outline()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            
            processing_time = time.time() - start_time
            print(f"-> Successfully created '{output_path}' in {processing_time:.2f} seconds.")

        except Exception as e:
            print(f"-> Error processing {pdf_file}: {e}")

if __name__ == "__main__":
    process_all_pdfs()
