import ebooklib
from ebooklib import epub
import sys

if len(sys.argv) != 2:
    print("Usage: python extract_chapters.py <epub_file>")
    sys.exit(1)

epub_path = sys.argv[1]

try:
    book = epub.read_epub(epub_path)
    with open('chapter.txt', 'w', encoding='utf-8') as f:
        for item in book.toc:
            if item.title:
                f.write(item.title + '\n')
    print("Chapter names have been saved to chapter.txt")
except Exception as e:
    print(f"Error: {e}")
