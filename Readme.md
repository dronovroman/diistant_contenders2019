# Cyclist Augmentation System (CAS'29)

We believe that the future of personal transportation in 2029 will be cycling! And in 2029 people will use diverse open data to make it as safe as possible. This is our concept implemented using 2019 technology. 
 
As you ride a bike, your mobile device runs a client app that periodically checks with this server on your location (within a set radius) and time of the day (within a set margin). 
 
The server filters historical pedestrian and cyclists crashes at that point of space and time based on your live location. It provides a statistical summary of crash events in your area as you move, as well as weather conditions from BOM that could affect cyclist safety.
 
Our API server data is updated daily from SODA APIs, and every 30 min from the Bureau of meteorology data feed.
 
Statistics on historical crash events around you and their severity, such  as injuries, fatalities, and property damage, can be used for smart object detection and interpretation on your mobile device that will issue voice prompts as you cycle around town.



Proof-of-concept for a cllient-server system involving a data-crunching Python API and an API-consuming mobile app to keep you safe while riding!