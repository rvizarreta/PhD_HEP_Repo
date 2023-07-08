list="$(ls | grep playlist_daily_.*txt$)"
htmladd=/web/sites/minerva.fnal.gov/htdocs/nusoft/minervacal
setupauth

pushd $htmladd
cp daily_muon_monitoring.html daily_muon_monitoring.html.bak
popd

for i in $list
do
    year=${i:15:4}
    month=${i:20:2}
    day=${i:23:2}
    echo Force plotting playlist-${year}-${month}-${day}
    python make_plots_force.py $year $month $day
done

pushd $htmladd
cp daily_muon_monitoring.html.bak daily_muon_monitoring.html
popd
