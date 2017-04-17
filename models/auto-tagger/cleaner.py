from nltk.corpus import stopwords
import nltk, string, re
from nltk.stem.porter import *

exclude = set(string.punctuation)
stemmer = PorterStemmer()

def removeStopWords(text):
	return " ".join([word.strip() for word in text.split(' ') if word.strip() not in set(stopwords.words('english'))])

def removePunctuations(text, customlist = []):
	if not customlist:
		customlist = exclude
	for punc in customlist:
		text = text.replace(punc,"")
	return text

def removeNumbers(text):
	return re.sub(r'\d','',text)

def cleaner(text):
	text = removePunctuations(text)
	text = removeStopWords(text)
	text = re.sub(r' {2,}',' ',text)
	text = removeNumbers(text)
	# stemmer creates noise, uncomment at risk
	# text = " ".join(stemmer.stem(word) for word in text.split(' '))
	return text