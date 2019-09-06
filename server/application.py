"""
Created on Fri Sep  6 22:55:01 2019

@author: roman
"""
# Server side for CAS2029
import json
import pandas as pd 
from flask import Flask
import urllib.request 


PARAMS = {}

app = Flask (__name__) 
app.secret_key = 'key'

try:
    with urllib.request.urlopen("https://www.data.act.gov.au/resource/emq2-8bc4.json") as url:
        data = json.loads(url.read().decode())
    crash_df = pd.DataFrame(data)
    print('Fetched pedestrian crash data from SODA API')
except:
    print('Failed to call pedestrian SODA API...')

df = crash_df.copy()
df['lat']=df['location'].apply(pd.Series)['latitude']
df['lon']=df['location'].apply(pd. Series)['longitude']
df['lat']=df['lat'].astype('float')
df['lon']=df['lon'].astype('float')


print('crash data:', len(crash_df))
PARAMS ['POINT'] = (-35.241951, 149.090256)  # coord
PARAMS ['RADIUS'] = 2   # radius in km
PARAMS ['TIME'] = 960   # time in minutes after midnight
PARAMS ['MARGIN'] = 100  #margin in minutes to calculate range


@app.route("/", methods = ['GET'])
def home():
    pass # placeholder
    return "homepage..."

@app.route("/api", methods = ['GET']) 
def api():
    return "api response"

