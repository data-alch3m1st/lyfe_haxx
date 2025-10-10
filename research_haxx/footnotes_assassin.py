import pdfplumber
import pandas as pd
from collections import Counter
import os

def extract_text_without_footnotes(pdf_path, threshold_ratio=0.85):
    """
    Extracts text from a PDF, removing words that are smaller than a threshold
    compared to the majority font size on each page. (As the intent is to remove 
    all footnotes and other small non-body text for an output which will be 
    exported to a text-to-speech app.) This will be ideal for grad students, 
    researchers and academics who need to have the ability to consume scholarly 
    works on the go.
    
    Args:
        pdf_path (str): Path to the PDF file
        threshold_ratio (float): Words with height smaller than this ratio of 
                                 the most common height will be considered footnotes
    
    Returns:
        str: Entire document text without footnotes
    """
    all_pages_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            words = page.extract_words()
            if not words:
                continue

            df = pd.DataFrame(words)

            # Determine the most common height
            height_counts = Counter(df['height'])
            most_common_height = height_counts.most_common(1)[0][0]

            # Define height threshold
            height_threshold = most_common_height * threshold_ratio

            # Filter words above threshold
            filtered_words = df[df['height'] >= height_threshold]

            # Reconstruct text in reading order
            filtered_words = filtered_words.sort_values(by=[ 'top', 'x0'])
            page_text = " ".join(filtered_words['text'].tolist())

            all_pages_text.append(page_text)

    # Join all pages with a newline between pages
    return "\n\n".join(all_pages_text)


# ---------------- Example usage ---------------- #

pdf_path = "./input/sample.pdf"
output_dir = './output/'

# Make sure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Extract text without footnotes
cleaned_text = extract_text_without_footnotes(pdf_path)

# Build output filename
base_name = os.path.splitext(os.path.basename(pdf_path))[0]
output_filename = f"{base_name}_CLEANED_TEXT.txt"
output_path = os.path.join(output_dir, output_filename)

# Write to a single text file
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(cleaned_text)

print(f"Cleaned text exported to: {output_path}")