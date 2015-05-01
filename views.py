#!/usr/bin/python

import os
import hashlib
import datetime
import time
import imghdr

from PIL import Image as PILImage

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate

from bottle import jinja2_template as template
from bottle import response, request

from settings import URL, SESSION_LIFE_TIME, MAIL_SENDTO, SMTP_PASSWORD, SMTP_PORT, SMTP_SERVER, SMTP_USERNAME, PAGE_PER_ENTRY, OFFER_TYPES, OFFER_NAMES, ENTRY_IMAGE_DIR, JUNK_FILE_DIR, PROFILE_IMAGE_DIR, ALLOW_IMAGE_TYPE, THUMBNAIL_MAX, IMAGE_FILE_DIR, IMAGES_URL, STATICS_URL, PROFILE_IMAGE_URL, ENTRY_IMAGES_URL

from models import Session, Entry_Image, UserProfile_Image

from locales import locales


def gettext(string, locale='ja'):
    if string in locales[locale]:
        return locales[locale][string]
    return string
_ = gettext


def mail_send(from_address, subject, body, encode='UTF-8'):
    def create_message(from_address, to_address, subject, body, encode):
        message = MIMEText(body, "plain", encode)
        message["Subject"] = str(Header(subject, encode))
        message["From"] = from_address
        message["To"] = to_address
        message["Date"] = formatdate()
        return message

    def sendmail(from_address, to_address, message):
        smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp.sendmail(from_address, [to_address], message.as_string())
        smtp.close()

    message = create_message(from_address, MAIL_SENDTO, subject, body, encode)
    sendmail(from_address, MAIL_SENDTO, message)

    return True


def request_is_get():
    if request.method == 'GET':
        return True
    return False


def form_get(name, default=None):
    try:
        return request.forms.decode().get(name, default)
    except:
        return request.forms.get(name, default)


def signin(user):
    sid = hashlib.sha256(repr(time.time()).encode()).hexdigest()
    response.set_cookie('sid', sid, max_age=SESSION_LIFE_TIME, path='/')
    response.set_cookie('username', user.username, max_age=SESSION_LIFE_TIME, path='/')

    Session.create(
        user=user,
        sid=sid
    )


def signout():
    sid = request.get_cookie('sid', None)

    if sid:
        response.delete_cookie('sid')
        response.delete_cookie('username')
        query = Session.delete().where(Session.sid == sid)
        query.execute()


def session_user():
    sid = request.get_cookie('sid', None)
    username = request.get_cookie('username', None)

    try:
        session = Session.get(Session.sid == sid)
    except:
        signout()
        return None

    if session.accessed_at < datetime.datetime.now() - datetime.timedelta(seconds=SESSION_LIFE_TIME):
        signout()
        return None

    if session.user.username != username:
        return None

    if session.user.is_active is False:
        return None

    return session.user


def make_thumbnail(filename, base_path):
    (name, ext) = os.path.splitext(filename)
    original_filename = name + ".original" + ext

    original_filepath = os.path.join(base_path, original_filename)
    base_filepath = os.path.join(base_path, filename)

    try:
        img = PILImage.open(base_filepath)
        img.save(original_filepath)
        img.thumbnail((THUMBNAIL_MAX, THUMBNAIL_MAX), PILImage.ANTIALIAS)
        img.save(base_filepath)
        del img
    except:
        pass


def upload_images_save(upload_type, upload_images, user, entry=None):
    for upload_image in upload_images:
        file_ext = '.' + imghdr.what(upload_image.file, h=None)
        if file_ext not in ALLOW_IMAGE_TYPE:
            (name, ext) = os.path.splitext(upload_image.filename)
            filename = '%s%s' % (datetime.datetime.now(), ext)
            upload_image.save(os.path.join(JUNK_FILE_DIR, filename))
        else:
            if upload_type == 'entry':
                entry_image_save(upload_image, user, entry, file_ext)
            elif upload_type == 'profile':
                profile_image_save(upload_image, user, file_ext)


def entry_image_save(upload_image, user, entry, file_ext):
    filename = '%s-%s' % (entry.id, file_ext)
    image = Entry_Image.create(
        user=user,
        entry=entry,
        filename=filename,
    )
    save_filename = '%s-%s%s' % (entry.id, image.id, file_ext)
    image.filename = save_filename
    image.save()
    upload_image.save(os.path.join(ENTRY_IMAGE_DIR, save_filename))
    make_thumbnail(image.filename, ENTRY_IMAGE_DIR)


def profile_image_save(upload_image, user, file_ext):
    filename = '%s-%s' % (user.id, file_ext)
    image = UserProfile_Image.create(
        user=user,
        filename=filename,
    )
    save_filename = '%s-%s%s' % (user.id, image.id, file_ext)
    image.filename = save_filename
    image.save()
    upload_image.save(os.path.join(PROFILE_IMAGE_DIR, save_filename))
    make_thumbnail(image.filename, PROFILE_IMAGE_DIR)


def render(template_name, **kwargs):
    return template(template_name, kwargs, request=request, user=session_user(), URL=URL, _=_, form_get=form_get, page_per_entry=PAGE_PER_ENTRY, offer_types=OFFER_TYPES, offer_names=OFFER_NAMES, STATICS_URL=STATICS_URL, IMAGES_URL=IMAGES_URL, PROFILE_IMAGE_URL=PROFILE_IMAGE_URL, ENTRY_IMAGES_URL=ENTRY_IMAGES_URL)
