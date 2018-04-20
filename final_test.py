import unittest
from final import *


class TestCrawling(unittest.TestCase):

	def test_umma_crawl(self):
		try:
			get_umma_titles("apple")
			get_umma_titles("dinner")
			get_umma_titles("mandolin")
		except:
			self.fail()

	def test_result_crawl(self):
		output = get_umma_titles("apple")
		for each in output:
			self.assertIn('resources', each)
			self.assertIn('view', each)


class TestDatabase(unittest.TestCase):

    def test_art_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        statement = 'SELECT Title FROM Art'
        results = cur.execute(statement)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 102)
        self.assertEqual(result_list[1], ('Apples ',))
        conn.commit()
        conn.close()

    def test_artist_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        statement = 'SELECT LastName FROM Artists'
        results = cur.execute(statement)
        result_list = results.fetchall()
        self.assertIn(('Freckelton',), result_list)
        self.assertIn(('Ebert',), result_list)
        self.assertEqual(len(result_list), 92)
        self.assertEqual(result_list[1], ('Sears',))
        conn.commit()
        conn.close()

    def test_joins(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        statement = "SELECT Title FROM Art JOIN Artists ON Art.ArtistId = Artists.Id WHERE LastName = 'Raimondi' "
        results = cur.execute(statement)
        result = results.fetchone()
        self.assertEqual(('Serpent Speaking to a Young Man ',), result)

        statement = "SELECT ObjectCreationDate FROM Art JOIN Artists ON Art.ArtistId = Artists.Id WHERE FirstName = 'Man' "
        results = cur.execute(statement)
        result = results.fetchone()
        self.assertEqual(('1972',), result)

        statement = "SELECT ObjectsInCollection FROM Artists JOIN Art ON Art.ArtistId = Artists.Id WHERE LastName = 'Picasso' "
        results = cur.execute(statement)
        result = results.fetchone()
        self.assertEqual((80,), result)
        conn.commit()
        conn.close()

class TestClass(unittest.TestCase):

	def test_constructor(self):
		picasso = Art("The Bull Fight", "Pablo Picasso", "Picasso", "1934", "oil on canvas", "17 3/8 in. x 22 11/16 in. x 1 15/16 in. ", "https://exchange.umma.umich.edu/resources/12175/view")
		self.assertEqual(picasso.artist_last_name, "Picasso")
		self.assertEqual(picasso.title, "The Bull Fight")
		self.assertEqual(picasso.med, "oil on canvas")
		self.assertEqual(picasso.url, "https://exchange.umma.umich.edu/resources/12175/view")

		mann = Art("Larry's Kiss", "Sally Mann", "Mann", "1992", "gelatin silver print on paper", "8 in x 10 in", "https://exchange.umma.umich.edu/resources/9174/view")
		self.assertEqual(mann.artist, "Sally Mann")
		self.assertEqual(mann.title, "Larry's Kiss")
		self.assertEqual(mann.date, "1992")
		self.assertEqual(mann.dim, "8 in x 10 in")


class TestGetTweets(unittest.TestCase):

    def test_tweets(self):
        tweets = get_tweets("building", 5)
        self.assertEqual(len(tweets), 5)
        for each in tweets:
            self.assertEqual(type(each.user.followers_count), int)


class TestPlotting(unittest.TestCase):

    # can't test to see if the maps are correct, but can test that the functions don't return an error
    def test_bar_chart(self):
        try:
            plot_artists_for_search()
        except:
            self.fail()

    def test_pie_chart(self):
        try:
            plot_medium()
        except:
            self.fail()

    def test_map(self):
        try:
            plot_tweets(get_tweets("Still Life with Apple"))
        except:
            self.fail()

    def test_fav(self):
        try:
            plot_tweets(get_tweets("Still Life with Apple"))
        except:
            self.fail()


if __name__ == '__main__':
    unittest.main()