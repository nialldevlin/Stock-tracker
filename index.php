<html>
<body>

<?php
require 'vendor/autoload.php';

use App\SQLiteConnection;

$SQLC = new SQLiteConnection()
$pdo = $SQLC->connect();
if ($pdo != null)
    echo 'Connected to the SQLite database successfully!';
else
    echo 'Whoops, could not connect to the SQLite database!';

$symbol = $_GET["Symbol"]
$min-price = $_GET["min-price"]
$max-price = $_GET["max-price"]
$analysis = $_GET["analysis"]
$stock-data = $SQLC->getStochData($symbol, $min-price, $max-price, $analysis);

$firstRow = true;
echo '<div class="table-responsive"><table class="table">';
foreach ($stock-data as $row) {
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
