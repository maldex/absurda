#!/bin/bash
# sudo apt-get install -y wkhtmltopdf
htmlFile=$1
pdfFile="${htmlFile::-4}pdf"
echo ${htmlFile}
echo ${pdfFile}

wkhtmltopdf ${htmlFile} ${pdfFile}
lpstat -d # -p
lp ${pdfFile}

sleep 12
echo  yseeeee