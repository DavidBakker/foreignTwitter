# TwitterForeignWordUsage
WHAT:
Crawls tweets in a country and language you specify, creates a wordcount and ranks by usage, then auto-translates the words using Google Translation API and returns a Pandas dataframe. exportTSV() Method allows you to export a .tsv for upload to ANKI flash card software, and save_words() inserts into a database.

WHY:
I created this because I traveled in South America for a while and was cramming to learn enough Spanish to survive. Meanwhile, Duolingo kept feeding me words I rarely saw again. Thinking back to that time, I wanted to try and create a tool that pulled words that were not only actually used in a given language conversationally, but that would allow me to target a specific country that spoke that language as local vocabulary/slang can shift a bunch. I.e. France vs Senegal, Spain vs Colombia, Olde Jersey vs New Jersey, yada yada.

NOTE ON SERVICE AUTHENTICATION: 
All of my secrets are stored in a git-ignored settings.py file, so anywhere you see settings.*whatever* you'll need to provide new creds there. 
-For the Twitter crawl fetch_tweets() method: you'll need to sign up for a Twitter dev account.
-For the auto translation translate_words() method: you'll need to sign up for Google Translate's API (some costs apply). The method pulls from an OS environment variable fed from the Google cred JSON file I got from them.
-For the save to database save_words() method: you'll need a MySQL DB set up and the appropriate user permissions and credentials.

LICENSE INFO:
I'm saving this under generic MIT license, so read my license.txt if you're not familiar and then treat my code like it was a lego set that owed you money.

BACKLOG/OPTIMIZATION:
-Refactor to req/pull console inputs for country and language, instead of hard-coding (mostly running in iPython/Jupyter, but could be handy).
-Implement open source translation library to reduce cost.
-Implement chunking and threading to speed up translation batches.
-Vectorize dataframe insert iterations, technically for loop/iterrow is an anti-pattern.
-Potentially remove intermediate list a couple steps, potentially replace in-memory lists with generators.
-Improve transparency with progress bar and @timer decorator.
-Update string %s syntax with f'' string substitution for easier readability. 
-Include DB columns list into insert query now that I'm using a DB SPROC to update/dedup instead of Python code.
-Further normalize DB table(s) for multi-language support.
