#!/usr/bin/python3
# coding: UTF-8

import csv
import sys
import os
sys.path.append(os.pardir)

from settings import DB

from models import PetCategory


FILENAME = 'PET_ALL.CSV'

CSV_FIELD = (
    'petname',
)


def main():
    reader = csv.DictReader(open(FILENAME, 'r', encoding="cp932"), CSV_FIELD)

    DB.begin()

    for i, row in enumerate(reader):
        PetCategory.create(
            parent=None,
            name=row['petname'],
        )

    DB.commit()


if __name__ == "__main__":
    main()


