# Travian-Automation v0.5

To make operations in Travian via Python3.

## Packages Needed

* requests

* BeautifulSoup(bs4)

## Previous Versions

* v0.1: Built in single driver which bases on Selenium and PhantomJS. Only supports logging in or out, and getting necessary informations from Travian.

* v0.2: Some active operations like upgrading buildings were added.

* v0.3: Split from a whole to three parts: Master, Getter and Setter, which use three drivers simultaneously in order to make each part run its own function independently.

* v0.4: Rewrote by using requests since Selenium is too slow to use. Basic functions were completedly rewrote in this version.

* v0.5: Map search was added.

    * v0.5.1: Account might be banned when searching the map too frequently. Add judgement of whether being banned.
    
    * v0.5.2: Add getting movements of troops. Fixed the exception of when there is no troops in village.