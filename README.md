# World Cup Prediction Model (Elo Rating System)

This project simulates and predicts international football outcomes using an Elo rating system trained on historical match data.

## Features
- Elo-based team strength modeling
- Trained on international match dataset
- Tournament weighting (World Cup, Euros, Copa America)
- Recency weighting for modern performance
- Full World Cup simulation (group stage + knockouts)

## How it works
1. Load historical international match data
2. Update team ratings using Elo formula
3. Simulate tournament using learned strengths
4. Run multiple simulations to estimate win probabilities

## Setup

```bash
pip install pandas python-dotenv
```

## Run

```bash
python main.py
```
## Example Output

```bash
Argentina: 5.4%
France: 4.1%
Brazil: 3.7%
```
