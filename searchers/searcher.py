import os
from selenium import webdriver
from searchers import content_types

class Searcher():
    """ 
    Generic parent class for classes that download raw data from any one of
    the various websites for clinical trials listings.
    """

    def __init__(self):
        """
        Constructor; sets up the Firefox web browser, which
        should be closed upon termination of the driver program.
        """
        self.fp = webdriver.FirefoxProfile()

        self.fp.set_preference("browser.download.folderList",2)
        self.fp.set_preference("browser.download.manager.showWhenStarting",
            False)
        self.fp.set_preference("browser.download.dir", os.getcwd())
        self.fp.set_preference("browser.helperApps.neverAsk.saveToDisk", 
            content_types.ALL_CONTENT_TYPES)

        self.browser = webdriver.Firefox(firefox_profile=self.fp)

    def __enter__(self):
        """
        Context manager method; returns a reference to the object itself.
        """
        return self

    def __exit__(self, *args):
        """
        Context manager method; closes the browser upon termination of the
        program or some failure.
        """
        self.close_browser()

    def search_and_download_raw(self, search_term):
        """
        Searches the corresponding website for clinical trials matching the
        specified search term.

        Args:
            search_term: The search term for which to search the website.
        """
        raise NotImplementedError("Searchers must implement this method.")

    def close_browser(self):
        self.browser.close()
