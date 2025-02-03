This is a simple project for extracting legal opinions (avize) from PDFs written in Romanian, and it adds them to a bootstrap html table. 

The project has an observer that checks for file system activity in the /input directory. If a pdf file is added, it's scanned.
The content from the PDFs is analyzed using tesseract, and then the program searches through the content of the files for opinions declared in the 'opinions.txt' file. 
It then checks if the characters before the match correspond to a checked box or an unchecked box. This is a workaround for the inability of the tesseract library to detect icons. 
Different characters may be identified by the lib based on the PDF documents provided. So far, these are the characters for a checked box: X, M, m, B, and these are for an unchecked one: O, o, Ol, D.
Using these matches it then writes the html files into the views directory.
