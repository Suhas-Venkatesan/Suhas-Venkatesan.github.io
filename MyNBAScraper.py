import requests
import Constants
from bs4 import BeautifulSoup
import time
import pandas as pd
from requests import get


def get_team_stats(team, season_end_year):
    r = get(
        f'https://widgets.sports-reference.com/wg.fcgi?css=1&site=bbr&url=%2Fleagues%2FNBA_{season_end_year}.html&div=div_per_game-team')
    df = None
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table')
        try:
            df = pd.read_html(str(table))[0]
        except ValueError:
            return pd.DataFrame()
        league_avg_index = df[df['Team'] == 'League Average'].index[0]
        df = df[:league_avg_index]
        df['Team'] = df['Team'].apply(lambda x: x.replace('*', '').upper())
        df['TEAM'] = df['Team'].apply(lambda x: Constants.TEAM_TO_TEAM_ABBR[x])
        df = df.drop(['Rk', 'Team'], axis=1)
        df.loc[:, 'SEASON'] = f'{season_end_year - 1}-{str(season_end_year)[2:]}'
        s = df[df['TEAM'] == team]
        return s


def get_team_misc(team, season_end_year):
    r = get(
        f'https://widgets.sports-reference.com/wg.fcgi?css=1&site=bbr&url=%2Fleagues%2FNBA_{season_end_year}.html&div=div_advanced-team')
    df = None
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table')
        try:
            df = pd.read_html(str(table))[0]
        except ValueError:
            return pd.DataFrame()
        df.columns = list(map(lambda x: x[1], list(df.columns)))
        league_avg_index = df[df['Team'] == 'League Average'].index[0]
        df = df[:league_avg_index]
        df['Team'] = df['Team'].apply(lambda x: x.replace('*', '').upper())
        df['TEAM'] = df['Team'].apply(lambda x: Constants.TEAM_TO_TEAM_ABBR[x])
        df = df.drop(['Rk', 'Team'], axis=1)
        df.rename(columns={'Age': 'AGE', 'Pace': 'PACE', 'Arena': 'ARENA',
                           'Attend.': 'ATTENDANCE', 'Attend./G': 'ATTENDANCE/G'}, inplace=True)
        df.loc[:, 'SEASON'] = f'{season_end_year - 1}-{str(season_end_year)[2:]}'
        s = df[df['TEAM'] == team]
        s = s.loc[:, ~s.columns.str.contains('^Unnamed')]
        return s


def getteamdata():

    teams = ['WAS', 'ATL', 'BRK', 'BOS', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW',
         'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC',
         'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA','SEA', 'SLH', 'TCB',
         'NJN', 'CHA', 'FWP', 'SFW', 'NOK', 'NOH', 'SYR', 'KCK', 'CAP', 'BAL']
    df = pd.DataFrame()

    for team in teams:
            for year in range(1980, 2020):
                teamstats = get_team_stats(team, year)
                teammisc = get_team_misc(team, year)
                if teamstats.empty or teammisc.empty:
                    continue
                new_df = pd.merge(teamstats, teammisc)
                new_df = new_df.loc[:, ~new_df.columns.duplicated()]
                df = df.append(new_df)
    print(df)
    return df


df = getteamdata()
df.to_csv('nbateamdata.csv')