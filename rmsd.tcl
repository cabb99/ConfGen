set outfile [open rmsdv2.dat w] 
set nmol [expr [molinfo num]+1]
set nf 181
for { set r 1 } { $r <= $nf } { incr r } {
set Sumx 0
set Sumy 0
set Sumz 0
set line "$r"
for { set m 0 } { $m <= $nmol } { incr m } {
set sel [atomselect $m "name CA and resid $r and not altloc B"]
set x [$sel get {x}]
set y [$sel get {y}]
set z [$sel get {z}]
#puts "$m $r $x $y $z"
set Sumx [expr $Sumx + $x]
set Sumy [expr $Sumy + $y]
set Sumz [expr $Sumz + $z]
}
set xave [expr $Sumx/($nmol+1)]
set yave [expr $Sumy/($nmol+1)]
set zave [expr $Sumz/($nmol+1)]
for { set m 0 } { $m < $nmol } { incr m } {
set sel [atomselect $m "name CA and resid $r and not altloc B"]
set x [$sel get {x}]
set y [$sel get {y}]
set z [$sel get {z}]
#puts "$x $y $z $xave $yave $zave"
set rmsd [expr ((($x-$xave)**2+($y-$yave)**2+($z-$zave)**2)**0.5)]
append line "," $rmsd 
}
puts "$line"
puts $outfile "$line"
} 
close $outfile
