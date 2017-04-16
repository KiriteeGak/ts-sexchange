from bs4 import BeautifulSoup
import urllib2, re
from bs4.element import Tag

def getHtmlResponse(url):
	try:
		return urllib2.urlopen(url).read()
	except Exception:
		return None

def getSoup(comm_page_url):
	resp = getHtmlResponse(comm_page_url)
	if resp != None:
		soup = BeautifulSoup(resp,'html.parser')
		return soup.find_all('div',{"class":"question-summary"})
	return None

def cleanText(text, space_status = True):
	if space_status:
		return re.sub(r'\n|\r|/.| |\$','',text)
	return re.sub(r'\n|\r|/.| {2,}|\$','',text)

def returnDetails(single_page_element):
	# for ques in single_page_element:
	# 	print ques,"\n\n\n"
	return [{"tags": getTags(ques),
		"question_summary" : cleanText(getQuestionSummary(ques), space_status = False),
		"question" : cleanText(getUserQuestionDetailed(ques), space_status = False),
		"votes" : cleanText(getVotes(ques)),
		"views" : cleanText(getViews(ques)),
		"no_of_answers" : cleanText(getAnswers(ques)[0]),
		"answered_status" : getAnswers(ques)[1],
		"poster" : getOP(ques),
		"time_of_posting" : getPostTime(ques),
		"user_details" : getOpsReputationAndBadges(ques)
		} for ques in single_page_element]

def getTags(ques_sum_element):
	return [tag_element.text for tag_element in ques_sum_element.find_all('a',{'class':'post-tag'})]

def getQuestionSummary(ques_sum_element):
	return ques_sum_element.find_all('a',{"class":"question-hyperlink"})[0].text

def getUserQuestionDetailed(ques_sum_element):
	return ques_sum_element.find_all('div',{"class":"excerpt"})[0].text

def getVotes(ques_sum_element):
	return ques_sum_element.find_all('span',{"class":"vote-count-post"})[0].text

def getViews(ques_sum_element):
	return ques_sum_element.find_all('div',{"class":"views"})[0].text.replace(' views','')

def getStatusAnswered(ques_sum_element):
	try: return ques_sum_element.find_all('div',{"class":"status answered"})[0].text
	except IndexError: return None

def getStatusUnanswered(ques_sum_element):
	try: return ques_sum_element.find_all('div',{"class":"status unanswered"})[0].text
	except IndexError: return None	

def getStatusAnsweredAccepted(ques_sum_element):
	try: return ques_sum_element.find_all('div',{"class":"status answered-accepted"})[0].text
	except IndexError: return None

def getOP(ques_sum_element):
	return ques_sum_element.find_all('div',{"class":"user-details"})[0].a.text

def getPostTime(ques_sum_element):
	return ques_sum_element.find_all('span',{"class":"relativetime"})[0].get('title')

def getOpsReputationAndBadges(ques_sum_element):
	raw_res = [e.text if e.get('title') == 'reputation score ' else e.find('span',{'class':'badgecount'}) for e in ques_sum_element.find_all('div',{"class":"-flair"})[0].find_all('span')]
	return [e.text if isinstance(e,Tag) else e for e in raw_res]

def getAnswers(ques_sum_element):
	if not getStatusAnswered(ques_sum_element) == None:
		return [getStatusAnswered(ques_sum_element).replace('answers',''), 'answered']
	elif not getStatusUnanswered(ques_sum_element) == None:
		return [getStatusUnanswered(ques_sum_element).replace('answers',''), 'unanswered']
	else:
		if not getStatusAnsweredAccepted(ques_sum_element) == None:
			return [getStatusAnsweredAccepted(ques_sum_element).replace('answers',''),'answered and accepted']
	return None

if __name__ == '__main__':
	comm_page_url = "https://datascience.stackexchange.com/questions"
	soup = getSoup(comm_page_url)
	print returnDetails(soup)