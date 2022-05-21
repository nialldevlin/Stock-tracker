# Stock tracker
## Technical analysis based stock screener and trader
<p>
Uses a combination of technical indicators to determine which stocks in the S&P 500 are profitable, finds the best stock, and places a trade with the Alpaca trade api (https://alpaca.markets/). It also monitors current positions and determines when to sell. Meant to be run hourly or daily from a server.
</p>

### Dependencies
- Python 3
- virtualenv
- pandas
- numpy
- alpaca-trade-api
- yahoo-fin
- SQLAlchemy

## Instructions for install on linux, or windows subsytem for linux
- Clone git repo

```
git clone https://github.com/nialldevlin/Stock-tracker.git
cd Stock-tracker
```

- Install virtualenv

```pip install virtualenv```

- Create new virtal environment

```python3 -m venv ./stracker```

- Install dependencies

```
source stracker/bin/activate
pip install numpy pandas yahoo-fin alpaca-trade-api SQLAlchemy
deactivate
```

- Add permissions and run

```
chmod 777 stock_tracker.py
chmod 777 stock_analyzer.py
./stock_tracker.py
```




		
 