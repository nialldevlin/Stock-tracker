# Stock tracker
## Instructions for install on linux, or windows subsytem for linux
<p>
Names of folders and virtual environments are just examples,<br>
use whatever you want.<br>

- Create new project directory

```mkdir ~/stocktracker && cd ~/stocktracker```

- Clone git repo

```git clone git@github.com:nialldevlin/Stock-tracker.git```

- Install virtualenv if not installed

```pip install virtualenv```

- Create new virtal environment

```python3 -m venv ./stracker```

- Install dependencies

```
source stracker/bin/activate
pip install numpy pandas yfinance telegram_send matplotlib cryptography
deactivate
```

- Add permissions and run

```
chmod 777 stock_tracker.py
chmod 777 stock_analyzer.py
./stock_tracker.py
```




		
 
