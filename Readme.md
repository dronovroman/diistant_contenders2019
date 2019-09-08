# Cyclist Augmentation System ([CAS'29](http://cas2029.azurewebsites.net/))

We believe that the future of personal transportation in 2029 will be cycling! And in 2029 people will use diverse open data to make it as safe as possible. This is our concept implemented using 2019 technology. 
 
As you ride a bike, your mobile device runs a client app that periodically checks with this server on your location (within a set radius) and time of the day (within a set margin). 
 
The server filters historical pedestrian and cyclists crashes at that point of space and time based on your live location. It provides a statistical summary of crash events in your area as you move, as well as weather conditions from BOM that could affect cyclist safety.
 
Our [API server](http://cas2029.azurewebsites.net/test) data is updated daily from SODA APIs, and every 30 min from the Bureau of meteorology data feed.
 
Statistics on historical crash events around you and their severity, such  as injuries, fatalities, and property damage, can be used for smart object detection and interpretation on your mobile device that will issue voice prompts as you cycle around town.



Proof-of-concept for a cllient-server system involving a data-crunching Python API and an API-consuming mobile app to keep you safe while riding!



###Dataset Highlights

[ACT cyclists crash data](https://www.data.act.gov.au/Justice-Safety-and-Emergency/Cyclist-Crashes/n2kg-qkwj)

[ACT pedestrian crash data]()

[Bureau of Meteorology live feed for ACT]()


#####Work in progress/proof-of-concept: 
(Queensland Open API)
[Crash data from Queensland roads - Open Data Portal | Queensland Government](https://www.data.qld.gov.au/dataset/crash-data-from-queensland-roads)

[QLDTraffic GeoJSON API - Open Data Portal | Queensland Government](https://www.data.qld.gov.au/dataset/131940-traffic-and-travel-information-geojson-api)


 
