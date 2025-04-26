#!/data/data/com.termux/files/usr/bin/python
import os
import sys
import zipfile
import tempfile
import shutil
import warnings
from bs4 import BeautifulSoup, SoupStrainer
from lxml import etree
from bs4 import XMLParsedAsHTMLWarning

# Suppress XML-as-HTML warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

def add_titles(in_epub, out_epub):
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

    # 3) Find navigation document
    try:
        opf = etree.parse(opf_path)
        nsmap = {'opf': 'http://www.idpf.org/2007/opf'}
        
        # EPUB3 nav detection
        nav_item = opf.xpath('//opf:item[@properties="nav"]', namespaces=nsmap)
        if nav_item:
            nav_href = nav_item[0].get('href')
            nav_file = os.path.normpath(os.path.join(opf_dir, nav_href))
            toc_map = parse_epub3_nav(nav_file)
        else:
            # EPUB2 fallback
            ncx_item = opf.xpath('//opf:item[@media-type="application/x-dtbncx+xml"]', namespaces=nsmap)
            if ncx_item:
                ncx_href = ncx_item[0].get('href')
                ncx_file = os.path.normpath(os.path.join(opf_dir, ncx_href))
                toc_map = parse_epub2_ncx(ncx_file)
            else:
                print("Error: No navigation document found")
                shutil.rmtree(tmp)
                sys.exit(1)
    except Exception as e:
        print(f"Error processing OPF: {str(e)}")
        shutil.rmtree(tmp)
        sys.exit(1)

    # 4) Inject titles
    for rel_href, title in toc_map.items():
        full_path = os.path.normpath(os.path.join(opf_dir, rel_href))
        if not os.path.isfile(full_path):
            continue
            
        try:
            with open(full_path, 'rb') as f:
                chap = BeautifulSoup(f, 'lxml', parse_only=SoupStrainer('body'))
            
            if chap.body:
                h1 = chap.new_tag('h1', **{'class': 'chapter-title'})
                h1.string = title
                chap.body.insert(0, h1)
                
                with open(full_path, 'wb') as f:
                    f.write(chap.encode('utf-8'))
        except Exception as e:
            print(f"Warning: Failed to process {rel_href}: {str(e)}")
            continue

    # 5) Re-zip
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
    print(f"Success: Created {out_epub}")

def parse_epub3_nav(nav_file):
    """Parse EPUB3 navigation document"""
    toc_map = {}
    try:
        with open(nav_file, 'rb') as f:
            soup_nav = BeautifulSoup(f, 'lxml-xml')
        
        for a in soup_nav.find_all('a', href=True):
            href = a['href'].split('#')[0]
            toc_map[href] = a.get_text(strip=True)
    except Exception as e:
        print(f"Warning: EPUB3 nav parsing failed: {str(e)}")
    return toc_map

def parse_epub2_ncx(ncx_file):
    """Parse EPUB2 NCX document"""
    toc_map = {}
    try:
        with open(ncx_file, 'rb') as f:
            soup_ncx = BeautifulSoup(f, 'lxml-xml')
        
        for nav_point in soup_ncx.find_all('navpoint'):
            text = nav_point.find('text')
            content = nav_point.find('content')
            if text and content:
                href = content['src'].split('#')[0]
                toc_map[href] = text.get_text(strip=True)
    except Exception as e:
        print(f"Warning: EPUB2 NCX parsing failed: {str(e)}")
    return toc_map

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: fix_epub_titles.py input.epub output.epub")
        sys.exit(1)
    
    if not os.path.exists(sys.argv[1]):
        print(f"Error: Input file {sys.argv[1]} not found")
        sys.exit(1)
        
    add_titles(sys.argv[1], sys.argv[2])
