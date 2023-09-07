import os
from dotenv import load_dotenv
from src.ScrapEvents import ScrapEvents

def main():
    Email=os.getenv("EMAIL")
    Password=os.getenv("PASSWORD")
    query="What to do in los angeles today"
    scrapper=ScrapEvents(Email,Password,query)
    # events=scrapper.get_events_with_fixed_pages(1)
    # events=scrapper.get_all_events()
    # events=scrapper.get_events_with_fixed_pages_optimized(5)
    events=scrapper.getAllEventsOptimized(10)
    print("number of scraped events ", len(events))
    scrapper.writeDictToExcelFile(events,"events.xlsx")
    print("done.")
    
if __name__ == "__main__":
    load_dotenv()
    main()
