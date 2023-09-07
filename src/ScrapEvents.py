import requests
from bs4 import BeautifulSoup
import pandas as pd
from .GoogleLogin import Google 
import pickle
import time
import threading
class ScrapEvents():
    def __init__(self,Email,Password,Query):
        self.Email=Email
        self.Password=Password
        self.cookies=[]
        self.Query="+".join(Query.split())
        self.checkCookies()
        self.cookiesString = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in self.cookies])

    # this function checks if Cookies.dump exist and validate the cookies time and if file not exist 
    # it generate new cookies by login with google account and stors that cookies in Cookies.dump 
    def checkCookies(self):
        try:
            with open('Cookies.dump', 'rb') as fp:
                data = pickle.load(fp)
                curr_time = time.time()
                if(len(data)<3):
                    raise Exception("invalid cookies")
                for cookie in data:
                    if(curr_time-cookie["expiry"]>=0):
                        raise Exception("cookie expired")
                self.cookies=data
        except Exception as e:
            print(e)
            print("generaitng new cookies")
            google = Google()
            google.login(self.Email, self.Password)
            self.cookies=google.getcookies()
            with open('Cookies.dump', 'wb') as fp:
                pickle.dump(self.cookies, fp)
            print("cookies generated successfully")

    # this fetch the html results based on the query and the offset
    def __fetch(self,query,offset):
        URL = "https://www.google.com/search?ei=ywf2ZK-aEMqA9u8PiMGp8AY&opi=89978449&rciv=evn&yv=3&nfpr=0&q="+query+"&start="+offset+"&asearch=evn_af&cs=0&async=_id:Q5Vznb,_pms:hts,_fmt:pc"
        headers={
                "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                "Cookie":self.cookiesString
                }
        page = requests.get(URL,headers=headers)
        return page.text
    
    # this functuon scrap all events elements form the provided html text and return a list of event elements
    def __scrapEventsFromHtml(self,html):
        soup = BeautifulSoup(html, "html.parser")
        events =soup.find_all(class_=["PaEvOc tv5olb wbTnP gws-horizon-textlists__li-ed","PaEvOc tv5olb gws-horizon-textlists__li-ed"])
        return events

    # this functuon scrap all info from provided event element and return a list of events
    def __extractEventData(self,events):
        result=[]
        for event in events:
            eventInf=event.find(class_="PaEvOc gws-horizon-textlists__tl-lif")
            if(eventInf):
                day=eventInf.find(class_="UIaQzd")
                if(day):
                    day=day.text
                month=eventInf.find(class_="wsnHcb")
                if(month):
                    month=month.text
                title=eventInf.find(class_="YOGjf")
                if(title):
                    title=title.text
                image=eventInf.find(class_="YQ4gaf zr758c wA1Bge")
                if(image):
                    image=image.get("src")
                time=eventInf.find(class_="cEZxRc")
                if(time):
                    time=time.text
                
                addressarr=eventInf.find_all(class_="cEZxRc zvDXNd")
                address=""
                for addr in addressarr:
                    if(not address):
                        address+=addr.text
                    else:
                        address+=", "+addr.text
            direction=event.find("a",{'data-url': True,'class':"wY5R3b"})
            if(direction):
                direction="https://www.google.com"+direction["data-url"]
            
            description=event.find(class_="PVlUWc")
            if(description):
                description=description.text
            readmore_link=event.find(class_="zTH3xc")
            if(readmore_link):
                readmore_link=readmore_link.get("href")
            ticket_elements=event.find_all(class_="SKIyM")
            ticket_links=[]
            for element in ticket_elements:
                ticket_links.append(element.get("href"))
            result.append({
                "Day":day,
                "Month":month,
                "Title":title,
                "Image":image,
                "Time":time,
                "Address":address,
                "Direction":direction,
                "Description":description,
                "Readmore_Link":readmore_link,
                "Ticket_Links":ticket_links,
            })
        return result
    
    # this function to fetch all events in a specifc page  note each page has a 10 events
    def __getEventsByPage(self,page):
        html=self.__fetch(self.Query,str(page*10))
        events=self.__scrapEventsFromHtml(html)
        data=self.__extractEventData(events)
        return data

    # This function retrieves all events in a fixed pages number note each page has a 10 events
    def getEventsWithFixedPages(self,pages):
        print("scrap all available events in the first",pages,"pages")
        result=[]
        for i in range(pages):
           data=self.__getEventsByPage(i)
           for d in data:
                result.append(d)
           if(len(data)<10):
                break
        print("events scraped successfully") 
        return result
    
    # This function retrieves all events from all available pages, but it takes some time because it fetches pages synchronously."
    def getAllEvents(self):
        print("scrap all available events")
        result=[]
        i=0
        while(True):
            data=self.__getEventsByPage(i)
            for d in data:
                result.append(d)
            if(len(data)<10):
                break
            i+=1
        print("events scraped successfully") 
        return result
    
    # this function is a wrapper for getEventsByPage function to run inside thread and queue its results
    def __getEventsByPageThreadWrapper(self,page,Queue):
            # print("page: ", page)
        res=self.__getEventsByPage(page)
        if(len(res)>0):
            Queue[page]=res

    # this function is a wrapper for getEventsByPage function to run inside thread and queue its results 
    # and it calculate the number of fetched pages and determine if there is a next page to fetch or not
    def __getEventsByPageThreadWrapper2(self,page,Queue):
        # print("page: ", page)
        res=self.__getEventsByPage(page)
        if(len(res)<10):
            self.hasNext=False
        if(len(res)>0):
            self.NumberOfFetchedPages+=1
            Queue[page]=res

    # You can specify the number of pages to be fetched asynchronously, improving speed.
    # For instance, if 'num_of_concurrent_req' is set to 10, it will fetch 10 pages simultaneously.
    # Once all 10 page results are returned, it will proceed to fetch the next 10 pages, and so on."
    def getEventsWithFixedPagesOptimized(self,pages):
        print("scrap all available events in the first",pages,"pages")
        Queue={}
        Threads=[]
        for i in range(0,pages):
            thread=threading.Thread(target=self.__getEventsByPageThreadWrapper,args=(i,Queue))
            thread.setDaemon(True)
            thread.start()
            # thread.join()
            Threads.append(thread)

        TrhreadsFinished=False
        while(not TrhreadsFinished):
            tmp=True
            for thread in Threads:
                if(thread.is_alive()):
                    tmp=False
                    break
            TrhreadsFinished=tmp

        result=[]
        for j in range(0,pages):
            for row in Queue[j]:
                result.append(row) 
        print("events scraped successfully") 
        return result
    

    def getAllEventsOptimized(self,num_of_concurrant_req=10):
        print("scrap all available events")
        Queue={}
        self.hasNext=True
        self.NumberOfFetchedPages=0
        x=0
        while(self.hasNext):
            Threads=[]
            for i in range(0,num_of_concurrant_req):
                thread=threading.Thread(target=self.__getEventsByPageThreadWrapper2,args=(x+i,Queue))
                thread.setDaemon(True)
                thread.start()
                # thread.join()
                Threads.append(thread)

            TrhreadsFinished=False
            while(not TrhreadsFinished):
                tmp=True
                for thread in Threads:
                    if(thread.is_alive()):
                        tmp=False
                        break
                TrhreadsFinished=tmp
            x=x+num_of_concurrant_req

        result=[]
        for j in range(0,self.NumberOfFetchedPages):
            for row in Queue[j]:
                result.append(row)
        print("events scraped successfully") 
        return result
    
    # this function writes a list of dict to excel document
    def writeDictToExcelFile(self,dict_data,  excel_file_path = 'events.csv'):
        print("writing events to "+ excel_file_path)
        df = pd.DataFrame(dict_data)
        df.to_csv(excel_file_path, index=False)
        

