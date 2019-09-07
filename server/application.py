"""
Created on Fri Sep  6 22:55:01 2019

@author: roman
"""
# Server side for CAS2029
import threading
import json 
import pandas as pd 
from haversine import haversine 
import time 
from flask import Flask, request, render_template, Response, stream_with_context, jsonify, make_response
from urllib.parse import unquote 
import urllib.request 
from flask_limiter import Limiter 
from flask_limiter.util import get_remote_address
import atexit
from bs4 import BeautifulSoup

#########
PARAMS = {}
#########

crash_df = pd.DataFrame()
bom={}

app = Flask(__name__)
limiter = Limiter(app,
                  key_func=get_remote_address,
                  default_limits=["60 per minute"],)
app.secret_key = 'key'



def init_params():
    """
    Initialises parameters
    """
    global PARAMS 
    PARAMS ['POINT'] = (-35.241951, 149.090256)  # coord
    PARAMS ['RADIUS'] = 2   # radius in km
    PARAMS ['TIME'] = 960   # time in minutes after midnight
    PARAMS ['MARGIN'] = 100  #margin in minutes to calculate range



def timeconv(x):
    """
    Converts time form %H:%M format to time in min after midnight
    """
    tmo = time.strptime (x, "%H:%M") 
    return tmo.tm_hour*60+tmo.tm_min


def hd(x):
    """
    Returns haversine distance between (lat, lon) coord and POINT tuple
    """
    global PARAMS
    return haversine((x[0], x[1]), PARAMS ['POINT']) 


# thread for loading data from pedestrian SODA API
def CrashApiCall():
    """
    Updates crash data from pedestrian SODA API
    """
    global t_crash
    global crash_df
    # code for API
    try:
        with urllib.request.urlopen("https://www.data.act.gov.au/resource/emq2-8bc4.json") as url:
            data = json.loads(url.read().decode())
        crash_df = pd.DataFrame(data)
        print('Fetched pedestrian crash data from SODA API')
    except:
        print('Failed to call pedestrian SODA API...')
    runinterval1 = 86400                        # 86400 seconds = 24 hours. API crash data is updated every 24 hours
    t_crash = threading.Timer(runinterval1, CrashApiCall)
    t_crash.daemon=True
    t_crash.start()    



# thread for loading data from cyclist SODA API...       
def CCCrashApiCall():
    """
    Updates crash data from pedestrian SODA API
    """
    global t_crash_cc
    global crash_df_cc
    # code for API
    try:
        with urllib.request.urlopen("https://www.data.act.gov.au/resource/n2kg-qkwj.json") as url:
            data_cc = json.loads(url.read().decode())
        crash_df_cc = pd.DataFrame(data_cc)
        print('Fetched cyclist crash data from SODA API')
    except:
        print('Failed to call cyclist SODA API...')
    runinterval1 = 86400                        # 86400 seconds = 24 hours. API crash data is updated every 24 hours
    t_crash_cc = threading.Timer(runinterval1, CCCrashApiCall)
    t_crash_cc.daemon=True
    t_crash_cc.start()    


def prepare_df(): # pedestrian df
    """
    Prepares reference dataframe
    """
    global crash_df
    df = crash_df.copy()
    
    df['lat']=df['location'].apply(pd.Series)['latitude']
    df['lon']=df['location'].apply(pd. Series)['longitude']
    df['lat']=df['lat'].astype('float')
    df['lon']=df['lon'].astype('float')
    df['time_in_min'] = df.iloc[:,2].apply(timeconv)
    return df


def prepare_dfcc(): # cyclist df
    """
    Prepares reference cyclist crash dataframe
    """
    global crash_df_cc
    df_c = crash_df_cc.copy()
    # rearranging following pedestrian df schema
    dfcc = df_c[['crash_date', 'crash_id', 'crash_time', 'crash_type', 'location_1', 'cyclist_casualties', 'cyclists', 'reported_location', 'severity']] 
    dfcc['lat'] = df_c[['latitude']]
    dfcc['lon'] = df_c[['longitude']]
    dfcc['lat']=dfcc['lat'].astype('float')
    dfcc['lon']=dfcc['lon'].astype('float')
    dfcc['time_in_min'] = dfcc.iloc[:,2].apply(timeconv) 
    return dfcc    
    
    
