# 507_Final_Project README

## Data Sources Used:
1. The UMMA Exchange: https://exchange.umma.umich.edu/   (data accessed via scraping and crawling)
2. Twitter  (data accessed via Tweepy NOTE: for this source, a consumer key, consumer secret, access token, and access secret are needed. I have included mine in my secrets.py file in my .gitignore)

## Database Notes/User Guide:
Due to the nature of the way The UMMA Exchange is built, in order to get to 100 rows minimum in the database, the user is prompted to search for different terms until the "Art" table has reached 100 rows. Additionally, it is recommended to start running the code with no database created for best results. 
Once this is achieved, the user can enter a number of different commands (as instructed) and get different information about either the general database (such as graphs that illustrate the different artists or media represented) or a specific object, accessed by its Id and a given keyword. (Please note the <# Tweets> command can be sensitive, I recommend using the Id corresponding with the object titled "(Buildings)" for a pretty result. =] Everything else, test away!

## Structure of Code:
I start by importing necessary modules and creating the cache function for the UMMA information. (Note there is a seperate caching function in a separate document that needed for the Tweepy calls later in the program). Then I define my class Art that I use later to populate the Art table in the database. Then I create the database with the tables “Art” and “Artist”, connected by the foreign key, “ArtistId” in the Art table. 
My next function, crawl_and_populate, crawls to different pages of The UMMA Exchange and scrapes for the information I need for both tables. This achieves the challenge score of 8. Next, I populate the “Art” table using instances of the class Art. 

Then, I define my data visualization functions using Plotly. First is a bar graph representing all of the different artists that are included in the database. Next is a pie chart representing the percentages of different media (material an object is made of) in the database. Then, using the Tweepy function from Homework 10, I define (based largely off of the code from Project 2) a function that maps the location of related tweets to a given work of art. (Note, due to the “messy” nature of the location information on Twitter, I strip the location to just the name of a city in the United States. Finally, I define a function that plots all of the usernames that have tweeted about a given work of art (or something related to it) and their number of followers in a horizontal bar graph. 

Finally I create two functions that aide in the interactivity of the program, first one that populates the database with search terms (the words “apple”, “orange”, “lemon”, “chocolate”, “mandolin”, “dinner”, “bicycle”, “flower”, “gown”, “building”, and “family” are already cached) and the second that processed the various commands a user may enter by using SELECT statements or invoking previously defined functions. 
