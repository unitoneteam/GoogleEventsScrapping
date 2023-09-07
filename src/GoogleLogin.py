from seleniumbase import SB
from time import sleep

class Google:
    def __init__(self):
        self.url = 'https://accounts.google.com'
        self.cookies={}
        self.timeout=30
    # this function login in google account based on gmail and password
    def login(self, email, password):
        with SB(uc=True,headless=True) as sb:
            sb.get(self.url)
            sb.type("#identifierId", email,timeout=self.timeout)
            sb.click("#identifierNext > div > button",timeout=self.timeout)
            sleep(2)
            sb.type("#password > div.aCsJod.oJeWuf > div > div.Xb9hP > input", password,timeout=self.timeout)
            sleep(2)
            sb.click("#passwordNext > div > button",timeout=self.timeout)
            self.cookies=sb.driver.get_cookies()
            # dr.save_screenshot("test.png")

    # this funtion gets the cookies after login
    def getcookies(self):
            return self.cookies

