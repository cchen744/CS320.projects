### Trying out Selenium

Selenium allows us to navigate through websites entirely using code. 
This means that we are able to automate and scrape from sites without 
having to do it all ourselves. It is important to follow restrictions 
when doing so, but this can be quite powerful. 

The selenium install can often result in some issues, so we can check
that everything works correctly right now. For MP4, we will be launching
our own website, and then navigating and scraping from it.


### Launching the Website (from MP4)

You'll be scraping a website implemented as a web application built
using the Flask framework (you don't need to know flask for this
project, though you'll learn it soon and get a chance to build your
own website in the next project).  In an SSH session, run the
following to launch it:

```
python3 application.py
```

### Scraping

By running the following code, we should be able to get everything 
from the homepage of the website. Try using .find_element() to get
the password box and then the "GO" button. From there, we will be able
programmatically type in the password and navigate through the site 
later in MP4.

```python
import os
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

driver = None

def browser():
    global driver

    if not driver:
        os.system("pkill -f -9 chromium")
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
    return driver

driver = browser()

url = "http://YOUR-VM-IP:5000"
driver.get(url)

driver.page_source
```