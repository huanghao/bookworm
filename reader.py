import subprocess

from pyPdf import PdfFileReader


def get_pdf_num_pages(path):
    reader = PdfFileReader(open(path, 'rb'))
    return reader.getNumPages()


def get_pdf_text(path):
    return subprocess.check_output(['pdf2txt.py', path])



