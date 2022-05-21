<?php
namespace App;

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
	public function getStockData($symbol="none", $price-min="none", $price-max, $analysis="none") {
		$query = "SELECT Symbol, Price, Analysis FROM stockdb WHERE";
		$and = False
		if ($symbol != "none") {
			if ($and) { $query = $query." AND"; }
			$query = $query." Symbol = ".$symbol;
			$and = True
		}
		if ($price-min != "none") {
			if ($and) { $query = $query." AND"; }
			$query = $query." Price >= ".$price-min.;
			$and = True
		}
		if ($price-max != "none") {
			if ($and) { $query = $query." AND"; }
			$query = $query." Price <= ".$price-max.;
			$and = True
		}
		if ($analysis != 'none') {
			if ($and) { $query = $query." AND"; }
			$query = $query." Analysis = ".$analysis;
			$and = True
		}
		$stmt = $this->pdo->query($query);
		$data = [];
		while ($row = $stmt->fetch(\PDO::FETCH_ASSOC)) {
			$data[] = [
				'Symbol' => $row['Symbol'],
				'Price' => $row['Price'],
				'Analysis' => $row['Analysis'],
			];
		}
		
		return $data;
	}
}
