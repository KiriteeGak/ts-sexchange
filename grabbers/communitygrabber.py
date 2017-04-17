from bs4 import BeautifulSoup
import re
from bs4.element import Tag
from utilities.utilities import *

class scrapDetails(object):
	def getSoup(self, comm_page_url):
		resp = getHtmlResponse(comm_page_url)
		if resp != None:
			soup = BeautifulSoup(resp,'html.parser')
			return soup.find_all('div',{"class":"question-summary"})
		return None

	def cleanText(self, text, space_status = True):
		if space_status:
			return re.sub(r'\n|\r|/.| |\$','',text)
		return re.sub(r'\n|\r|/.| {2,}|\$','',text)

	def modifyNumbers(self, number):
		return number if len(set(['k','m']).intersection(list(str(number)))) == 0 else self.helperModNumber(number)

	def helperModNumber(self, number, ref_dict = {'k':'000','m':'000000'}):
		ret = ''
		for e in list(number):
			if e.lower() in ref_dict: ret += ref_dict[e.lower()]
			else: ret += e
		return ret

	def returnDetails(self, single_page_element):
		return [{"_id" : self.getId(ques), 
			"tags": self.getTags(ques),
			"question_summary" : self.cleanText(self.getQuestionSummary(ques), space_status = False),
			"question" : self.cleanText(self.getUserQuestionDetailed(ques), space_status = False),
			"votes" : int(self.cleanText(self.modifyNumbers(self.getVotes(ques)))),
			"views" : int(self.cleanText(self.modifyNumbers(re.sub(r'vie(w|ws)','',self.getViews(ques))))),
			"no_of_answers" : self.modifyNumbers(self.cleanText(self.getAnswers(ques)[0])),
			"answered_status" : self.getAnswers(ques)[1],
			"poster" : self.getOP(ques),
			"time_of_posting" : self.getPostTime(ques),
			"user_details" : self.getOpsReputationAndBadges(ques, ['bronze','silver','gold'])
			} for ques in single_page_element]

	def getTags(self, ques_sum_element):
		return [tag_element.text for tag_element in ques_sum_element.find_all('a',{'class':'post-tag'})]

	def getQuestionSummary(self, ques_sum_element):
		return ques_sum_element.find_all('a',{"class":"question-hyperlink"})[0].text

	def getUserQuestionDetailed(self, ques_sum_element):
		return ques_sum_element.find_all('div',{"class":"excerpt"})[0].text

	def getVotes(self, ques_sum_element):
		return ques_sum_element.find_all('span',{"class":"vote-count-post"})[0].text

	def getViews(self, ques_sum_element):
		return ques_sum_element.find_all('div',{"class":"views"})[0].text.replace(' views','')

	def getStatusAnswered(self, ques_sum_element):
		try: return ques_sum_element.find_all('div',{"class":"status answered"})[0].text
		except IndexError: return None

	def getStatusUnanswered(self, ques_sum_element):
		try: return ques_sum_element.find_all('div',{"class":"status unanswered"})[0].text
		except IndexError: return None	

	def getStatusAnsweredAccepted(self, ques_sum_element):
		return ques_sum_element.find_all('div',{"class":"status answered-accepted"})[0].text
		
	def getOP(self, ques_sum_element):
		try: return ques_sum_element.find_all('div',{"class":"user-details"})[0].a.text
		except AttributeError: return None 

	def getPostTime(self, ques_sum_element):
		try: return ques_sum_element.find_all('span',{"class":"relativetime"})[0].get('title')
		except IndexError: return None

	def getOpsReputationAndBadges(self, ques_sum_element, badges):
		try: badge_counts = { str(e.get('title').split(' ')[1]) : int(e.get('title').split(' ')[0]) for e in ques_sum_element.find_all('div',{"class":"-flair"})[0].find_all('span') if 'badge' in str(e.get('title'))}
		except IndexError:
			badge_counts = {}
			pass
		for badge in badges:
			if badge not in badge_counts:
				badge_counts[badge] = 0
		try:
			badge_counts['reputation_score'] = int(self.modifyNumbers(ques_sum_element.find_all('span',{"title":"reputation score "})[0].text.replace(',','')))
		except IndexError:
			badge_counts['reputation_score'] = 0
			pass
		return badge_counts

	def getAnswers(self, ques_sum_element):
		if not self.getStatusAnswered(ques_sum_element) == None:
			return [self.getStatusAnswered(ques_sum_element).replace('answers',''), 'answered']
		elif not self.getStatusUnanswered(ques_sum_element) == None:
			return [self.getStatusUnanswered(ques_sum_element).replace('answers',''), 'unanswered']
		else:
			if not self.getStatusAnsweredAccepted(ques_sum_element) == None:
				return [self.getStatusAnsweredAccepted(ques_sum_element).replace('answers',''),'answered and accepted']
		return None

	def getId(self, ques_sum_element):
		return ques_sum_element.find_all('a',{"class":"question-hyperlink"})[0]['href'].split("/")[2]