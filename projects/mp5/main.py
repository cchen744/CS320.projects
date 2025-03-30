import pandas as pd
from flask import Flask, request, jsonify,Response
import time
import re
import io
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

# TODO: Add a comment about your data source
#My dataset was collected from 'https://quickstats.nass.usda.gov/'

app = Flask(__name__)
df = pd.read_csv("main.csv")

#For rate limiting
last_visit = {}

#For record visitors
ip_addrs = []

#For A/B testing
global_counter = 0
donation_clicks = {"A": 0, "B": 0}
best_version = None

@app.route('/')
def home():
    global global_counter, best_version
    
    with open("index.html",'r') as f:
        html = f.read()
    
    if global_counter < 10:
        if global_counter % 2 == 0:
            version = "A"
            html=html.replace("VERSION","A").replace("LINK_COLOR",'red')
        else:
            version = "B"
            html=html.replace("VERSION","B").replace("LINK_COLOR",'blue')
    
        global_counter += 1
        
    if best_version is not None:
        version = best_version
        html = html.replace("VERSION", best_version)
        
        if best_version == "A":
            html = html.replace("LINK_COLOR", "red")
        else:
            html = html.replace("LINK_COLOR", "blue")
    
    # html = html.replace("/donate.html", f'donate.html?from={version}') 
    html = html.replace('VERSION', version, 1)  # Replace "VERSION" only once
    html = html.replace('LINK_COLOR', 'red' if version == 'A' else 'blue', 1)
    html = re.sub(r'(<a .*?href=")/donate.html', r'\1donate.html?from=' + version, html, count=1)

    return html

@app.route('/donate.html')
def donation():
    
    global donation_clicks, global_counter,best_version
    source = request.args.get("from","")
    
    if source == 'A':
        donation_clicks['A'] += 1
    elif source == 'B':
        donation_clicks["B"] += 1
    
    
    if global_counter == 10 and best_version is None:
        CTR_A = donation_clicks['A']/10
        CTR_B = donation_clicks['B']/10
                
        best_version = "A" if CTR_A >= CTR_B else "B"
                
    return f"<h1>Please fund me!</h1>"

@app.route('/browse.html')
def show(): 
    html_output = df.to_html(index=False)
    return f"<h1>Browse Data</h1>{html_output}"


@app.route('/browse.json')
def tojson():
    global ip_last_visit
    ip_addr = request.remote_addr
    ip_addrs.append(ip_addr)
    print('IP address:',ip_addr)
    
    current_time = time.time()
    if ip_addr in last_visit and current_time - last_visit[ip_addr] < 60:
        return Response("Please do not access this page so frequently", status=429,headers = {"Retry-After":60,"key":"value"})
        
    last_visit[ip_addr] = current_time
    df_json = df.to_dict(orient="records")  # Convert DataFrame to list of dictionaries
    return jsonify(df_json)  # Return JSON response

    
@app.route('/visitors.json')
#Now add a resource at `http://your-ip:5000/visitors.json` that returns a list of the IP addresses that have visited your `browse.json` resource.
def visitors():
    return jsonify(list(set(ip_addrs)))

@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    if len(re.findall(r"[\w]+@[\w]+\.[A-Za-z]{3}", email)) > 0: # 1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + '\n') # 2
            
        with open("emails.txt", "r") as f:
            num_subscribed = len(f.readlines())+1 # find the number of subscribers
            
        return jsonify(f"thanks, your subscriber number is {num_subscribed}!")
    
    return jsonify( "Warning: Wrong format for email address. Please input email address such as:'abc@xyz.opq'") # 3

@app.route("/dashboard1.svg")
def plot(bins=5):    
    fig, ax = plt.subplots(figsize=(6, 4))
    df['Value'].plot.hist(ax=ax, bins=bins,color = "lavender",edgecolor = "white")
    
    ax.set_ylabel("Corn Yield per Acre")
    ax.set_title("Histogram of Corn Yield per Acre")
    plt.tight_layout()
    
    # save to local
    bins = request.args.get("bins")
    
    f = io.BytesIO() 
    fig.savefig(f, format="svg")
    plt.close()
    
    filename = f"dashboard1_{bins}.svg"
    with open(filename, "wb") as file:
        file.write(f.getvalue())
    
    return Response(f.getvalue(), headers={"Content-type": "image/svg+xml"})

@app.route("/dashboard2.svg")
def plot2(lwd = 1):    
    fig, ax = plt.subplots(figsize=(9, 6))
    
    x = df["Year"]
    y=df["Value"]
    
    ax.plot(x, y, linewidth=lwd,color="#54A375")
    
    ax.set_xlabel("Year")
    ax.set_ylabel("Corn Yield per Acre")
    ax.set_title("Corn Yield Changes with Year")
    plt.tight_layout()
    
    # save to local
    lwd = request.args.get("from")
   
    f = io.BytesIO() 
    fig.savefig(f, format="svg")
    plt.close()
    
    filename = f"dashboard2.svg"
    with open(filename, "wb") as file:
        file.write(f.getvalue())
    
    return Response(f.getvalue(), headers={"Content-type": "image/svg+xml"})

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.