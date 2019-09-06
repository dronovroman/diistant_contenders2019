# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 22:55:01 2019

@author: roman
"""
# Server side for CAS2029
import json
import pandas as pd 
from flask import Flask
import urllib.request 

app = Flask (__name__) 



try:
    with urllib.request.urlopen("https://www.data.act.gov.au/resource/emq2-8bc4.json") as url:
        data = json.loads(url.read().decode())
    crash_df = pd.DataFrame(data)
    print('Fetched pedestrian crash data from SODA API')
except:
    print('Failed to call pedestrian SODA API...')



@app.route("/", methods = ['GET'])
def home():
    pass # placeholder
    return "homepage..."

@app.route("/api", methods = ['GET']) 
def api():
    return "api response"

if __name__ == "__main__":
    app.run(debug = False)  