def check(df, PARAMS):
    """
    Executes user query
    """
    dfc = df.copy()
    crashes = list(set(dfc['crash_type'].values))
    sev = list(set(dfc['severity'].values))
    c1 = dict((e,0) for e in crashes)
    c2 = dict((e,0) for e in sev)
    res_obj = dict(c1)
    res_obj.update(c2)
    dfc['dist_km'] = dfc.iloc[:,9:11].apply(hd, axis=1)    
    # shortlist is our resulting df 
    shortlist = dfc[(dfc['dist_km'] < PARAMS ['RADIUS'])&(dfc['time_in_min'] > PARAMS['TIME']-PARAMS['MARGIN'])&(dfc['time_in_min'] < PARAMS['TIME']+PARAMS['MARGIN'])]
    types_of_crashes = list(set(shortlist['crash_type'].values)) 
    types_of_severity = list(set(shortlist['severity'].values)) 
    # List of dictionalries to return to client 
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
    

    
    
@app.route("/", methods=['GET'])
@limiter.limit("60 per minute") 
def home():
    #pass
    
    return render_template('index.html')


@app.route("/test", methods=['GET'])
@limiter.limit("60 per minute")
def test():
    #pass
    return render_template('test.html')


@app.route("/about", methods=['GET'])
@limiter.limit("60 per minute")
def about():
    #pass
    return render_template('about.html')


@app.route("/contact", methods=['GET'])
@limiter.limit("60 per minute")
def contact():
    #pass
    return render_template('contact.html')
    
 

@app.route("/testapi", methods = ['GET']) 
@limiter.limit("60 per minute") 
def api():
    t_start=time.time() 
    global df 
    global dfcc
    global PARAMS 
    global bom
    params = PARAMS.copy () # init local params with global defaults 
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
        params[ 'RADIUS'] = float(radius_) 
    if time_ :
        params['TIME'] = float(time_) 
    if margin_:
        params['MARGIN'] = float(margin_) 
    
    params['CYCLISTS']=True
    
        
    PARAMS=params
    print('parametrs:', params) 
    results = check(df, params) 
    results_cc=check(dfcc, params)  # for cyclists
    results['response_time'] = time.time()-t_start
    
    res_clean = {}
    res_clean_cc = {}
    for key in results:
        mod_key = key.replace("(","").replace(")","").replace(" ","_").replace("-","") 
        if key !=mod_key:
            res_clean[mod_key] = results[key] 
        else:
            res_clean[key] = results[key]

    for key in results_cc:
        mod_key = key.replace("(","").replace(")","").replace(" ","_").replace("-","") 
        if key !=mod_key:
            res_clean_cc[mod_key] = results_cc[key] 
        else:
            res_clean_cc[key] = results_cc[key]    

    return jsonify([res_clean,  res_clean_cc, bom])


@app.errorhandler(429) 
def ratelimit_handler(e):
    return make_response(jsonify(error="rate limit exceeded %s" % e.description), 429)



def BoMApiCall():
    global t_BoM
    global bom
    try:
        req = urllib.request.Request('http://www.bom.gov.au/products/IDN60903/IDN60903.94926.shtml', headers={'User-Agent': 'Mozilla/5.0'})
        page = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(page, "lxml")
        row_last = soup.find_all('tr', attrs={'class': 'rowleftcolumn'})
        info= row_last[0]
        inf = info.find_all('td')
        bom={}
        bom['update_datetime'] = inf[0].text
        bom['temperature'] = inf[1].text
        bom['apparent_temperature'] = inf[2].text
        bom['dew_point'] = inf[3].text
        bom['rel_humidity'] = inf[4].text
        bom['wind_dir'] = inf[6].text
        bom['wind_spd_kmh'] = inf[7].text
        bom['wind_gust_kmh'] = inf[8].text
        bom['press_qnh'] = inf[11].text
        bom['rainsince9am'] = inf[13].text
        print('refreshed data from BoM')
    except:    
        print(' Could not refresh data from BoM')
    
    runinterval2 = 1800 # seconds in 30 min. BoM data is updated every 30 min, and we are going to fetch it every 30 min
    t_BoM = threading.Timer(runinterval2, BoMApiCall)
    t_BoM.daemon=True
    t_BoM.start()



# cleaning
def close_threads():
    """
    stops all running daemon threads at exit
    """
    global t_crash
    global t_BoM
    try:
        t_crash.cancel()
        print('Closed SODA pedestrian API thread...')
    except:
        print('Could not close pedestrian SODA API thread...')
    try:
        t_BoM.cancel()
        print('Closed BoM weather thread...')
    except:
        print('Could not close BoM weather thread...')  
    try:
        t_crash_cc.cancel()
        print('Closed cyclist SODA API thread...')
    except:
        print('Could not close cyclist SODA API thread...')
    
    


atexit.register(close_threads)
CrashApiCall()
CCCrashApiCall()
BoMApiCall()
print(__doc__)
print('pedestrian crash data:', len(crash_df))
print('cyclist crash data:', len(crash_df_cc))
init_params ()
df = prepare_df()
dfcc=prepare_dfcc()


