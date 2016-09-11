from postcodes import PostCoder
import googlemaps
import json
from datetime import datetime

class PostalCodeDistance(PostCoder):
    MODE = "driving"
    UNITS = 'imperial'
    METERS_IN_A_MILE = 1600

    def __init__(self,postal_code_data, api_key):
        PostCoder.__init__(self)
        self.postal_code_data = postal_code_data
        self.client = googlemaps.Client(api_key)


    def get_postal_codes(self, data):
            # returns a list of lists where each list is a line in data
            postal_code_list = []
            for line in data.splitlines():
                postal_code_list.append(line.replace(" ", "").upper().split("TO"))
            return postal_code_list

    def get_lat_long_list(self,postal_code_list):
        #takes a list of postal codes and returns a list of corresponding lat/long
        lat_long_list = []
        for code in postal_code_list:
            code_data = self.get(code) #invalid postal codes return None
            if(code_data != None):
                lat_long_list.append("{},{}".format(code_data['geo']['lat'],
                    code_data['geo']['lng']))
            else: return 0
        return lat_long_list

    def get_distance(self,single_list, route_choice):
        if single_list == 0:
            return 0
        total_distance = 0
        print(len(single_list))
        for key in range(1,len(single_list)):
            #if key != len(single_list):
            best_route = self.get_best_route_distance(single_list[key-1], single_list[key], route_choice)
            total_distance = total_distance + best_route
        return total_distance

    def get_best_route_distance(self,start, finish, route_choice):
        routes = self.client.directions(start, finish, mode='driving',
            alternatives='True',units='imperial')
        distances = []
        total_time_list = []
        for route in routes:
            total_distance = 0
            total_time = 0
            for leg in route['legs']:
                total_distance = total_distance + leg['distance']['value']
                total_time = total_time + leg['duration']['value']
                total_time_list.append(total_time)
                distances.append(total_distance)
        if route_choice == 'shortest':
            print (min(distances))
            return min(distances)
        else:

            index_of_fastest = total_time_list.index(min(total_time_list))
            return distances[index_of_fastest]


    def get_list_of_distances(self, route_choice):
            lat_long_lists =[]
            list_of_distances = []
            postal_code_lists = self.get_postal_codes(self.postal_code_data)
            for line in postal_code_lists:
                lat_long_lists.append(self.get_lat_long_list(line))
            for single_list in lat_long_lists:
                print(single_list)
                list_of_distances.append(self.get_distance(single_list,route_choice) / self.METERS_IN_A_MILE)
            return list(map(lambda x: round(x, 1), list_of_distances)) #round distances for presentation
