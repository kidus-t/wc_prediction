import requests 
import math
import random
from itertools import combinations
import os
from dotenv import load_dotenv

load_dotenv()


groups = {
    "A": ["Mexico", "South Africa", "South Korea", "Czechia"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["USA", "Paraguay", "Australia", "Türkiye"],
    "E": ["Germany", "Curaçao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cabo Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"]
}


def get_fixtures(league_id, season):
  url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={season}"

  headers = {
      'x-apisports-key': os.getenv("API_SPORTS_KEY")
      }

  response = requests.get(url, headers=headers)
  data = response.json()

  return data["response"]

def build_matches(fixtures):
    matches = []

    for match in fixtures:
        match_data = {
            "Date": match["fixture"]["date"],
            "Home Team": match["teams"]["home"]["name"],
            "Away Team": match["teams"]["away"]["name"],
            "Home Goals": match["goals"]["home"],
            "Away Goals": match["goals"]["away"]
        }

        matches.append(match_data)

    matches.sort(key=lambda x: x["Date"])
    return matches
    
def expected_score(rating_a, rating_b):
  return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def get_actual_score(home_goals, away_goals):
  if home_goals > away_goals: 
    return 1, 0
  elif home_goals < away_goals:
    return 0, 1
  else:
    return 0.5, 0.5

def predict_match_elo(team_a, team_b, ratings):
  if team_a not in ratings:
      ratings[team_a] = 1500

  if team_b not in ratings:
      ratings[team_b] = 1500

  ra = ratings[team_a]
  rb = ratings[team_b]

  pa = expected_score(ra, rb)
  pb = 1 - pa

  return {
      team_a: round(pa, 2),
      team_b: round(pb, 2)
  }

def generate_scoreline(team_a, team_b, ratings):
  if team_a not in ratings:
    ratings[team_a] = 1500

  if team_b not in ratings:
    ratings[team_b] = 1500

  ra = ratings[team_a]
  rb = ratings[team_b]

  elo_diff = ra - rb

  expected_goals_a = max(0.2, 1.35 + elo_diff / 400)
  expected_goals_b = max(0.2, 1.35 - elo_diff / 400)

  goals_a = min(8, round(random.gauss(expected_goals_a, 1.1)))
  goals_b = min(8, round(random.gauss(expected_goals_b, 1.1)))

  goals_a = max(0, goals_a)
  goals_b = max(0, goals_b)

  return goals_a, goals_b

def simulate_match(team_a, team_b, ratings, allow_draws=False):
  if team_a not in ratings:
    ratings[team_a] = 1500

  if team_b not in ratings:
    ratings[team_b] = 1500

  ra = ratings[team_a]
  rb = ratings[team_b]

  p_a = expected_score(ra, rb)

  if allow_draws:
    draw_prob = 0.25
    win_prob_a = p_a * (1 - draw_prob)

    r = random.random()

    if r < win_prob_a:
      return team_a
    elif r < win_prob_a + draw_prob:
      return "DRAW"
    else:
      return team_b

  r = random.random()

  if r < p_a:
      return team_a
  else:
      return team_b

def simulate_group(group_teams, ratings):
  standings = {
      team: {
          "Points": 0,
          "GF": 0,
          "GA": 0,
          "GD": 0
      }
      for team in group_teams
  }

  for a, b in combinations(group_teams, 2):
    goals_a, goals_b = generate_scoreline(a, b, ratings)

    if goals_a > goals_b:
      standings[a]["Points"] += 3
    elif goals_b > goals_a:
      standings[b]["Points"] += 3
    else:
      standings[a]["Points"] += 1
      standings[b]["Points"] += 1

    standings[a]["GF"] += goals_a
    standings[a]["GA"] += goals_b
    standings[a]["GD"] = standings[a]["GF"] - standings[a]["GA"]

    standings[b]["GF"] += goals_b
    standings[b]["GA"] += goals_a
    standings[b]["GD"] = standings[b]["GF"] - standings[b]["GA"]

  ranked = sorted(
      standings.items(),
      key=lambda x: (
          x[1]["Points"],
          x[1]["GD"],
          x[1]["GF"]
      ),
      reverse=True
  )

  return ranked

def simulate_group_stage(ratings):
  advancing = []
  third_place = []

  for group in groups.values():
      ranked = simulate_group(group, ratings)

      advancing.append(ranked[0][0])
      advancing.append(ranked[1][0])

      third_place.append(
          (ranked[2][0], ranked[2][1])
      )

  third_place.sort(
      key=lambda x: (
          x[1]["Points"],
          x[1]["GD"],
          x[1]["GF"]
      ),
      reverse=True
  )

  best_third = [team for team, stats in third_place[:8]]

  advancing.extend(best_third)

  return advancing

def simulate_knockout(teams, ratings):
  round_teams = teams

  while len(round_teams) > 1:

    next_round = []

    for i in range(0, len(round_teams), 2):

      a = round_teams[i]
      b = round_teams[i + 1]

      goals_a, goals_b = generate_scoreline(a, b, ratings)

      if goals_a > goals_b:
        winner = a
      elif goals_b > goals_a:
        winner = b
      else:
        # Extra time
        et_a = random.randint(0, 1)
        et_b = random.randint(0, 1)

        goals_a += et_a
        goals_b += et_b

        if goals_a > goals_b:
          winner = a
        elif goals_b > goals_a:
          winner = b
        else:
          # Penalties
          winner = random.choice([a, b])

      next_round.append(winner)

    round_teams = next_round

  return round_teams[0]

def simulate_world_cup(ratings):

  group_winners = simulate_group_stage(ratings)

  winner = simulate_knockout(group_winners, ratings)

  return winner

fixtures = get_fixtures(1, 2022)

matches = build_matches(fixtures)

ratings = {}

results = {}

K = 30

matches.sort(key=lambda x: x["Date"])

for match in matches:

  home_team = match.get("Home Team")
  away_team = match.get("Away Team")

  home_goals = match.get("Home Goals")
  away_goals = match.get("Away Goals")

  if not home_team or not away_team:
      continue

  ratings.setdefault(home_team, 1500)
  ratings.setdefault(away_team, 1500)

  exp_home = expected_score(ratings[home_team], ratings[away_team])
  exp_away = expected_score(ratings[away_team], ratings[home_team])

  act_home, act_away = get_actual_score(home_goals, away_goals)

  ratings[home_team] += K * (act_home - exp_home)
  ratings[away_team] += K * (act_away - exp_away)

for i in range(10000):
  winner = simulate_world_cup(ratings)

  results[winner] = results.get(winner, 0) + 1

sorted_results = sorted(
    results.items(),
    key=lambda x: x[1],
    reverse=True
)

for team, wins in sorted_results:
    print(f"{team}: {wins / 10000:.2%}")
