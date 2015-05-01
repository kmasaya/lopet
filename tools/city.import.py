#!/usr/bin/python3
# coding: UTF-8

import csv
import sys
import os
sys.path.append(os.pardir)

import kana

from settings import DB

from models import City


FILENAME = 'KEN_ALL.CSV'

CSV_FIELD = (
    'tmp1',
    'tmp2',
    'tmp3',
    'ken-yomigana',
    'shi-yomigana',
    'tmp4',
    'ken',
    'shi',
    'tmp5',
    'tmp6',
    'tmp7',
    'tmp8',
    'tmp9',
    'tmp10',
    'tmp11',
)


def main():
    reader = csv.DictReader(open(FILENAME, 'r', encoding="cp932"), CSV_FIELD)

    DB.begin()

    for i, row in enumerate(reader):
        if i == 0:
            continue
        if not i % 1000:
            print(i)

        cities = City.select().where(City.name == row['ken'])
        if not cities.count():
            parent = City.create(
                parent=None,
                name=row['ken'],
                yomigana=kana.hj(row['ken-yomigana'])
            )
        else:
            parent = City.get(City.name == row['ken'])

        cities = City.select().where(City.name == row['shi'])
        if not cities.count():
            City.create(
                parent=parent,
                name=row['shi'],
                yomigana=kana.hj(row['shi-yomigana'])
            )

    DB.commit()


if __name__ == "__main__":
    main()

