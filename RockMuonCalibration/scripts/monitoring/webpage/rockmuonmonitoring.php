<!-- Author: Chris Marshall             -->
<!-- e-mail: marshall@pas.rochester.edu -->
<!-- Date: 2011/11/01                   -->

<head>

 	<style type="text/css" media="screen">
		<?php include('plots_sty.css'); ?>
	</style>

	<title>Rock muon plots</title>

</head>

	<body>

		<table border="0" width="100%">

			<td>

				<div id="content">

<?php
function console_log( $data ){
   echo '<script>';
   echo 'console.log('. json_encode( $data ) .')';
   echo '</script>';
 }


$day=$_GET["day"];
$month=$_GET["month"];
$year=$_GET["year"];


$plotname = array("Protons per pulse","Time slices per POT", "MINERvA rock muons per POT", "MINOS tracks per POT", "MINOS-matched rock muons per POT","MINERvA muon cluster PE", "MINERvA-MINOS track deltaT", "MINERvA-MINOS gate deltaT", "MINOS Prange vs. Pcurvature", "Time between gates", "Dead time fraction", "Dead time vs. intensity", "Peak muon cluster PE", "Protons per pulse", "Time slices per POT",   "MINERvA rock muons per POT",   "MINOS tracks per POT",   "MINOS-matched rock muons per POT",   "MINOS tracks per POT (MINOS gate match)",   "MINOS-matched rock muons per POT (MINOS gate match)",   "MINOS tracks per POT (MINOS gate match)",   "MINOS-matched rock muons per POT (MINOS gate match)",   "Rock mu- per POT ",   "Rock mu+ per POT ",   "Daily rock muons energy distribution",   "High energy rock mu- summary",   "Mid energy rock mu- summary",   "Low energy rock mu- summary",   "High energy rock mu+ summary",   "Mid energy rock mu+ summary",   "Low energy rock mu+ summary");

$hasref = array(0,1,2,3,4,5,6,7,8,9,10,11,18,19,22,23,24);

$pagetitle = "Rock muon monitoring plots: $year-$month-$day";

echo "<h3><center><b>" .$pagetitle. "</b></center></h3>";

echo "<div id='runlist'>";
echo "<center>";

echo '<table border=1 width=1500>';

for ($a=0; $a<sizeof($plotname); $a++)
  {
    /*
  if ($a == 0) $title = "Protons per pulse";
  if ($a == 1) $title = "Time slices per POT";
  if ($a == 2) $title = "MINERvA rock muons per POT";
  if ($a == 3) $title = "MINOS tracks per POT";
  if ($a == 4) $title = "MINOS-matched rock muons per POT";
  if ($a == 5) $title = "MINERvA muon cluster PE";
  if ($a == 6) $title = "MINERvA-MINOS deltaT";
  if ($a == 7) $title = "MINOS Prange vs. Pcurvature";
  if ($a == 8) $title = "Time between gates";
  if ($a == 9) $title = "Peak muon cluster PE";
  if ($a == 10) $title = "Protons per pulse";
  if ($a == 11) $title = "Time slices per POT";
  if ($a == 12) $title = "MINERvA rock muons per POT";
  if ($a == 13) $title = "MINOS tracks per POT";
  if ($a == 14) $title = "MINOS-matched rock muons per POT";
    */
    $title = $plotname[$a];
    $npage = "Page $a: $title";
    $rpage = "Ref  $a: $title";
    $index = sprintf("%02d", $a);

    $rname="plot_$index.png";

    $rplot = "<td> <ul class='NoBullet'> <li> <ftit> $npage </ftit> </ul> <center> <a href='dump/daily_$year-$month-$day/$rname' target='_blank'> <img src='dump/daily_$year-$month-$day/$rname' width=90% border=0> </a> </center> </td>";
    $ref   = "<td> <ul class='NoBullet'> <li> <ftit> $rpage </ftit> </ul> <center> <a href='dump/reference/$rname' target='_blank'> <img src='dump/reference/$rname' width=90% border=0> </a> </center> </td>";
    $noref   = "<td> <ul class='NoBullet'> <li> <ftit> $rpage </ftit> </ul> <center> <a href='dump/reference/noref.png' target='_blank'> <img src='dump/reference/noref.png' width=90% border=0> </a> </center> </td>";

    echo "<tr>";
    echo $rplot;
    if (in_array($a, $hasref)) {
      echo $ref;
	} else {
      echo $noref;
    }
    //if( $a < 12 ) echo $ref;
    ////else if( $a < 18 ) echo $noref;
    echo "</tr>\n";

  }

echo '</table>';
echo "</div>";
echo "</center>";

?>

				</div>

			</td>

		</table>

	</body>

</html>


