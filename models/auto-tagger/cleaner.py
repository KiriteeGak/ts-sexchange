from nltk.corpus import stopwords
import nltk, string, re
from nltk.stem.porter import *
from nltk.stem import WordNetLemmatizer

exclude = set(string.punctuation)
stemmer = PorterStemmer()
wordnet_lemmatizer = WordNetLemmatizer()

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

def removeSmallWords(text, min_len = 3):
	return " ".join([word.lower() for word in text.split(' ') if len(word) > min_len])

def removeLargeWords(text, min_len = 12):
	return " ".join([word.lower() for word in text.split(' ') if len(word) < min_len])

def cleaner(text):
	text = removePunctuations(text)
	text = removeStopWords(text)
	text = re.sub(r' {2,}',' ',text)
	text = removeNumbers(text)
	text = removeSmallWords(text)
	text = removeLargeWords(text)
	text = " ".join(wordnet_lemmatizer.lemmatize(word) for word in text.split(' '))
	text = " ".join(stemmer.stem(word) for word in text.split(' '))
	return text