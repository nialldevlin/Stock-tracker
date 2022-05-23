<html>
<body>

<?php
require_once('SQLiteConnection.php');
$lastModifiedTimestamp = filemtime("stockdb.sqlite");
$lastModifiedDatetime = date("d M Y H:i:s", $lastModifiedTimestamp);

$SQLC = new SQLiteConnection();
$pdo = $SQLC->connect();
if ($pdo != null)
    echo 'Connected to the SQLite database successfully!';
else
    echo 'Whoops, could not connect to the SQLite database!';

echo "<br>";
echo "<a href='index.html'>Return</a>";
echo "<br>";
echo "Results: <br>";

$symbol = $_GET["Symbol"];
$min_price = $_GET["min-price"];
$max_price = $_GET["max-price"];
$analysis = $_GET["analysis"];
$stock_data = $SQLC->getStockData($symbol, $min_price, $max_price, $analysis);

echo "Last Updated: ";
echo $lastModifiedDatetime;

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
        echo '<td>'.$value.'</td>';
    }
    echo '</tr>';
}
echo '</tbody>';
echo '</table></div>';
?>

</body>
</html>
