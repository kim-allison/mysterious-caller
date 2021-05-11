from textblob import TextBlob

'''
run pip install textblob
run python -m textblob.download_corpora
'''

# wiki = TextBlob("Python is a high-level, general-purpose programming language.")
# print("Tags: ", wiki.tags)
# print("Noun Phrases: ", wiki.noun_phrases)

# sentiment analysis
# testimonial = TextBlob("Textblob is amazingly simple to use. What great fun!")
# print("Sentiment: ", testimonial.sentiment)
# print("Polarity: ", testimonial.sentiment.polarity)

testimonial1 = TextBlob("USA is an country.")
print("Sentiment: ", testimonial1.sentiment.subjectivity)

testimonial2 = TextBlob("Carleton College is located in Northfield, Minnesota.")
print("Sentiment: ", testimonial2.sentiment.subjectivity)

testimonial3 = TextBlob("I hate Carleton College!")
print("Sentiment: ", testimonial3.sentiment.subjectivity)
# print("Sentiment: ", testimonial3.sentiment)
