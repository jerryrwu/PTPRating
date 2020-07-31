'''
Possible rating images:
'imdb://image.rating'
'rottentomatoes://image.rating.rotten'
'rottentomatoes://image.rating.ripe'
'rottentomatoes://image.rating.certified'
'rottentomatoes://image.rating.spilled'
'rottentomatoes://image.rating.upright'
'''

import requests
from lxml import html
from lxml.html import fromstring
import re

regex_pattern = re.compile('Average rating: ([0-9]+)%. Votes: ([0-9]+)')

def Start():
    pass

def ValidatePrefs():
    pass

class PTPApi(Agent.Movies):

    # From OMDB bundle
    name = 'PTP Rating'
    languages = [Locale.Language.English]
    primary_provider = False
    contributes_to = [
    'com.plexapp.agents.imdb',
    'com.plexapp.agents.themoviedb'
    ]

    def search(self, results, media, lang):
        if media.primary_agent == 'com.plexapp.agents.imdb':
            imdb_id = media.primary_metadata.id

        elif media.primary_agent == 'com.plexapp.agents.themoviedb':
            # Get the IMDb id from the Movie Database Agent
            imdb_id = Core.messaging.call_external_function(
                'com.plexapp.agents.themoviedb',
                'MessageKit:GetImdbId',
                kwargs = dict(
                tmdb_id = media.primary_metadata.id
                )
            )
            if not imdb_id:
                Log("*** Could not find IMDb id for movie with The Movie Database id: {} ***".format(media.primary_metadata.id))
                return None

        results.Append(MetadataSearchResult(
            id = imdb_id,
            score = 100
        ))
    # End OMDB bundle

    def update(self, metadata, media, lang):
        GetMetadata(metadata, media, metadata.id, type='movie')

def get_omdb_data(imdb_id):
    mt_rating = None
    imdb_rating = None
    rt_rating = None
    plot = None
    if Prefs["omdb_key"] == "":
        Log("no omdb key")
        return dict(mt_rating=mt_rating, imdb_rating=imdb_rating,rt_rating=rt_rating,plot=plot)
    params = dict(i=imdb_id, apikey=Prefs["omdb_key"], plot="full")
    resp = requests.get("http://www.omdbapi.com/",params=params)
    if resp.status_code != 200:
        return dict(mt_rating=mt_rating, imdb_rating=imdb_rating,rt_rating=rt_rating,plot=plot)
    data = resp.json()
    if data["Response"] == "False":
        return dict(mt_rating=mt_rating, imdb_rating=imdb_rating,rt_rating=rt_rating,plot=plot)
    if data["Plot"] != "N/A":
        plot = data["Plot"]
    if data["Ratings"] != "N/A":
        for each in data["Ratings"]:
            if each["Source"] == "Internet Movie Database":
                imdb_rating = float(each["Value"].split("/")[0])
            elif each["Source"] == "Rotten Tomatoes":
                rt_rating = int(each["Value"].split("%")[0])/10.0
            elif each["Source"] == "Metacritic":
                mt_rating = int(each["Value"].split("/")[0])/10.0
    return dict(mt_rating=mt_rating, imdb_rating=imdb_rating,rt_rating=rt_rating,plot=plot)
    


def get_tmdb_id(imdb_id):
    if (Prefs["tmdb_rating"]) == "":
        Log("No TMDB key")


def search_ptp(imdb_id):
    params = dict(action="autocomplete", searchstr=imdb_id)
    headers = dict(cookie=Prefs["session"])
    resp = requests.get("https://passthepopcorn.me/torrents.php", params=params, headers=headers)
    try:
        resp = resp.json()
    except:
        Log("Request error, is website down? Is session cookie valid?")
        return False
    if len(resp[1]) != 1:
        Log("Multiple matches... bad IMDB tag?")
        return False
    Log("search_ptp working...")
    return resp[2][0]

def get_rating_votes(torrent_id):
    headers = dict(cookie=Prefs["session"])
    params = dict(action="ratings", id=torrent_id)
    page = requests.get("https://passthepopcorn.me/torrents.php", headers=headers, params=params)
    match = re.search(regex_pattern, page.text)
    if match == None:
        Log("No votes found/Error")
        return [0,0]
    Log("Votes found")
    rating, votes = match.group(1), match.group(2)
    if len(rating) == 2:
        rating = int(rating)/10.0
    votes = int(votes)
    return [rating, votes]

def GetMetadata(metadata, media, url, type):
    if type != 'movie':
        return

    mt_rating = 0.0
    rt_rating = 0.0
    imdb_rating = 0.0
    ptp_rating = 0.0
    ptp_link = ""
    ptp_votes = 0
    plot = ""
    metadata.summary = None

    omdb_resp = get_omdb_data(url)
    if omdb_resp["mt_rating"] is not None:
        mt_rating = omdb_resp["mt_rating"]
    if omdb_resp["imdb_rating"] is not None:
        imdb_rating = omdb_resp["imdb_rating"]
    if omdb_resp["rt_rating"] is not None:
        rt_rating = omdb_resp["rt_rating"]
    if omdb_resp["plot"] is not None:
        plot = omdb_resp["plot"]

    rating_prefs = [Prefs["audience_rating"],Prefs["personal_rating"],Prefs["critic_rating"]]

    if  "Pass the Popcorn" in [Prefs["audience_rating"],Prefs["personal_rating"],Prefs["critic_rating"]]:
        if Prefs["session"] == "":
            Log("Need session to use site")
            return
        torrent_id = search_ptp(url).split("=")[1]
        ptp_link = "https://passthepopcorn.me/torrents.php?id=" + torrent_id
        ptp_rating, ptp_votes = get_rating_votes(torrent_id)
        metadata.summary = plot
        if Prefs["add_link_ptp"]:
            metadata.summary = ptp_link + "\n" + metadata.summary
        if Prefs["add_rating_ptp_summary"]:
            metadata.summary = "Pass the Popcorn: " + str(ptp_rating) + " (" + str(ptp_votes) + " votes)  " + metadata.summary
    
    if Prefs["critic_rating"] == "IMDb":
        metadata.rating_image = "rottentomatoes://image.rating.certified"
        metadata.rating = imdb_rating
    elif Prefs["critic_rating"] == "Rotten Tomatoes Critic":
        metadata.rating_image = "rottentomatoes://image.rating.ripe"
        metadata.rating = rt_rating
    elif Prefs["critic_rating"] == "Rotten Tomatoes Audience":
        metadata.rating_image = "rottentomatoes://image.rating.ripe"
        metadata.rating = rt_rating
    elif Prefs["critic_rating"] == "Pass the Popcorn":
        metadata.rating_image = "rottentomatoes://image.rating.upright"
        metadata.rating = ptp_rating

    if Prefs["audience_rating"] == "IMDb":
        metadata.audience_rating_image = "rottentomatoes://image.rating.certified"
        metadata.audience_rating = imdb_rating
    elif Prefs["audience_rating"] == "Rotten Tomatoes Critic":
        metadata.audience_rating_image = "rottentomatoes://image.rating.ripe"
        metadata.audience_rating = rt_rating
    elif Prefs["audience_rating"] == "Rotten Tomatoes Audience":
        metadata.audience_rating_image = "rottentomatoes://image.rating.ripe"
        metadata.audience_rating = rt_rating
    elif Prefs["audience_rating"] == "Pass the Popcorn":
        metadata.audience_rating_image = "rottentomatoes://image.rating.upright"
        metadata.audience_rating = ptp_rating
    else:
        metadata.audience_rating = 0.0
        metadata.audience_rating_image = None

    
