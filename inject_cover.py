#!/data/data/com.termux/files/usr/bin/python
import os
import sys
import zipfile
import tempfile
import shutil
from lxml import etree

def inject_cover(in_epub, out_epub, cover_path, overwrite=True):
    """Adds/overwrites cover image in EPUB"""
    if not os.path.exists(cover_path):
        print(f"Error: Cover image {cover_path} not found")
        sys.exit(1)

    tmp = tempfile.mkdtemp()
    try:
        # 1) Extract EPUB
        with zipfile.ZipFile(in_epub, 'r') as zin:
            zin.extractall(tmp)

        opf_dir, opf_path = find_opf_path(tmp)

        # 2) Handle existing cover
        opf = etree.parse(opf_path)
        ns = {'opf': 'http://www.idpf.org/2007/opf'}
        
        # Remove existing cover references
        for item in opf.xpath('//opf:item[@properties="cover-image"]', namespaces=ns):
            old_cover_path = os.path.join(opf_dir, item.get('href'))
            if os.path.exists(old_cover_path):
                os.unlink(old_cover_path)
            item.getparent().remove(item)

        # 3) Add new cover
        cover_dest = os.path.join(opf_dir, 'cover.jpg')
        shutil.copy2(cover_path, cover_dest)

        # 4) Update OPF manifest
        manifest = opf.xpath('//opf:manifest', namespaces=ns)[0]
        etree.SubElement(manifest, 'item', {
            'id': 'cover-image',
            'href': 'cover.jpg',
            'media-type': 'image/jpeg',
            'properties': 'cover-image'
        })

        with open(opf_path, 'wb') as f:
            f.write(etree.tostring(opf, encoding='utf-8', pretty_print=True))

        # 5) Rebuild EPUB
        rebuild_epub(tmp, out_epub)
        print(f"Success: {'Overwrote' if overwrite else 'Added'} cover in {out_epub}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def find_opf_path(tmp_dir):
    """Locates OPF file path in EPUB container"""
    container_path = os.path.join(tmp_dir, 'META-INF', 'container.xml')
    if not os.path.exists(container_path):
        raise Exception("Missing META-INF/container.xml - invalid EPUB")

    cont = etree.parse(container_path)
    ns = {'c': 'urn:oasis:names:tc:opendocument:xmlns:container'}
    rootfile = cont.xpath('/c:container/c:rootfiles/c:rootfile', namespaces=ns)[0]
    opf_path = os.path.join(tmp_dir, rootfile.get('full-path'))
    return os.path.dirname(opf_path), opf_path

def rebuild_epub(tmp_dir, out_path):
    """Repackages EPUB with proper structure"""
    with zipfile.ZipFile(out_path, 'w') as zout:
        # Mimetype must be first and uncompressed
        mt_path = os.path.join(tmp_dir, 'mimetype')
        if os.path.exists(mt_path):
            with open(mt_path, 'rb') as f:
                zout.writestr('mimetype', f.read(), compress_type=zipfile.ZIP_STORED)
        
        # Add remaining files
        for root, _, files in os.walk(tmp_dir):
            for fn in files:
                if fn == 'mimetype':
                    continue
                abs_path = os.path.join(root, fn)
                rel_path = os.path.relpath(abs_path, tmp_dir)
                zout.write(abs_path, rel_path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: inject_cover.py input.epub output.epub cover.jpg [--force]")
        print("Note: --force is enabled by default")
        sys.exit(1)
    
    overwrite = True  # Enabled by default
    cover_arg = sys.argv[3] if len(sys.argv) > 3 else 'cover.jpg'
    inject_cover(sys.argv[1], sys.argv[2], cover_arg, overwrite)
