import os, fitz, time

class PdfOut:
    def __init__(self):
        cwd = os.getcwd()
        
        # 3 pdf files exist in the /temp folder
        self.files = ['pdf1.pdf', 'pdf2.pdf', 'pdf3.pdf']
        self.dir_in = os.path.join(cwd, 'temp')
        # /archive directory exists - this is where composite pdf will be saved
        self.dir_out = os.path.join(cwd, 'archive')
        # /raw directory exists - this is where single page pdf must be moved at the end of the script
        self.dir_store = os.path.join(cwd, 'raw')
        
        self.bookmarks = ['file1', 'file2', 'file3']
        self.file_out = "Combined_File.pdf"

    def writePDFusingClose(self):
            composite_pdf = fitz.open()
            for f in self.files:
                new_page = fitz.open(os.path.join(self.dir_in, f))
                composite_pdf.insert_pdf(new_page)
                new_page.close()
            new_toc = []
            page_count = 1
            for item in self.bookmarks:
                entry = [1, item, page_count]
                new_toc.append(entry)
                page_count += 1
            composite_pdf.set_toc(new_toc)
            composite_pdf.save(os.path.join(self.dir_out, self.file_out), deflate=True, garbage=3)
            composite_pdf.close()

    def writePDFusingWith(self):
        with fitz.open() as composite_pdf:
            for f in self.files:
                with fitz.open(os.path.join(self.dir_in,f)) as new_page:
                    composite_pdf.insert_pdf(new_page)
            new_toc = []
            page_count = 1
            for item in self.bookmarks:
                entry = [1, item, page_count]
                new_toc.append(entry)
                page_count += 1
            composite_pdf.set_toc(new_toc)
            composite_pdf.save(os.path.join(self.dir_out, self.file_out), deflate=True, garbage=3)
    
    def cleanUp(self):
        for file_name in os.listdir(self.dir_in):
            os.replace(os.path.join(self.dir_in, file_name), os.path.join(self.dir_store, file_name))
        os.rmdir(self.dir_in)

new_file = PdfOut()
new_file.writePDFusingClose()
# new_file.writePDFusingWith()
print("All methods completed, starting 20sec sleep")
time.sleep(20)
new_file.cleanUp()