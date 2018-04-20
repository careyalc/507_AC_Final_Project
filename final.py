import requests
import json
from bs4 import BeautifulSoup
import sqlite3
import webbrowser
import plotly.plotly as py
import plotly.graph_objs as go
import tweepy
from secrets import *
from caching_func import *

DBNAME = 'umma.sqlite'

CACHE_FNAME = 'artcache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

def get_unique_key(url):
    return url

def make_request_using_cache(url):
    unique_ident = get_unique_key(url)
    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        print("Making a request for new data...")
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

class Art():
    def __init__(self, title, artist, lastname, date, med, dim, url):
        self.title = title
        self.artist = artist
        self.artist_last_name = lastname 
        self.date = date
        self.med = med
        self.dim = dim
        self.url = url

def get_umma_titles(term): #page will be an integer that tells you which page you want to get to 
    baseurl = 'https://exchange.umma.umich.edu/quick_search/query?utf8=%E2%9C%93&q='
    query_url = baseurl + term
    page_text = make_request_using_cache(query_url)
    page_soup = BeautifulSoup(page_text, 'html.parser')

    result = page_soup.find_all(class_ = "text-left qsResultText") #finding all divs for each result

    #find each text attached to the href
    #make those into a list and print them next to a number 
    list_of_art = [] #making a list of all art restuls
    list_of_links = [] 

    for i in range(len(result)):
        titles = result[i].find("a") #add href to get the links!
        list_of_links.append(result[i].find("a")["href"])
        for each in titles:
            list_of_art.append(each) #making a list of all titles!

    return list_of_links

def create_art_db():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        statement = '''
            DROP TABLE IF EXISTS 'Artists';
        '''
        cur.execute(statement)
        conn.commit()
        statement = '''
        CREATE TABLE 'Artists' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'FirstName' TEXT NOT NULL,
            'LastName' TEXT,
            'Nationality' TEXT,
            'ObjectsInCollection' INTEGER
                );
            '''
        cur.execute(statement)
        conn.commit()

        statement = '''
            DROP TABLE IF EXISTS 'Art';
        '''
        cur.execute(statement)
        conn.commit()

        statement = '''
        CREATE TABLE 'Art' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Title' TEXT NOT NULL,
            'Artist' TEXT NOT NULL,
            'ArtistId' INTEGER NOT NULL,
            'ObjectCreationDate' TEXT NOT NULL,
            'Medium' TEXT NOT NULL,
            'Dimensions' TEXT NOT NULL,
            'URL' TEXT NOT NULL,
            FOREIGN KEY('ArtistId') REFERENCES 'Artists(Id)' 
                );
            '''
        cur.execute(statement)
        conn.commit()

        conn.close()
    except:
        print("Sorry, cannot create database")


def crawl_and_populate(link_list):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    artist_tracking = [] #used for making sure no repeate artists are added to the DB
    #SEARCH FOR ART TABLE INFO
    baseurl = 'https://exchange.umma.umich.edu'
    list_of_art_insts = []

    for each_href in link_list:
        each_art_page = baseurl + each_href
        page_text = make_request_using_cache(each_art_page)
        page_soup = BeautifulSoup(page_text, 'html.parser')

        #FINDING TITLE
        art_title = page_soup.find("h2").text
        
        #FINDING ARTIST NAME AND OTHER ARTIST DATA
        try:
            art_artist = page_soup.find('span', class_="co-search co-artist").text #this is the class of the span which includes the artist text
        except:
            artists = page_soup.find_all(class_="col-sm-4 collectionObjectDetailText")
            art_artist = artists[0].find('a').text
            artist_link = artists[0].find('a')['href']

        #split into first and last names for Artist table
        artist_pages = []
        first_last = art_artist.split()
        if len(first_last) == 3:
            first = str(first_last[0] + " " + first_last[1])
            last = first_last[-1]
            artist_url_append = "{}+{}+{}".format(first_last[0], first_last[1], first_last[2])
        elif len(first_last) == 2: 
            first = first_last[0]
            last = first_last[-1]
            artist_url_append = "{}+{}".format(first_last[0], first_last[1])
        else:
            first = first_last[0]
            last = " "
            artist_url_append = first


        #getting the number of objects that an artist has in the UMMA collection
        artist_crawl = 'https://exchange.umma.umich.edu/quick_search/query?utf8=%E2%9C%93&q=' + artist_url_append
        artist_text = make_request_using_cache(artist_crawl)
        artist_soup = BeautifulSoup(artist_text, 'html.parser')
        objects_info= (artist_soup.text).find("UMMA objects (")
        try:
            number = int(artist_soup.text[objects_info+14: objects_info+16])
        except:
            number = int(artist_soup.text[objects_info+14])


        #FINDING THE REST....
        stuff = page_soup.find_all(class_="col-sm-4 collectionObjectDetailText")
        # print(stuff)

        #FINDING DATE
        starting_location = (stuff[0].text).find("Creation Date") # this will return the first index of Creation Date1234
        year = stuff[0].text[starting_location+13: starting_location+17] 
        try:
            try: 
                art_date = int(year) #this is if there is just one year
            except: 
                art_date = int(stuff[0].text[starting_location+19: starting_location+23]) #this is if there is 'circa' in front of the year
        except:
            art_date = stuff[0].text[starting_location+13: starting_location+25] #this is if its xth century


        #FINDING MEDIUM AND DIMENSIONS
        medium_start = (stuff[0].text).find("Medium & Support") #len of Medium & Support is 16
        dimensions_start = (stuff[0].text).find("Dimensions") #len of dimenstions is 10
        credit_start = (stuff[0].text).find("Credit Line")  

        art_med = stuff[0].text[medium_start+16: dimensions_start]
        art_dim = stuff[0].text[dimensions_start+10: credit_start]

        #FINING ARTIST NATIONALITY (IF EXISTS)
        nation_start = (stuff[0].text).find("Artist Nationality") #len of Artist Nationality is 17
        obj = (stuff[0].text).find("Object")
        almost_nat  = stuff[0].text[nation_start+18: obj]
        if len(almost_nat) > 30: #if the page does not have nationality data, a long nonsense string is returned, so that is why I chose to test length
            art_nat = None
        else:
            art_nat = almost_nat

        #POPULATING ARTIST TABLE
        if (first, last) not in artist_tracking:
            insertion = (None, first, last, art_nat, number) 
            statement = 'INSERT INTO "Artists" '
            statement += 'VALUES (?, ?, ?, ?, ?)'
            cur.execute(statement, insertion)

        artist_tracking.append((first, last))

        #create ART class instances for next function
        each_artwork = Art(art_title, art_artist, last, art_date, art_med, art_dim, each_art_page)
        list_of_art_insts.append(each_artwork)

    conn.commit()
    conn.close()

    return list_of_art_insts

