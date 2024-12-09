# %%
from balldontlie import BalldontlieAPI
import os

ball_api = BalldontlieAPI(api_key=os.getenv("BALL_DONT_LIE_API_KEY"))


valid_players = []

response = ball_api.nba.players.list(cursor=0, per_page=100)
players = response.data
next_cursor = response.meta.next_cursor

for player in players:
    id = player.id
