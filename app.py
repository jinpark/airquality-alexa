import os
from flask import Flask, render_template
from flask_ask import Ask, statement, question
import requests

app = Flask(__name__)
ask = Ask(app, '/')

GEOCODE_URL = "http://www.mapquestapi.com/geocoding/v1/address?key={}&location={}"
AIRVISUAL_LAT_LNG = "http://api.airvisual.com/v2/nearest_city?key={}&lat={}&lon={}"


def airvisual_lag_lng(lat, lng):
    key = os.environ.get('AIRVISUAL_KEY')
    search = requests.get(AIRVISUAL_LAT_LNG.format(key, lat, lng)).json()
    if search["status"] == "success":
        aqi = search["data"]["current"]["pollution"]["aqius"]
        city = search["data"]["city"]
        state = search["data"]["state"]
        return aqi, city, state
    return None, None, None

def aqi_status(aqi):
    if aqi and isinstance( aqi, int ):
        if aqi < 50:
            return "Good"
        elif 50 <= aqi < 100:
            return "Moderate"
        elif 100 <= aqi < 150:
            return "Unhealthy for Sensitive Groups"
        elif 150 <= aqi < 200:
            return "Unhealthy"
        elif 250 <= aqi < 300:
            return "Very Unhealthy"
        elif aqi > 300:
            return "Hazardous"
    return 'Unknown'

def geocode(location):
    key = os.environ.get('MAPQUEST_KEY')
    search = requests.get(GEOCODE_URL.format(key, location)).json()
    status = search["info"]["statuscode"]
    if status == 0 and len(search["results"]) > 0 and len(search["results"][0]["locations"]) > 0:
        found_location = search["results"][0]["locations"][0]
        lat = search["results"][0]["locations"][0]["latLng"]["lat"]
        lng = search["results"][0]["locations"][0]["latLng"]["lng"]
        return lat, lng
    return None, None

@ask.intent('AirQualityIntent',
    mapping={'city': 'City'},
    default={'city': 'seoul'})
def airquality(city):
    lat, lng = geocode(city)
    aqi, area, state = airvisual_lag_lng(lat, lng)
    status = aqi_status(aqi)
    text = render_template('airquality', location="{}, {}".format(area, state), aqi=aqi, status=status)
    return statement(text).simple_card('AirQuality', text)

@ask.launch
def launch():
    launch_text = render_template('launch')
    return question(launch)text.consent_card("read::alexa:device:all:address:country_and_postal_code")

@ask.intent('AMAZON.HelpIntent')
def help():
    help_text = render_template('help')
    return question(help_text).reprompt(help_text)


@ask.intent('AMAZON.StopIntent')
def stop():
    bye_text = render_template('bye')
    return statement(bye_text)


@ask.intent('AMAZON.CancelIntent')
def cancel():
    bye_text = render_template('bye')
    return statement(bye_text)


@ask.app.route('/health')
def health():
    return('OK')

if __name__ == '__main__':
    app.run(debug=True)
