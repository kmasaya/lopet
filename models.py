#!/usr/bin/python3

import datetime
import os

from peewee import Model as PeeweeModel, ForeignKeyField, CharField, TextField, BooleanField, IntegerField, DateTimeField

from settings import DB, DB_FILE_PATH, OFFER_TYPES, SEX_TYPES


class BaseModel(PeeweeModel):
    class Meta:
        database = DB


class User(BaseModel):
    username = CharField(max_length=16, unique=True)
    password = CharField(max_length=64)
    password_hash = CharField(max_length=512)
    email = CharField(max_length=128, null=True)
    nickname = CharField(max_length=32, default='anonymous')
    fullname = CharField(max_length=32, null=True)
    telephone = CharField(max_length=32, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    is_active = BooleanField(default=True)


class UserProfile(BaseModel):
    user = ForeignKeyField(User, unique=True)
    body = TextField(default='')


class UserProfile_Image(BaseModel):
    user = ForeignKeyField(User)
    filename = CharField(max_length=32)
    body = TextField(null=True)
    sort_order = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.datetime.now)
    is_active = BooleanField(default=True)


class PetCategory(BaseModel):
    parent = ForeignKeyField('self', null=True)
    name = CharField(max_length=32, unique=True)
    body = TextField(default='')


class City(BaseModel):
    parent = ForeignKeyField('self', null=True)
    name = CharField(max_length=32)
    yomigana = CharField(max_length=32)


class Entry(BaseModel):
    user = ForeignKeyField(User)
    type = IntegerField(choices=tuple(OFFER_TYPES.items()))
    petcategory = ForeignKeyField(PetCategory)
    city = ForeignKeyField(City)

    name = CharField(max_length=32)
    petcategory_note = CharField(max_length=32, default='')
    city_note = CharField(max_length=32, default='')
    sex = IntegerField(choices=tuple(SEX_TYPES.items()), default=0)
    length = IntegerField(default=0)
    scale = IntegerField(default=0)
    age = IntegerField(default=100)
    special = TextField(default='')
    note = TextField(default='')

    find_at = DateTimeField()
    modified_at = DateTimeField()
    created_at = DateTimeField(default=datetime.datetime.now)

    is_open = BooleanField(default=True)
    is_active = BooleanField(default=True)


class Entry_Image(BaseModel):
    user = ForeignKeyField(User)
    entry = ForeignKeyField(Entry, related_name='image')
    filename = CharField(max_length=32)
    body = TextField(null=True)
    sort_order = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.datetime.now)
    is_active = BooleanField(default=True)


class Comment(BaseModel):
    user = ForeignKeyField(User)
    entry = ForeignKeyField(Entry)
    parent = ForeignKeyField('self', null=True)

    body = TextField()

    created_at = DateTimeField(default=datetime.datetime.now)
    is_active = BooleanField(default=True)


class Message(BaseModel):
    send = ForeignKeyField(User, related_name='send')
    to = ForeignKeyField(User, related_name='to')
    parent = ForeignKeyField('self', null=True)

    title = CharField(max_length=32)
    body = TextField()

    created_at = DateTimeField(default=datetime.datetime.now)
    readed_at = DateTimeField(null=True)

    is_active = BooleanField(default=True)


class Session(BaseModel):
    user = ForeignKeyField(User)
    sid = CharField(max_length=512)
    accessed_at = DateTimeField(default=datetime.datetime.now)
    created_at = DateTimeField(default=datetime.datetime.now)


if __name__ == '__main__':
    if not os.path.exists(DB_FILE_PATH):
        User.create_table()
        UserProfile.create_table()
        UserProfile_Image.create_table()
        PetCategory.create_table()
        City.create_table()
        Entry_Image.create_table()
        Entry.create_table()
        Comment.create_table()
        Message.create_table()
        Session.create_table()