def populate_art_table(list_of_art_insts):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    for art in list_of_art_insts:
        statement = "SELECT Artists.Id FROM Artists WHERE LastName LIKE '" + str(art.artist_last_name) + "'"
        cur.execute(statement)
        number = cur.fetchone()[0]

        insertion = (None, art.title, art.artist, number, art.date, art.med, art.dim, art.url) 
        statement = 'INSERT INTO "Art" '
        statement += 'VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)

    conn.commit()
    conn.close()
    
def plot_artists_for_search():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    artists = []
    artworks = []

    statement = "SELECT COUNT(Artist), Artist FROM Art JOIN Artists ON Art.ArtistId = Artists.Id GROUP BY Artists.Id"
    cur.execute(statement)
    infos = cur.fetchall()
    for info in infos:
        artworks.append(info[0])
        artists.append(info[1])

    data = [go.Bar(
            x=artists,
            y=artworks
    )]

    py.plot(data, filename='basic-bar2')
    conn.commit()
    conn.close()

def plot_medium():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    mediums = []
    statement = "SELECT Medium FROM Art"
    cur.execute(statement)
    meds = cur.fetchall()
    for med in meds:
        mediums.append(med[0])
    conn.commit()
    conn.close()

    labels = ['Photography','Painting','Sketch','Woodwork','Pottery', 'Sculpture', 'Fabric', 'Print', 'Other']
    values = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    for each in mediums:
        if "lithograph" in each or "gelatin" in each or "platinum" in each or "albumen" in each or "drypoint" in each or "iris" in each or "photograph" in each:
            values[0] += 1
        elif "aquatint" in each or "oil" in each or "watercolor" in each or "canvas" in each or "acrylic" in each:
            values[1] += 1
        elif "engraving" in each or "ink" in each or "pencil" in each:
            values[2] += 1
        elif "wood" in each or "plywood" in each:
            values[3] += 1
        elif "porcelain" in each or "clay" in each or "glaze" in each:
            values[4] += 1
        elif "marble" in each or "stone" in each or "ceramic" in each:
            values[5] += 1
        elif "silk" in each or "blanket" in each or "cotton" in each:
            values[6] += 1
        elif "mezzotint" in each or "print" in each:
            values[7] += 1
        else:
            values[8] += 1

    trace = go.Pie(labels=labels, values=values)

    py.plot([trace], filename='basic_pie_chart')

def get_tweets(search_term, num_tweets=30):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
    searched_tweets = [status for status in tweepy.Cursor(api.search, q=search_term).items(num_tweets)]
    # print(searched_tweets)
    return searched_tweets

