set terminal pdf fontscale 0.4 background rgb "#ffffffff"
set output "roster-size-jr-sr.pdf"

set auto x
set yrange [15:70]
set y2range [0:40]
set style fill solid border -1
set boxwidth 0.9
set xtic rotate by -45 font 'Sans,12' scale 1
set style line 2 lt 1 lw 3 linecolor "#00000000"
set style histogram rowstacked gap 1
set key autotitle columnheader
set y2tics auto

plot for [COL=3:4] 'roster-size-jr-sr.dat' using COL:xtic(1) with histogram, 'roster-size-jr-sr.dat' using 2 with lines axes x1y2 ls 2 title "% Women"
