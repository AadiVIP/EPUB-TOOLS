📚 EPUB Tools Collection

  

A suite of scripts and utilities to enhance, extract, and package EPUB files for personal ebook libraries, especially web novel rips or incomplete books.


---

Table of Contents

Features

Scripts

1. inject_cover.py

2. fix_epub_titles.py

3. add_title.py

4. extract_chapters.py

5. heading fixer docx.py

6. make_epub.sh


Installation

Usage

Workflow Examples

Troubleshooting

Notes

License



---

Features

Inject Cover: Replace or add a high-quality cover image.

Fix Titles: Auto-generate missing <h1> titles from the EPUB navigation files (EPUB 2/3).

Add Title Page: Create a custom title page as the book’s opening.

Extract Chapters: Dump chapter titles from an EPUB's TOC to a text file.

DOCX Heading Fixer: Fix misformatted or missing headings inside DOCX files.

Build EPUB: Stitch Markdown-converted chapters into a single EPUB via Bash.

Proper EPUB Packaging: Maintains EPUB standards (e.g., mimetype first uncompressed).

Lightweight and Fast: Uses lxml, BeautifulSoup, and pandoc for quick processing.



---

Scripts

1. inject_cover.py

Function: Adds or overwrites the cover image in an EPUB.

Command:

python inject_cover.py input.epub output.epub cover.jpg


2. fix_epub_titles.py

Function: Inserts missing <h1> titles into each chapter HTML/XHTML, using the EPUB TOC (NCX or NAV).

Command:

python fix_epub_titles.py input.epub output.epub


3. add_title.py

Function: Generates and inserts a styled title page at the start of an EPUB.

Command:

python add_title.py input.epub output.epub


4. extract_chapters.py

Function: Reads an EPUB’s TOC and writes all chapter titles to chapter.txt.

Command:

python extract_chapters.py input.epub


5. heading fixer docx.py

Function: Automatically fixes misformatted DOCX chapter headings. Useful for batch-fixing heading levels before EPUB creation.

Command:

python "heading fixer docx.py" input_folder/

Notes:

Processes all DOCX files in the provided folder.

Ensures consistent heading styles for proper EPUB conversion.



6. make_epub.sh

Function: Converts a series of DOCX chapter files into Markdown, cleans headings, and assembles them into a single EPUB with metadata and TOC via pandoc.

Usage:

1. Name your chapters ch01.docx through ch21.docx (or adjust the seq range).


2. Update the script’s TITLE, AUTHOR, PUBLISHER, and OUT variables.


3. Run:

chmod +x make_epub.sh
./make_epub.sh


4. Result: The Weakest Link Book One.epub (as defined in OUT).





---

Installation

Requirements

Python 3.6+

Bash (for make_epub.sh)

Install Python dependencies:

pip install lxml beautifulsoup4 ebooklib

Pandoc (for make_epub.sh):

sudo apt-get install pandoc   # Debian/Ubuntu

Optional (Android/Termux):

pkg install python pandoc
pip install lxml beautifulsoup4 ebooklib



---

Usage

You can run each script standalone, or chain them for a full workflow:

1. Inject Cover


2. Fix Chapter Titles


3. Add Title Page


4. Extract Chapter Names


5. (Optional) Fix DOCX Headings


6. (Optional) Generate EPUB from DOCX



Example chain:

python inject_cover.py raw.epub temp1.epub my_cover.jpg
python fix_epub_titles.py temp1.epub temp2.epub
python add_title.py temp2.epub temp3.epub
python extract_chapters.py temp3.epub
python "heading fixer docx.py" chapters_folder/
./make_epub.sh


---

Workflow Examples

graph TD;
    A[Raw EPUB] --> B[inject_cover.py]
    B --> C[fix_epub_titles.py]
    C --> D[add_title.py]
    D --> E[extract_chapters.py]
    E --> F[Markdown Chapters]
    F --> G["heading fixer docx.py"]
    G --> H[make_epub.sh]
    H --> I[Final EPUB]


---

Troubleshooting

EPUB appears blank

Ensure mimetype is uncompressed and first in archive.

Use the provided rebuild logic in scripts.


Cover image not updating

Clear reader cache.

Confirm cover.jpg path and properties="cover-image" in OPF.


Chapter titles missing after fix

Verify EPUB has a valid NCX (EPUB2) or NAV (EPUB3) file.



---

Notes

Always backup your EPUB before modifications.

Scripts assume standard EPUB structure; heavily corrupted files may fail.

You can edit the title page template in add_title.py to customize styling.



---

License

MIT License — freely modify and share.


---

If you want, I can prepare the updated README.md file for you as a downloadable file. Would you like that?

