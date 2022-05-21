<!doctype html>

<html>

<head>
	<title>S&P 500 Stock Tracker</title>
	<meta name="description" content="S&P Stock Tracker">
	<meta name="keywords" content="stock S&P finance analysis">
</head>

<body>
	<h1>S&P 500 Stocks and Analysis</h1>
	<p>Refreshes every hour</p>
	<table>
	<thead>
	<tr>
		<td>Stock</td>
		<td>Price</td>
		<td>Analysis</td>
		<td>Total Score</td>
	</tr>
	</thead>
	<tbody>
	<?php
	$db_file = "sqlite:///home/proffessordevnito/Documents/Python_Projects/Stock-tracker/stockdb.sqlite";
	$db = new PDO($db_file) or die("cannot open database");
	$query = "SELECT * FROM STOCKDB";
	$stmt = $db->prepare($query);
	$stmt->execute(array("%$query%"));
	while ($row = $stmt->fetch()) {
		echo "<tr>";
		echo "<td>".$row["Symbol"]."</td>";
		echo "<td>".$row["Price"]."</td>";
		echo "<td>".$row["Analysis"]."</td>";
		echo "<td>".$row["Score"]."</td>";
		echo "<tr>";
	}
	?>
	</tbody>
	</table>
</body>

</html>
