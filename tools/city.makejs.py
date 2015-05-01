#!/usr/bin/python3

import sys
import os
import json
sys.path.append(os.pardir)

from models import City


def main():
    cities = City.select()
    city_dict = {}
    for city in cities:
        if city.parent is None:
            city_dict[city.id] = []
            city_dict[city.id].append({'id': city.id, 'name': city.name})
        else:
            city_dict[city.parent.id].append({'id': city.id, 'name': city.name})

    print(json.dumps(city_dict, ensure_ascii=False))

if __name__ == '__main__':
    main()
