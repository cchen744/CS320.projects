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
last_visit = 0 

#For record visitors
ip_addrs = []

#For A/B testing
global_counter = 0
donation_clicks = {"A": 0, "B": 0}
best_version = None

@app.route('/')
def home():
    global global_counter
    
    with open("index.html",'r') as f:
        html = f.read()
    
    if global_counter <= 10:
        if global_counter % 2 == 0:
            version = "A"
            html=html.replace("VERSION","A").replace("DONATE_LINK", "/donate?from=A").replace("LINK_COLOR",'red')
        else:
            version = "B"
            html=html.replace("VERSION","B").replace("DONATE_LINK", "/donate?from=B").replace("LINK_COLOR",'blue')
    
        global_counter += 1
    
    else:
        version = best_version # the best version (with the highest CTR)
        if best_version == "A":
            html = html.replace("VERSION", "A").replace("LINK_COLOR", "blue")
        else:
            html = html.replace("VERSION", "B").replace("LINK_COLOR", "red")
    
    html = html.replace("DONATE_LINK", f'donate?from={version}')        

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
def donation(source = ''):
    
    global donation_clicks, global_counter,best_version
    From = request.args.get("from")
    
    if From=='A':
        donation_clicks['A']+=1
    elif From=='B':
        donation_clicks["B"]+=1
    
    print(global_counter)
    
    if global_counter == 10 and best_version is None:
        CTR_A = donation_clicks['A']/10
        CTR_B = donation_clicks['B']/10
                
        best_version = "A" if CTR_A > CTR_B else "B"
                
    return "Please fund me!"

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

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.