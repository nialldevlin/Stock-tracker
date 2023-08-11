from simulate import Simulate
import yaml

with open("config.yaml", 'r') as f:
    config = yaml.safe_load(f)

s = Simulate(starting_cash=config["simulate"]["starting_cash"],
             period=config["data"]["period"],
             interval=config["data"]["interval"],
             csv=config["data"]["csv"],
             rw=config["data"]["rw"])



