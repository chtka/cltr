import os
from selenium import webdriver
from searchers import content_types

class Searcher():
    def __init__(self):
        self.fp = webdriver.FirefoxProfile()

        self.fp.set_preference("browser.download.folderList",2)
        self.fp.set_preference("browser.download.manager.showWhenStarting",False)
        self.fp.set_preference("browser.download.dir", os.getcwd())
        self.fp.set_preference("browser.helperApps.neverAsk.saveToDisk", content_types.ALL_CONTENT_TYPES)

        self.browser = webdriver.Firefox(firefox_profile=self.fp)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close_browser()

    def search_and_download_raw(self, search_term):
        raise NotImplementedError("Searchers must implement this method.")

    def close_browser(self):
        self.browser.close()
