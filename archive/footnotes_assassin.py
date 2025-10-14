# footnotes_assassin_v2.4.2 #

import pdfplumber
import pandas as pd
from collections import Counter
import os

import pdfplumber
import pandas as pd
from collections import Counter
import os

def extract_text_without_footnotes(
    pdf_path
    , threshold_ratio=0.90
    , header_threshold=None  # e.g., 50 means: remove anything within top 50 units of page
):
    """
    Extracts text from a PDF, removing:
    - Words that are smaller than a threshold relative to the main text (footnotes)
    - Words within a specified top region of each page (headers), if header_threshold is set
    
    Args:
        pdf_path (str): Path to the PDF file
        threshold_ratio (float): Words with height smaller than this ratio of 
                                 the most common height will be considered footnotes
        header_threshold (float or None): Distance from top of page (in points) to treat as header.
                                          If None, headers are not filtered.
    
    Returns:
        str: Entire document text without footnotes and optional headers
    """
    all_pages_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            words = page.extract_words()
            if not words:
                continue

            df = pd.DataFrame(words)

            # Remove headers if header_threshold is set
            if header_threshold is not None:
                df = df[df['top'] > header_threshold]

            # Determine the most common height from remaining words
            if df.empty:
                continue
            height_counts = Counter(df['height'])
            most_common_height = height_counts.most_common(1)[0][0]

            # Define height threshold
            height_threshold = most_common_height * threshold_ratio

            # Filter out footnotes by height
            filtered_words = df[df['height'] >= height_threshold]

            # Reconstruct text in reading order
            filtered_words = filtered_words.sort_values(by=[ 'top', 'x0'])
            page_text = " ".join(filtered_words['text'].tolist())

            all_pages_text.append(page_text)

    return "\n\n".join(all_pages_text)


# ---------------- Example usage ---------------- #

pdf_path = "sample.pdf"
output_dir = './output/'

# Create output directory if needed
os.makedirs(output_dir, exist_ok=True)

# Adjust header_threshold per PDF as needed (e.g., 50 points from top)
cleaned_text = extract_text_without_footnotes(
    pdf_path
    , threshold_ratio=0.90
    , header_threshold=50  # set to None if not needed
)

# Build output filename
base_name = os.path.splitext(os.path.basename(pdf_path))[0]
output_filename = f"{base_name}_CLEANED_TEXT.txt"
output_path = os.path.join(output_dir, output_filename)

# Write to a single text file
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(cleaned_text)

print(f"Cleaned text exported to: {output_path}")



# NOTE: If you have some random words, phrases, watermarks or other nonsense that seems to be persistent,

    """
    Notes: 
    The script used pdfplumber's 'extract_words' method, which provides 
    the raw height of each word. The script then uses a ratio which eliminates 
    words that are 15% (or more) smaller then the main body text words. The result 
    (theoretically) is a text file with all of the content minus the footnotes and 
    other 'marginalia' which is not ideal to a text-to-speech experience.
    """