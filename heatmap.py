import requests
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# downloads data sets from the FPL website. There are 3 options (maybe more):
#  1. "teams" --> download a data frame of each team in the PL
#  2. "elements" --> download core FPL data set
#  3. "element_types" --> download the meta df for elements
def downloadFplData(dataType):
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    r = requests.get(url)
    json = r.json()    

    df = pd.DataFrame(json[dataType])
    return df


# Function which downloads the fixture list from the PL website, creates a data frame
# containing features for creating the fixture difficulty matrix
def downloadFixtures():
    fixture_url = 'https://fantasy.premierleague.com/api/fixtures/'
    r = requests.get(fixture_url)
    json = r.json()
    
    fixtures = pd.DataFrame(json)

    teams_df = downloadFplData("teams")
    
    fixtures['home_team'] = fixtures.team_h.map(teams_df.set_index('id').name)
    fixtures['away_team'] = fixtures.team_a.map(teams_df.set_index('id').name)
    
    fixtures_df = pd.DataFrame()
    fixtures_df['team'] = pd.concat([fixtures['home_team'],fixtures['away_team']])
    fixtures_df['difficulty'] = pd.concat([fixtures['team_h_difficulty'], fixtures['team_a_difficulty']])
    fixtures_df['time'] = pd.concat([fixtures['kickoff_time'], fixtures['kickoff_time']])
    fixtures_df = fixtures_df.sort_values(by=["team", "time"], ascending = True)
    fixtures_df['gameweek'] = [i for i in range(1,39)] * 20
    return fixtures_df

def getFixtureHeatmap(gameweek, nweeks):
    fixtures_df = downloadFixtures()
    df = fixtures_df[(fixtures_df['gameweek']<gameweek+nweeks) & (fixtures_df['gameweek'] >= gameweek)]
    df = df.pivot(index = 'team', columns='gameweek', values='difficulty')
    return df


# Create a heatmap of fixture difficulty by team name for a given gameweek + number of weeks to look forward
def plotFixtureHeatmap(gameweek, nweeks):
    sns.set(rc={'figure.figsize':(11.7,8.27)})

    df = getFixtureHeatmap(gameweek, nweeks)

    value_to_int = {j:i for i,j in enumerate(pd.unique(df.values.ravel()))} # like you did
    n = len(value_to_int) 

    colors = ["#40572a", "#01fc7a", "#e7e7e7", "#ff1751", "#80072d"]
    colors = colors[-n:]
    diverging_colors = sns.color_palette(colors, n_colors=n, desat=0.8)

    sns.heatmap(df, cmap=diverging_colors, annot=True, cbar=False)
    plt.show()

# This function downloads fixture data, filters out historical matches and then creates a "difficulty matrix"
# The difficulty matrix (DM) compares each team's fixture difficulty rating with all other teams for each GW.
# We can then average this over N gameweeks and pick out teams with large 'difficulty deltas' i.e. teams whose
# fixture difficulties complement each other
def calculateDifficultyMatrix():
    import heatmap as hm
    import time
    from datetime import datetime

    fixtures = hm.downloadFixtures()
    df = fixtures[fixtures['time'] > str(datetime.fromtimestamp(time.time()))].reset_index()
    r = []
    for i in range(0, len(df)):
        diff = df['difficulty'][i]
        data = df[df['gameweek'] == df['gameweek'][i]][['team','gameweek','difficulty']]
        data['difficulty'] = data['difficulty'] - diff
        r.append(data)

    df['difficulty_matrix'] = r
    return df

# This function uses the difficulty matrices calculated above and filters based on a given team and number of gameweeks.
# It returns the top 3 teams with 'complementary' fixtures i.e. teams playing easy fixtures when given team has a difficult one
# and vice versa. We can use this to filter the heatmap we display
def getComplementaryTeams(team, gameweeks_from_current=5):
    df = calculateDifficultyMatrix()
    gw = df[df['team'] == team]['gameweek'].iloc[0] + gameweeks_from_current
    res = df[(df['gameweek'] < gw) & (df['team'] == team)]['difficulty_matrix']

    difficulty_matrix = pd.DataFrame()
    for i in range(0,len(res)):
        difficulty_matrix = pd.concat([difficulty_matrix,res.iloc[i]])

    return difficulty_matrix.groupby("team").mean().sort_values("difficulty", ascending=False).head(3)
