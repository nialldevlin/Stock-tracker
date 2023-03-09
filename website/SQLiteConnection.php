<?php
require_once("Config.php");

/**
 * SQLite connnection
 * Credit https://www.sqlitetutorial.net/sqlite-php/connect/
 */
class SQLiteConnection {
    /**
     * PDO instance
     * @var type 
     */
    private $pdo;

    /**
     * return in instance of the PDO object that connects to the SQLite database
     * @return \PDO
     */
    public function connect() {
        if ($this->pdo == null) {
            $this->pdo = new \PDO("sqlite:" . Config::PATH_TO_SQLITE_FILE);
        }
        return $this->pdo;
    }
	/**
	 * Get stock data from database
	 * @return data
	 */
	public function getStockData($symbol, $price_min, $price_max, $analysis) {
		$query = "SELECT * FROM stockdb";
		$params = True;
		if ($symbol == "" && $price_min == "" && $price_max == "" && $analysis == "") {
			$params = False;
		}
		$and = False;
		if ($params) {
			$query .= " WHERE ";
			if ($symbol != "") {
				if ($and) { $query .= " AND "; }
				$query .= "Symbol = '";
				$query .= $symbol;
				$query .= "'";
				$and = True;
			}
			if ($price_min != "") {
				if ($and) { $query .= " AND "; }
				$query .= "Price >= '";
				$query .= $price_min;
				$query .= "'";
				$and = True;
			}
			if ($price_max != "") {
				if ($and) { $query .= " AND "; }
				$query .= "Price <= '";
				$query .= $price_max;
				$query .= "'";
				$and = True;
			}
			if ($analysis != "" && $analysis !='All') {
				if ($and) { $query .= " AND "; }
				$query .= "Analysis = '";
				$query .= $analysis;
				$query .= "'";
				$and = True;
			}
		}
		$result = $this->pdo->prepare($query);
		try {
     		$result->execute();
		}
		Catch(PDOException $e)
		{
			echo "Statement failed: " . $e->getMessage();
			return false;
		}
		$result = $this->pdo->query($query);
		$data = [];
		while ($row = $result->fetch(PDO::FETCH_ASSOC)) {
			$data[] = array_slice($row, 1);
		}
		return $data;
	}
}
?>
