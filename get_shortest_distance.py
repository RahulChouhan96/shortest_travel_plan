import json
import math
import flask
from flask import request

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"



cities_data_file = open('cities.json', encoding="utf8")
cities_data = json.loads(cities_data_file.read())


# class City:
#     id = "BBA"
#     name = "Balmaceda"
#     location = {
#         "lat": -45.909431,
#         "lon": -71.6976
#     }
#     countryName = "Chile"
#     iata = "BBA"
#     rank = 93
#     countryId = "CL"
#     dest = None
#     airports = [
#         "BBA"
#     ],
#     images = [
#         "4.jpg",
#         "5.jpg"
#     ],
#     popularity = 5.00001
#     regId = "southern-america"
#     contId = "south-america"
#     subId = None
#     terId = None
#     con = 5


def get_distance_from_lat_lon_in_km(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the earth in km
    dLat = deg2rad(lat2-lat1)  # deg2rad below
    dLon = deg2rad(lon2-lon1)
    a = \
        math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * \
        math.sin(dLon/2) * math.sin(dLon/2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c  # Distance in km
    return d


def deg2rad(deg):
    return deg * (math.pi/180)


def get_nearest_continent_city(source_city_data, continents_sequence):
    source_city_continent_id = source_city_data["contId"]
    source_city_location = source_city_data["location"]
    continents_traversed = set(source_city_continent_id)
    shortest_distance_from_source_city = math.inf
    for _, city in cities_data.items():
        if (city["contId"] not in continents_traversed) and (city["contId"] not in continents_sequence):
            source_to_current_city_distance = get_distance_from_lat_lon_in_km(
                source_city_location["lat"], source_city_location["lon"], city["location"]["lat"], city["location"]["lon"]
            )
            if source_to_current_city_distance < shortest_distance_from_source_city:
                shortest_distance_from_source_city = source_to_current_city_distance
                nearest_city = city
            continents_traversed.add(city["contId"])
    return nearest_city


def pick_last_city_continent(fifth_continent_city, first_continent_city, continents_sequence):
    fifth_city_continent_id = fifth_continent_city["contId"]
    fifth_city_location = fifth_continent_city["location"]
    first_city_continent_id = first_continent_city["contId"]
    first_city_location = first_continent_city["location"]
    continents_traversed = set(fifth_city_continent_id)
    shortest_distance_from_fifth_to_first_city = math.inf
    for _, city in cities_data.items():
        if (city["contId"] not in continents_traversed) and (city["contId"] not in continents_sequence):
            fifth_to_current_city_distance = get_distance_from_lat_lon_in_km(
                fifth_city_location["lat"], fifth_city_location["lon"], city["location"]["lat"], city["location"]["lon"]
            )
            current_to_first_city_distance = get_distance_from_lat_lon_in_km(
                city["location"]["lat"], city["location"]["lon"], first_city_location["lat"], first_city_location["lon"]
            )
            source_to_first_city_distance = fifth_to_current_city_distance + \
                current_to_first_city_distance
            if source_to_first_city_distance < shortest_distance_from_fifth_to_first_city:
                shortest_distance_from_fifth_to_first_city = source_to_first_city_distance
                sixth_city = city
            continents_traversed.add(city["contId"])
    return sixth_city


class CityNode:
    def __init__(self, source_city_data) -> None:
        self.current_city = source_city_data
        self.next_city = None


def get_shortest_travel_continents_sequence(source_city_data):
    source_city_continent_id = source_city_data["contId"]
    source_city_location = source_city_data["location"]
    # continents_sequence = [source_city_continent_id]
    current_city_data = source_city_data
    continents_sequence = {}
    city_sequence = CityNode(source_city_data).__dict__
    city_sequence_iterator = city_sequence
    while len(continents_sequence) < 5:
        continents_sequence[current_city_data["contId"]] = "" 
        nearest_continent_city = get_nearest_continent_city(current_city_data, continents_sequence)
        continents_sequence[current_city_data["contId"]] = nearest_continent_city["contId"]
        city_sequence_iterator["next_city"] = CityNode(nearest_continent_city).__dict__
        city_sequence_iterator = city_sequence_iterator["next_city"]
        current_city_data = nearest_continent_city
    continents_sequence[current_city_data["contId"]] = source_city_data["contId"]
    city_sequence_iterator["next_city"] = CityNode(source_city_data).__dict__
    return continents_sequence, city_sequence


@app.route("/travel/plan", methods=['GET'])
def get_shortest_distance():
    print("ARGUMENTS", request.args)
    
    source_city_id = request.args.get("city_id")
    source_city_data = cities_data[source_city_id]
    if not source_city_data:
        raise Exception("Enter correct city ID")
    # continent_to_distance_from_current_city_map = {
    #     source_city_continent_id: 0
    # }
    shortest_continents_travel_sequence, city_sequence = get_shortest_travel_continents_sequence(
        source_city_data)
    print(shortest_continents_travel_sequence)
    city_sequence_response = json.loads(json.dumps(city_sequence))
    city_sequence_response = flask.jsonify(city_sequence_response)
    city_sequence_response.headers.add('Access-Control-Allow-Origin', '*')
    return city_sequence_response


print(len({"a": 1, "b": 2, "c": 3}))
print("a" in {"a": 1})
# get_shortest_distance("BOM")



# Improvements that can be done in the solution:
# To find the next shortest distance city, find the 

app.run()
