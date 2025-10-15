# footnotes_assassin.py v3.0.0 #

import pdfplumber
import pandas as pd
from collections import Counter
import re
import statistics
import os

def parse_page_ranges(page_spec):
    """
    Parse a page specification string like "1-3,5,8-10" into a set of 0-based page indices.
    """
    pages = set()
    if not page_spec:
        return pages
    parts = page_spec.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            start, end = int(start), int(end)
            pages.update(range(start - 1, end))  # convert to 0-based
        else:
            pages.add(int(part) - 1)  # single page, 0-based
    return pages

def extract_text_without_footnotes(
    pdf_path
    , threshold_ratio=0.90
    , header_threshold=50
    , pages_to_skip=None
):
    """
    Extracts text from a PDF, removing:
    - Footnotes based on font height (robust mode/median strategy)
    - Headers within top X points of the page
    - Entirely skipping user-specified pages

    Returns:
        str: Document text without footnotes/headers/skipped pages
    """
    all_pages_text = []
    skip_set = parse_page_ranges(pages_to_skip)

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            if page_number in skip_set:
                continue

            words = page.extract_words()
            if not words:
                continue

            df = pd.DataFrame(words)

            # Remove headers if header_threshold is set
            if header_threshold is not None:
                df = df[df['top'] > header_threshold]

            if df.empty:
                continue

            # --- Robust determination of main text height ---
            heights = df['height'].tolist()
            heights_sorted = sorted(heights)

            # Drop the smallest 25% of heights to avoid bias toward footnotes
            cutoff_index = int(len(heights_sorted) * 0.25)
            filtered_heights = heights_sorted[cutoff_index:] if cutoff_index < len(heights_sorted) else heights_sorted

            main_height = None
            if filtered_heights:
                height_counts = Counter(filtered_heights)
                main_height = height_counts.most_common(1)[0][0]

            # Fallback to median if needed
            if main_height is None:
                main_height = statistics.median(heights)

            # --- Define threshold and filter ---
            height_threshold = main_height * threshold_ratio
            filtered_words = df[df['height'] >= height_threshold]

            # Sort and reconstruct text
            filtered_words = filtered_words.sort_values(by=['top', 'x0'])
            page_text = " ".join(filtered_words['text'].tolist())

            all_pages_text.append(page_text)

    return "\n\n".join(all_pages_text)


def pdf_to_txt(
    pdf_path
    , txt_output_path=None
    , output_dir=None
    , threshold_ratio=0.90
    , header_threshold=50
    , pages_to_skip=None
):
    """
    Extracts text and writes it to a .txt file.
    If txt_output_path is not provided, automatically uses:
        '{'pdf_basename'}'_CLEANED_TEXT.txt
    If output_dir is provided, the file is saved there (created if missing).
    Otherwise, it's saved in the same directory as the PDF.
    """
    # Determine output filename
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_filename = f"{base_name}_CLEANED_TEXT.txt"

    # Decide where to place it
    if txt_output_path:
        final_path = txt_output_path
    else:
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            final_path = os.path.join(output_dir, output_filename)
        else:
            dir_name = os.path.dirname(pdf_path)
            final_path = os.path.join(dir_name, output_filename)

    text = extract_text_without_footnotes(
        pdf_path=pdf_path
        , threshold_ratio=threshold_ratio
        , header_threshold=header_threshold
        , pages_to_skip=pages_to_skip
    )

    with open(final_path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"\n Cleaned text exported to: {final_path}")
    
    
# EXAMPLE USAGE:
# Main intended usage - ingest single pdf from input folder, export to output folder;
pdf_to_txt(
    pdf_path="./input/sample_article.pdf",
    output_dir="./output/",
    threshold_ratio=0.90,
    header_threshold=50,
    pages_to_skip="1, 3, 14"
)

# Example 1 — Auto filename in same directory as PDF
pdf_to_txt(
    pdf_path="./input/My_Research_Article.pdf"
    , threshold_ratio=0.88
    , header_threshold=50
    , pages_to_skip="1-2, 10-12"
)

# Example 2 — Send all outputs to a dedicated folder
pdf_to_txt(
    pdf_path="./input/Another_Paper.pdf"
    , output_dir="./output"
    , threshold_ratio=0.90
    , header_threshold=50
    , pages_to_skip="1"
)

# Example 3 — Batch process multiple PDFs into one output_dir
pdfs = [
    "./input/article1.pdf"
    , "./input/article2.pdf"
    , "./input/article3.pdf"
]

for p in pdfs:
    pdf_to_txt(
        pdf_path=p
        , output_dir="./output"
        , threshold_ratio=0.88
        , header_threshold=50
        , pages_to_skip="1-2"
    )
