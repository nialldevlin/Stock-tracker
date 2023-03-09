<html>
<head>
<link rel="stylesheet" href="styles.css">
</head>
<body>

<?php
require_once('SQLiteConnection.php');
$lastModifiedTimestamp = filemtime("stockdb.sqlite");
$lastModifiedDatetime = date("d M Y H:i:s", $lastModifiedTimestamp);

$SQLC = new SQLiteConnection();
$pdo = $SQLC->connect();

echo "<div>";
if ($pdo != null)
    echo '<p>Connected to the database</p>';
else
    echo '<p>Whoops, could not connect to the SQLite database!</p>';

echo "<br>";
echo "<a href='index.html'>Return</a>";
echo "<br>";

$symbol = $_GET["Symbol"];
$min_price = $_GET["min-price"];
$max_price = $_GET["max-price"];
$analysis = $_GET["analysis"];
$stock_data = $SQLC->getStockData($symbol, $min_price, $max_price, $analysis);

echo "<p>Last Updated: ";
echo $lastModifiedDatetime;
echo "</p>";
echo "</div>";

$firstRow = true;
echo '<div class="table-responsive"><table class="table">';
foreach ($stock_data as $row) {
    if ($firstRow) {
        echo '<thead><tr>';
        foreach ($row as $key => $value) {
            echo '<th>'.$key.'</th>';
        }
        echo '</tr></thead>';
        echo '<tbody>';
        $firstRow = false;
    }

    echo '<tr>';
    foreach ($row as $value) {
		if (is_numeric($value)) {
			echo '<td>'.round($value, 2).'</td>';
		} else {
			echo '<td>'.$value.'</td>';
		}
    }
    echo '</tr>';
}
echo '</tbody>';
echo '</table></div>';
?>

</body>
</html>
