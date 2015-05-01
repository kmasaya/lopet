#!/usr/bin/python3

import os

import peewee

DEBUG = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'statics')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'views')
JUNK_FILE_DIR = os.path.join(BASE_DIR, 'junks')
IMAGE_FILE_DIR = os.path.join(BASE_DIR, 'images')
PROFILE_IMAGE_DIR = os.path.join(IMAGE_FILE_DIR, 'profile')
ENTRY_IMAGE_DIR = os.path.join(IMAGE_FILE_DIR, 'entry')

ALLOW_IMAGE_TYPE = ('.png', '.jpeg', '.gif')
THUMBNAIL_MAX = 1024

SESSION_LIFE_TIME = 4*24*60*60

PAGE_PER_ENTRY = 30

DB_FILE_PATH = BASE_DIR + '/lopet.sqlite3'
DB = peewee.SqliteDatabase(DB_FILE_PATH, threadlocals=True)


LENGTH = {
    'username': 6,
    'password': 6,
}

URL = {
    'index': '/',
    'contact': '/contact/',

    'offer': '/offer/',
    'offer_form': '/offer/<offer_type>/',
    'offer_lose': '/offer/lose/',
    'offer_conservation': '/offer/conservation/',
    'offer_witness': '/offer/witness/',

    'search': '/search/',
    'search_page': '/search/<page:int>/',
    'search_from': '/search/<offer_type>/',
    'search_from_page': '/search/<offer_type>/<page:int>/',
    'search_lose': '/search/lose/',
    'search_lose_page': '/search/lose/<page:int>/',
    'search_conservation': '/search/conservation/',
    'search_conservation_page': '/search/conservation/<page:int>/',
    'search_witness': '/search/witness/',
    'search_witness_page': '/search/witness/<page:int>/',
    'search_city': '/search/city/',
    'search_city_id': '/search/city/<city_id:int>/',
    'search_city_id_page': '/search/city/<city_id:int>/<page:int>/',
    'search_type': '/search/type/',
    'search_type_id': '/search/type/<type_id:int>/',
    'search_type_id_page': '/search/type/<type_id:int>/<page:int>/',
    'search_entry': '/e/<entry_id:int>/',

    'account': '/account/',
    'setting': '/setting/',
    'mypage': '/mypage/',
    'mypage_page': '/mypage/<page:int>/',
    'edit': '/edit/<entry_id:int>/',

    'signin': '/signin/',
    'signup': '/signup/',
    'signout': '/signout/',

    'user': '/u/<user_id:int>/',
    'user_page': '/u/<user_id:int>/<page:int>/',
}


OFFER_TYPES = {0: 'lose', 1: 'conservation', 2: 'witness', 9: 'full'}
OFFER_NAMES = {OFFER_TYPES[0]: '迷子', OFFER_TYPES[1]: '保護', OFFER_TYPES[2]: '目撃', OFFER_TYPES[9]: '全て'}
SEX_TYPES = {0: 'unknown', 1: 'male', 2: 'female'}
SEX_NAMES = {SEX_TYPES[0]: '不明', SEX_TYPES[1]: 'オス', SEX_TYPES[2]: 'メス'}

MAIL_SENDTO = ''
SMTP_SERVER = ''
SMTP_PORT = 587
SMTP_USERNAME = ''
SMTP_PASSWORD = ''

if DEBUG:
    STATICS_URL = '/statics/'
    IMAGES_URL = '/images/'
    ENTRY_IMAGES_URL = '/images/entry/'
    PROFILE_IMAGE_URL = '/images/profile/'
else:
    STATICS_URL = 'http://statics.example.jp/'
    IMAGES_URL = 'http://images.example.jp/'
    ENTRY_IMAGES_URL = 'http://images.example.jp/entry/'
    PROFILE_IMAGE_URL = 'http://images.example.jp/profile/'