from espn_api.football import League

league_id = 565994
espn_s2 = 'AECM5wfhjIj%2FgFWK7gldFYleiro5zx5YQV0NKDgcd1glbVuvTot8VFFUNWhPjAOG46Ut0lFYEI5mo75eeL5VDdQMyLKmpms7TetGiz2dMsUSIfl2A7MNQMrSMFvmBHhg0wi1SQbHOFKI6FBVsJqtBlq5c%2B%2Bl5dGvpM8LmhrFp563Dv4eaZhclj9lfSPq3CC4u%2FsUk7iSzQq42W7AUMVbYJqAKKX11dazM5GmocQozc9GXNKiRIhuNDAe2en7%2FjyAbJqSZEwlWu%2BRyOIyOpmLgr6wnx47jWxeKJmTIYP24Hk13Q%3D%3D'
swid = '{1B555C10-31F2-4EC7-A015-90782392E593}'

league = League(league_id=league_id, year=2024, espn_s2=espn_s2, swid=swid)

print(league.members)

scores = league.box_scores(week=1)
scores2 = league.scoreboard(week=1)

