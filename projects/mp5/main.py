import pandas as pd
from flask import Flask, request, jsonify,Response
import time

# TODO: Add a comment about your data source
#My dataset was collected from 'https://quickstats.nass.usda.gov/'

app = Flask(__name__)
df = pd.read_csv("main.csv")
last_visit = 0
ip_addrs = []


@app.route('/')
def home():
    with open("index.html") as f:
        html = f.read()

    return html

@app.route('/browser')
def show(): 
    return df.to_html(index=False)

@app.route('/browser.json')
def tojson():
    global last_visit
    ip_addr = request.remote_addr
    ip_addrs.append(ip_addr)
    print('IP address:',ip_addr)
    if time.time() - last_visit>60:
        last_visit = time.time()
        df_json = df.to_dict(orient="records")  # Convert DataFrame to list of dictionaries
        return jsonify(df_json)  # Return JSON response
    else:
        return Response("Please do not access this page so frequently", status=429,headers = {"Retry-After":60,"key":"value"})
    
    
@app.route('/visitors.json')
#Now add a resource at `http://your-ip:5000/visitors.json` that returns a list of the IP addresses that have visited your `browse.json` resource.
def visitors():
    return list(set(ip_addrs))

@app.route('/donate')
def donation():
    return "Please fund me!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.