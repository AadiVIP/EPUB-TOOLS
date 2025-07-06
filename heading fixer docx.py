from docx import Document
import os

# Number of chapters
CHAPTER_COUNT = 6

for i in range(1, CHAPTER_COUNT + 1):
    filename = f'ch{i}.docx'
    if not os.path.isfile(filename):
        print(f'File not found: {filename}')
        continue

    print(f'Processing {filename}...')

    doc = Document(filename)
    fixed = False

    for para in doc.paragraphs:
        if para.text.strip():  # Find first non-empty paragraph
            para.style = 'Heading 1'  # Set to Heading 1
            fixed = True
            print(f'✔️ Fixed heading in {filename}: "{para.text.strip()}"')
            break

    if fixed:
        doc.save(filename)
    else:
        print(f'⚠️ No non-empty paragraph found in {filename}')

print('✅ All files processed.')
