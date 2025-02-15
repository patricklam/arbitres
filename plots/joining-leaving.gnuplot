set terminal pdf fontscale 0.4 background rgb "#ffffffff"
set output "joining-leaving.pdf"

set auto x
set yrange [-14:14]
set y2range [30:90]
set style data histogram
set style fill solid border -1
set boxwidth 0.9
set xtic rotate by -45 font 'Sans,12' scale 1
set style line 2 lt 1 lw 3 linecolor "#00000000"
set style histogram cluster gap 1
plot for [COL=2:3] 'joining-leaving.dat' using COL:xtic(1) with histogram notitle, 'joining-leaving.dat' using 4 with lines axes x1y2 ls 2 title "# arbitres"

