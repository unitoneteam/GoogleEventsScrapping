from seleniumbase import SB

class Google:
    def __init__(self):
        self.url = 'https://accounts.google.com'
        self.cookies={}

    def login(self, email, password):
        with SB(uc=True,headless=True) as sb:
            sb.get(self.url)
            sb.type("#identifierId", email)
            sb.click("#identifierNext > div > button")
            sb.type("#password > div.aCsJod.oJeWuf > div > div.Xb9hP > input", password)
            sb.click("#passwordNext > div > button")
            self.cookies=sb.driver.get_cookies()
            # dr.save_screenshot("test.png")

    def getcookies(self):
            return self.cookies

