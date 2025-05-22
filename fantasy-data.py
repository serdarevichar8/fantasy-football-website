from espn_api.football import League

league_id = 565994
espn_s2 = None
swid = None

league = League(league_id=league_id, year=2024, espn_s2=espn_s2, swid=swid)

print(league.members)

scores = league.box_scores(week=1)
scores2 = league.scoreboard(week=1)

