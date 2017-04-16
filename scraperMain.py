from grabbers.communityScraper import scrapDetails as scd
comm_page_url = "https://datascience.stackexchange.com/questions"
scd().returnDetails(scd().getSoup(comm_page_url))