def plot_tweets(searched_tweets):
    lat_vals = []
    lon_vals = []
    text_vals = []

    tweets = []
    for each in searched_tweets:
        tweets.append(str(each.user.location))

    cities = []
    for each in tweets:
        if len(each) < 30:
            if ", " in each:
                new = each.split(", ")
                if len(new[1]) == 2: 
                    cities.append(new[0])

    for each in cities: 
        base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
        params_dict = {}
        params_dict["query"] = each
        params_dict["key"] = "AIzaSyCKWaW6wM0pAj86rA_SWSAYNXLONYCAWeU"
        tweet_data = caching_func(base_url, params_dict)
        if tweet_data["status"] != "ZERO_RESULTS":
            lat_vals.append(tweet_data["results"][0]["geometry"]["location"]["lat"])
            lon_vals.append(tweet_data["results"][0]["geometry"]["location"]["lng"])
            text_vals.append(each)        

    data = [ dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = lon_vals,
        lat = lat_vals,
        text = text_vals,
        mode = 'markers',
        marker = dict(
            size = 8,
            symbol = 'star',
            color = 'red'
        ))]

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
    padding = max_range * .10
    lat_axis = [min_lat - padding, max_lat + padding]
    lon_axis = [min_lon - padding, max_lon + padding]

    layout = dict(
            title = 'Location of U.S. Related Tweets',
            geo = dict(
                scope='usa',
                projection=dict( type='albers usa' ),
                showland = True,
                landcolor = "rgb(250, 250, 250)",
                subunitcolor = "rgb(100, 217, 217)",
                countrycolor = "rgb(217, 100, 217)",
                lataxis = {'range': lat_axis},
                lonaxis = {'range': lon_axis},
                center = {'lat': center_lat, 'lon': center_lon },
                countrywidth = 3,
                subunitwidth = 3
            ),
        )

    fig = dict(data=data, layout=layout )
    py.plot( fig, validate=False, filename='usa - sites' )


def plot_favorites(searched_tweets):
    tweeters = []
    followers = []
    for tweet in searched_tweets:
        user = tweet.user.screen_name
        tweeters.append(user)
        follower_num = tweet.user.followers_count
        followers.append(follower_num)

    data = [go.Bar(
            x=followers,
            y=tweeters,
            orientation = 'h'
    )]

    py.plot(data, filename='basic-bar')


def make_database():
    create_art_db()
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    print("Time to populate your database!")

    response = ''

    flag = True

    while response != 'exit':

        if flag == True:
            response = input("Please enter search terms until databse is ready: ")
            populate_art_table(crawl_and_populate(get_umma_titles(response)))

            statement = 'SELECT COUNT(Id) FROM Art'
            cur.execute(statement)
            check = cur.fetchone()[0]
            if check > 100:
                flag = False
                response = ''
                print("Database has reached 100 rows.")
                return
    conn.commit()
    conn.close()c

def interactive_prompt(response):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    while response != 'exit':

        try:
            if response == "1":
                statement = 'SELECT Id, Title FROM Art'
                cur.execute(statement)
                titles = cur.fetchall()
                for each in titles:
                    print(each[0], each[1])
            
            response = input("For information options about the database as a whole, type 'general'. For information options about a specific work of art, type 'art'. \n")

            if response == "art":

                response = input("Which work of art would you like to know more about? Enter a number, followed by 'info', browser', 'artist', 'tweets', or 'tweeters'. \n")

                try:
                    try:
                        number = int(response[:2]) #if 3 digit number
                    except:
                        number = int(response[:1]) #if 2 digit number
                except:
                    number = int(response[0]) #if 1 digit number

                statement = 'SELECT Title FROM Art WHERE Art.Id = ' + str(number)
                cur.execute(statement)
                art_title = cur.fetchone()[0]

                if "info" in response:
                    statement = 'SELECT Title, Medium, Artist, ObjectCreationDate FROM Art WHERE Art.Id = ' + str(number)
                    cur.execute(statement)
                    art_info = cur.fetchone()
                    print(art_info)
                    print("{} is a {} created by {} in {}. \n".format(art_info[0], art_info[1], art_info[2], art_info[3]))

                elif "browser" in response:
                    statement = 'SELECT URL FROM Art WHERE Id = ' + str(number)
                    cur.execute(statement)
                    open_url = cur.fetchone()[0]
                    webbrowser.open(open_url)

                elif "artist" in response:
                    statement = 'SELECT Artist, Nationality, ObjectsInCollection FROM Artists JOIN Art ON Art.ArtistId = Artists.Id WHERE Art.Id = ' + str(number)
                    cur.execute(statement)
                    artist_info = cur.fetchone()
                    print("{} is a {} artist with {} objects in the UMMA collection. \n".format(artist_info[0], artist_info[1], artist_info[2]))

                elif 'tweet' in response:
                    tweet_search = get_tweets(art_title)

                    if 'tweets' in response:
                        plot_tweets(tweet_search)

                    elif 'tweeter' in response:
                        plot_favorites(tweet_search)

            elif response == "general":

                response = input("For a chart showing the differnt media rerpesented in the database, type 'media'\nFor a chart showing different artists represetend in the database, type 'artists'")

                if response == "media":
                    plot_medium()

                elif response == "artists":
                    plot_artists_for_search()

                else:
                    response = input("Please enter a valid command! ")

        except:
            response = input("Please enter a valid command! ")
    conn.commit()
    conn.close()


if __name__=="__main__":
    make_database()
    interactive_prompt(input("Press 1 for a list of all artwork in the database. "))

