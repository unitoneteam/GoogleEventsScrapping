import os
from dotenv import load_dotenv
from src.ScrapEvents import ScrapEvents

def main():
    Email=os.getenv("EMAIL")
    Password=os.getenv("PASSWORD")
    query="What to do in los angeles today"
    scrapper=ScrapEvents(Email,Password,query)
    events=scrapper.getEventsWithFixedPages(1)
    #events=scrapper.getAllEvents()
    #events=scrapper.getEventsWithFixedPagesOptimized(5)
    #events=scrapper.getAllEventsOptimized(10)
    print("number of scraped events ", len(events))
    scrapper.writeDictToExcelFile(events,"events.csv")
    print("done.")
    
if __name__ == "__main__":
    load_dotenv()
    main()
