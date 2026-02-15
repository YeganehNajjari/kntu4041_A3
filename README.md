 Flask + OpenLayers + GeoServer Web GIS Project

This project is a simple Web GIS application built using:

Flask (Python) – Backend server

OpenLayers (JavaScript) – Map visualization

GeoServer – WMS service provider

Flask Proxy Route – CORS handling

 Project Structure
your-project/
│
├── app.py
├── requirements.txt
│
├── templates/
│   ├── login.html
│   ├── register.html
│   └── map.html
│
├── static/
│   ├── css/style.css
│   └── js/map.js

 How to Run the Project
1️ Clone the Repository
git clone <repository-url>
cd your-project

2 Create a Virtual Environment
python -m venv .venv


Activate (Windows):

.venv\Scripts\activate

3️ Install Dependencies
pip install -r requirements.txt

4️ Run GeoServer

Install GeoServer (Windows Installer version)

Start GeoServer:

C:\GeoServer\bin\startup.bat


Open in browser:

http://localhost:8080/geoserver


Default credentials:

Username: admin
Password: geoserver


Make sure your WMS layer is published and queryable.

5️ Run Flask Application
python app.py


Open in browser:

http://127.0.0.1:5000/map

 CORS Handling (Important)

Since:

GeoServer runs on port 8080

Flask runs on port 5000

The browser blocks direct WMS requests due to CORS policy.

To solve this, a Flask proxy route is implemented:

@app.route("/geoserver/wms")
def geoserver_wms_proxy():
    geoserver_wms = "http://localhost:8080/geoserver/wms"
    upstream = requests.get(geoserver_wms, params=request.args)
    return Response(upstream.content, status=upstream.status_code)


The frontend uses:

http://127.0.0.1:5000/geoserver/wms


instead of calling GeoServer directly.

🗺 Features

Interactive map using OpenLayers

WMS layer integration from GeoServer

GetFeatureInfo support

Basic Login / Register system

Proper CORS handling using backend proxy

⚠ Important Notes

GeoServer must be running before starting Flask.

The WMS layer must:

Be published

Be set as Queryable

Have correct workspace and layer name

JDK 17 is recommended for GeoServer.

🛠 Technologies Used

Python 3.x

Flask

OpenLayers

GeoServer

Java (JDK 17)