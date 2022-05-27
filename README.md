# Stock tracker
## Technical analysis based stock screener and trader
<p>
Uses a combination of technical indicators to determine which stocks in the S&P 500 are profitable, finds the best stock, and places a trade with the Alpaca trade api (https://alpaca.markets/). It also monitors current positions and determines when to sell. Meant to be run hourly or daily from a server.

WARNING:
THIS PROGRAM DOES NOT CONSTITUTE INVESTMENT ADVICE AND THE CREATOR OF THIS PROJECT IS NOT RESPONSIBLE FOR ANY MONETARY GAIN OR LOSS FROM THE USE OF THIS REPOSITORY- SEE LICENSE FOR MORE INFORMATION
</p>

### Dependencies
- Python 3
- virtualenv
- pandas
- numpy
- alpaca-trade-api
- yahoo-fin
- SQLite3
- dotenv

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
pip install numpy pandas yahoo-fin alpaca-trade-api SQLAlchemy python-dotenv
deactivate
```

- This project uses the dotenv library for environmental variables. Simply create a file named '.env' in the project directory with your API keys. Mine looks like this. The only thing that must match is the key names. Simply comment/uncomment the appropriate lines for paper or live trading.

```
# Paper trading keys
APCA_API_SECRET_KEY="sample_secret_key"
APCA_API_KEY_ID="sample_public_key"
APCA_ENDPOINT="https://paper-api.alpaca.markets"
# Live trading keys
# APCA_API_SECRET_KEY="sample_secret_key"
# APCA_API_KEY_ID="sample_public_key"
# APCA_ENDPOINT="https://api.alpaca.markets"
```

- Add permissions and run

```
chmod 777 stock_tracker.py
chmod 777 stock_analyzer.py
./stock_tracker.py
```




		
 
