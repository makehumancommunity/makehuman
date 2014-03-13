You need:

* perl
* xsltproc
* rst2pdf

(these are readily available on any linux distro)

Download the docexport.xml file from http://www.makehuman.org/docexport.xml and save it
as docexport.xml (it's an ajax page, so don't use wget)

run "perl parse.pl", ignore the warnings.

In the new directory "rst" you should now have both a restructuredtext and a PDF.

To get an actually working PDF file you'll want the images from the server too, but in 
order to get those you need FTP access.

