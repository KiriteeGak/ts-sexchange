import urllib2

def getHtmlResponse(url):
	try:
		return urllib2.urlopen(url).read()
	except Exception:
		return None