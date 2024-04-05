#!/bin/sh
echo 'Building my graphs...'
rm -rf output
mkdir output
ggrapher 162833:ad -o me.dot && dot -Tpdf me.dot > me.pdf && dot -Tpng me.dot > me.png && ggrapher 6871:ad -o all.dot && dot -Tpdf all.dot > all_ksu.pdf && dot -Tpng all.dot > all_ksu.png
mv *.png output/
mv *.pdf output/
rm *.dot