"""
Created on Fri Sep  6 22:55:01 2019

@author: roman
"""
# Server side for CAS2029
import json
import pandas as pd 
from haversine import haversine 
import time 
from flask import Flask, request, jsonify
from urllib.parse import unquote 
import urllib.request 

PARAMS = {}
crash_df = pd.DataFrame()
app = Flask (__name__) 
app.secret_key = 'key'

def timeconv(x):
    #time format conversion
    tmo = time.strptime (x, "%H:%M") 
    return tmo.tm_hour*60+tmo.tm_min

def hd(x):
    #haversine
    global PARAMS
    return haversine((x[0], x[1]), PARAMS ['POINT']) 
    
def check(df, PARAMS):
# query
    dfc = df.copy()
    crashes = list(set(dfc['crash_type'].values)) 
    sev = list(set(dfc['severity'].values)) 
    c1 = dict((e,0) for e in crashes) 
    c2 = dict((e,0) for e in sev) 
    res_obj = dict(c1) 
    res_obj.update(c2)
    dfc['dist_km'] = dfc.iloc[:,9:11].apply(hd, axis=1)    
    shortlist = dfc[(dfc['dist_km'] < PARAMS ['RADIUS'])&(dfc['time_in_min'] > PARAMS['TIME']-PARAMS['MARGIN'])&(dfc['time_in_min'] < PARAMS['TIME']+PARAMS['MARGIN'])]
    types_of_crashes = list(set(shortlist['crash_type'].values)) 
    types_of_severity = list(set(shortlist['severity'].values)) 
    out_resp=[] 
    out_resp.append({"total_incidents":len(shortlist)})
    for ct in types_of_crashes:
        instances = len(shortlist[shortlist['crash_type'] == ct]) 
        out_resp.append({ct.replace(" ","_").replace("(","").replace(")",""): instances}) 
        res_obj[ct] = instances
    for st in types_of_severity:
        instances = len(shortlist[shortlist['severity'] == st]) 
        out_resp.append({st.replace(" ","-").replace("(","").replace(")",""): instances})
        res_obj[st] = instances 
    return res_obj
   
    
@app.route("/", methods = ['GET'])
def home():
    pass # placeholder
    return "homepage..."


@app.route("/api", methods = ['GET']) 
def api():
    t_start=time.time() 
    global df 
    global PARAMS 
    params = PARAMS.copy() # init local params with global defaults 
    key_ = None 
    lat_ = None 
    lon_ = None 
    radius_ = None 
    time_ = None 
    margin_ = None 
    try:
        key_ = unquote(request.args.get('KEY')) # not used, but this can be a personalised key connectede to a specific user account
        print(key_) 
    except:
        print("Could not extract parameter: KEY") 
    try:
        lat_ = unquote(request.args.get('LAT'))
        print(lat_) 
    except:
        print("Could not extract parameter: LAT")
    try:
        lon_ = unquote(request.args.get('LON'))
        print(lon_) 
    except:
        print("Could not extract parameter: LON") 
    try:
        radius_ = unquote(request.args.get('RADIUS'))
        print(radius_) 
    except:
        print("Could not extract parameter: RADIUS") 
    try:
        time_ = unquote(request.args.get('TIME'))
        print(time_) 
    except:
        print("Could not extract parameter: TIME") 
    try:
        margin_ = unquote(request.args.get("MARGIN"))
        print(margin_) 
    except:
        print("Could not extract parameter: MARGIN")
    if not key_ :
        print ('no key provided')
        #return Response ('Error: no key provided) 
    if lat_:
        if lon_:
            params['POINT'] = (float(lat_), float(lon_)) 
    if radius_ :
        params [ 'RADIUS'] = float(radius_) 
    if time_ :
        params['TIME'] = float(time_) 
    if margin_:
        params [ 'MARGIN'] = float(margin_) 
    PARAMS=params
    print('parametrs:', params) 
    results = check(df, params) 
    results['response_time'] = time.time()-t_start
    
    res_clean={} 
    for key in results:
        mod_key = key.replace("(","").replace(")","").replace(" ","_").replace("-","") 
        if key !=mod_key:
            res_clean[mod_key] = results[key] 
        else:
            res_clean[key] = results[key]
    return jsonify([res_clean])

###################################################

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
df['time_in_min'] = df.iloc[:,2].apply(timeconv)
print('crash data:', len(crash_df))
PARAMS ['POINT'] = (-35.241951, 149.090256)  # coord
PARAMS ['RADIUS'] = 2   # radius in km
PARAMS ['TIME'] = 960   # time in minutes after midnight
PARAMS ['MARGIN'] = 100  #margin in minutes to calculate range


