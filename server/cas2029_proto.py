# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 22:55:01 2019

@author: roman
"""
# Server side for CAS2029


from flask import Flask


app = Flask (__name__) 


@app.route("/", methods = ['GET'])
def home():
    pass # placeholder
    return "homepage..."

@app.route("/api", methods = ['GET']) 
def api():
    return "api response"

if __name__ == "__main__":
    app.run(debug = False)  