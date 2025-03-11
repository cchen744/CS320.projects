from collections import deque
import pandas as pd
import time
import requests


class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def visit_and_get_children(self, node):
        """ 
        Leave this method as is! It will be over-written the child classes
        Each child class should perform the following:
            Record the node value in self.order AND return its children
            parameter: node
            return: children of the given node
        """
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        # 1. clear out visited set and order list
        self.visited.clear()
        self.order.clear()
        # 2. start recursive search by calling dfs_visit
        return self.dfs_visit(node)
        
    def dfs_visit(self, node):
        # 1. if this node has already been visited, just `return` (no value necessary)
        if node in self.visited:
            return
        # 2. mark node as visited by adding it to the set
        self.visited.add(node)
        # 3. call self.visit_and_get_children(node) to get the children
        for child in self.visit_and_get_children(node):
            self.dfs_visit(child)
        # 4. in a loop, call dfs_visit on each of the children
        
    def bfs_search(self,node):
        self.visited.clear()
        self.order.clear()
        return self.bfs_visit(node)
    
    def bfs_visit(self,node):
        to_visit = deque([node])
        self.visited.add(node)
        
        while len(to_visit) > 0:
            curr_node = to_visit.popleft()   # Fast O(1) operation
            
            for child in self.visit_and_get_children(curr_node):
                if child not in self.visited:
                    to_visit.append(child)
                    self.visited.add(child)        
        

class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__() # call constructor method of parent class
        self.df = df
        
    def visit_and_get_children(self, node):
        # TODO: Record the node value in self.order
        self.order.append(node)
        children = []
        # TODO: use `self.df` to determine what children the node has and append them
        for node, has_edge in self.df.loc[node].items():
            if has_edge == 1:
                children.append(node)
        return children
    
    
class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__() # call constructor method of parent class
    
    def visit_and_get_children(self,filename):
        with open(f"file_nodes/{filename}",'r') as file:
            lines=file.readlines()
        self.order.append(lines[0].strip()) # Record the node value in self.order
        children = [] # a list of children
        for line in lines[1:]:
            children.extend(line.strip().split(','))
        return children
    
    def concat_order(self):
        c=''.join(self.order)
        return(c)
    
class WebSearcher(GraphSearcher):
    def __init__(self,some_driver):
        super().__init__() # call constructor method of parent class

        self.driver = some_driver
        self.DataFrames = pd.DataFrame() # set up an empty dataframe to store all table in all webs
        
    def visit_and_get_children(self, url):
        # TODO: Record the node value in self.order
        self.driver.get(url) # Direct the driver to the targeted url
        self.order.append(url)
        
        # Using pandas.read_html() to find all table elements in this webpage
        # table = pd.read_html(url)
        
        children = []
        for link in self.driver.find_elements('tag name','a'):
        # TODO: use `self.df` to determine what children the node has and append them
            if link.get_attribute('href') != None:
                children.append(link.get_attribute('href'))
        return children
    
    def table(self):
        
        tables = []
        seen = set()  # Set to track seen URLs
        unique_urls = []

        # Iterate through self.order and preserve the sequence while removing duplicates
        for url in self.order:
            if url not in seen:
                unique_urls.append(url)
                seen.add(url)

        for url in unique_urls:
            table = pd.read_html(url)
            tables.append(table[0])

        # Concatenate all tables and return the result
        return pd.concat(tables, ignore_index=True)
    
def reveal_secrets(driver, url, travellog):
    # Generate a password from the "clue" column of the `travellog` DataFrame.  For example, if `travellog` is the big DataFrame built **after doing BFS** (as shown earlier), the password will start with "171358..."
    password = ''.join(str(x) for x in list(travellog['clue']))
    # driver = webdriver.Chrome(options=options)
    driver.get(url)
    text = driver.find_element("id", "password-textbox")
    text.send_keys(password) # send the password
                       
    button1 = driver.find_element("id","submit-button")
    button1.click() #click the button
    time.sleep(3) # Wait until the page is loaded (perhaps with `time.sleep`)
    
    button2 = driver.find_element('id','location-button')
    button2.click()
    time.sleep(3) # Click the "View Location" button and wait until the result finishes loading
    
    # Save the image that appears to a file named 'Current_Location.jpg' (use the `requests` module to do the download, once you get the URL from selenium)
    img_url=driver.find_element('id','image').get_attribute('src')
    response = requests.get(img_url)
    with open('Current_Location.jpg', 'wb') as file:
        file.write(response.content) 
    
    # Return the current location that appears on the page (should be "CAMP RANDALL STADIUM")
    current_location = driver.find_element('id','location').text 
    return current_location