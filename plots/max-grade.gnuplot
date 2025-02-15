set terminal pdf fontscale 0.4  background rgb "#ffffffff"
set output "max-grade.pdf"

set auto x
set style data histogram
set style histogram cluster gap 1
set style fill solid border -1
set boxwidth 0.9
set xtic rotate by -45 scale 0
plot "max-grade.dat" using 4:xtic(1) notitle
