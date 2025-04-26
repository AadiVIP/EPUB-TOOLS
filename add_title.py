#!/data/data/com.termux/files/usr/bin/python
import os
import sys
import zipfile
import tempfile
import shutil
import warnings
from bs4 import BeautifulSoup
from lxml import etree
from bs4 import XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

def add_title_page(in_epub, out_epub):
    # 1) Unzip to temp dir
    tmp = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(in_epub, 'r') as zin:
            zin.extractall(tmp)
    except zipfile.BadZipFile:
        print(f"Error: {in_epub} is not a valid ZIP file")
        shutil.rmtree(tmp)
        sys.exit(1)

    # 2) Locate the OPF
    container_path = os.path.join(tmp, 'META-INF', 'container.xml')
    if not os.path.exists(container_path):
        print("Error: Missing META-INF/container.xml")
        shutil.rmtree(tmp)
        sys.exit(1)

    try:
        cont = etree.parse(container_path)
        ns = {'c': 'urn:oasis:names:tc:opendocument:xmlns:container'}
        rootfile = cont.xpath('/c:container/c:rootfiles/c:rootfile', namespaces=ns)[0]
        opf_path = os.path.join(tmp, rootfile.get('full-path'))
        opf_dir = os.path.dirname(opf_path)
    except (etree.XMLSyntaxError, IndexError) as e:
        print(f"Error parsing container.xml: {str(e)}")
        shutil.rmtree(tmp)
        sys.exit(1)

    # 3) Create title page
    title_page_content = f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
    <meta charset="utf-8"/>
    <title>Level Up Zombie</title>
    <style type="text/css">
        body {{ text-align: center; margin-top: 20%; font-family: serif; }}
        h1 {{ font-size: 2.5em; margin-bottom: 0.5em; }}
        .credit {{ font-style: italic; font-size: 1.2em; }}
    </style>
</head>
<body>
    <h1>LEVEL UP ZOMBIE</h1>
    <div class="credit">Webnovel Ripped by</div>
    <div class="credit">No Headphone Gamerz</div>
</body>
</html>"""

    # Save title page
    title_page_path = os.path.join(opf_dir, 'title_page.xhtml')
    with open(title_page_path, 'w', encoding='utf-8') as f:
        f.write(title_page_content)

    # 4) Update OPF and TOC
    try:
        # Parse OPF
        opf = etree.parse(opf_path)
        nsmap = {'opf': 'http://www.idpf.org/2007/opf'}

        # Add title page to manifest
        manifest = opf.xpath('//opf:manifest', namespaces=nsmap)[0]
        item = etree.SubElement(manifest, 'item')
        item.set('id', 'title_page')
        item.set('href', 'title_page.xhtml')
        item.set('media-type', 'application/xhtml+xml')

        # Add title page as first spine item
        spine = opf.xpath('//opf:spine', namespaces=nsmap)[0]
        itemref = etree.SubElement(spine, 'itemref')
        itemref.set('idref', 'title_page')
        spine.insert(0, itemref)  # Make it first in reading order

        # Save updated OPF
        with open(opf_path, 'wb') as f:
            f.write(etree.tostring(opf, encoding='utf-8', xml_declaration=True))

    except Exception as e:
        print(f"Error updating OPF: {str(e)}")
        shutil.rmtree(tmp)
        sys.exit(1)

    # 5) Re-zip with proper EPUB structure
    try:
        with zipfile.ZipFile(out_epub, 'w') as zout:
            # Mimetype must be first and uncompressed
            mimetype_path = os.path.join(tmp, 'mimetype')
            if os.path.exists(mimetype_path):
                with open(mimetype_path, 'rb') as f:
                    zout.writestr('mimetype', f.read(), compress_type=zipfile.ZIP_STORED)
            
            # Add remaining files
            for root, _, files in os.walk(tmp):
                for fn in files:
                    full = os.path.join(root, fn)
                    rel = os.path.relpath(full, tmp)
                    if rel != 'mimetype':
                        zout.write(full, rel)
    except Exception as e:
        print(f"Error creating output EPUB: {str(e)}")
        shutil.rmtree(tmp)
        sys.exit(1)
        
    shutil.rmtree(tmp)
    print(f"Success: Created {out_epub} with title page")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: add_title_page.py input.epub output.epub")
        sys.exit(1)
    
    if not os.path.exists(sys.argv[1]):
        print(f"Error: Input file {sys.argv[1]} not found")
        sys.exit(1)
        
    add_title_page(sys.argv[1], sys.argv[2])
