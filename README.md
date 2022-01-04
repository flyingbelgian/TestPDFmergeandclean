# TestPDFmergeandclean
This is some test code to illustrate a problem of files not being closed by PyMuPDF, making it impossible to do file cleanup at the end of the script.

Original question as posted on StackOverflow:

I can't figure out why I'm getting a PermissionError when trying to clean up some temporary pdf files that are no longer needed.

My script downloads a bunch of single page pdf's into a /temp folder, then uses PyMuPDF to merge them into a single pdf. At the end of the script, when the merged file has been created, a cleanup function is supposed to move the pdf's from the temp folder to a another folder so I can delete the temp folder. It's when everything else is done, at the end, that I get the permission error when trying to move the temp files.

I tried 2 methods to generate the pdf without leaving files open at the end: 1 as per the [fitz wiki][1] using `open()` and then `close()`, and the other using `with` to ensure that nothing was being left open unintentionally. I included a simplification of what I'm trying to do, which results in exactly the same PermissionError. Both methods I used are in there, which can be tried by commenting out either one of the methods when initiation the object. The scripts assumes some things to be present as defined in the dubinit of the PdfOut class:

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
    # time.sleep(10)
    new_file.cleanUp()

As you can see I even tried putting in a 10sec delay to allow for any scanning or system background operations to finish, but it didn't make a difference. In fact I actually tried manually deleting the files in windows explorer while the 10sec delay was ticking and it told me the file was locked by Python (so not some other system process). This leads me to believe PyMuPDF/fitz somehow keeps those files open in the python process even though the use of `with` should cause it to relinquish the files when completed with that specific operation.

This is the error message it generates:

    Traceback (most recent call last):
      File "d:\GitHub\TestPDFmergeandclean\main.py", line 52, in <module>
        new_file.cleanUp()
      File "d:\GitHub\TestPDFmergeandclean\main.py", line 45, in cleanUp
        os.replace(os.path.join(self.dir_in, file_name), os.path.join(self.dir_store, file_name))
    PermissionError: [WinError 32] The process cannot access the file because it is being used by another process: 'D:\\GitHub\\TestPDFmergeandclean\\temp\\pdf1.pdf' -> 'D:\\GitHub\\TestPDFmergeandclean\\raw\\pdf1.pdf'

Everything works as expected, the combined pdf is generated with the ToC in the folder where it's supposed to go, it's just the problem with the cleanup of the temp folder. For the life of me I can't find anywhere in the PyMuPDF documentation any other way of forcibly closing out docs other than with the use of .close() ...

Anybody have any idea what I'm doing wrong, or another suggestion to achieve the cleanup of the temp folder as I'm trying to achieve?


  [1]: https://github.com/pymupdf/PyMuPDF/wiki/Inserting-Pages-from-other-PDFs
