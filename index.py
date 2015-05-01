#!/usr/bin/python3

import hashlib

from bottle import run, get, post, static_file, error, request, abort

from settings import STATIC_DIR, URL, LENGTH, PROFILE_IMAGE_DIR, ENTRY_IMAGE_DIR, OFFER_TYPES, DEBUG

from views import render, request_is_get, signin, signout, form_get, session_user, mail_send, upload_images_save, _

from models import *


@get(URL['index'])
@get('/index.py')
def index_view():
    template_name = 'index.html'
    return render(template_name)


@get(URL['contact'])
@post(URL['contact'])
def contact_view():
    template_name = 'contact.html'
    if request_is_get():
        return render(template_name)

    name = form_get('name')
    from_address = form_get('email')
    body = form_get('body', '')
    agree = form_get('cb', False)

    if not agree:
        return render(template_name, message=_('Please agree'))

    if not name or not from_address:
        return render(template_name, message=_('has not been entered'))

    send = mail_send(from_address=from_address, subject=_('Was accepted - example.jp'), body="%s\n\n%s" % (name, body))
    if not send:
        return render(template_name, message=_('An error has occurred'))

    return render(template_name, message=_('Has been sent'))


@get(URL['signup'])
@post(URL['signup'])
def signup_view():
    template_name = 'signup.html'
    if request_is_get():
        return render(template_name)

    username = form_get('username')
    password = form_get('password')
    email = form_get('email')
    agree = request.forms.get('cb', False)

    if not agree:
        return render(template_name, message=_('Please agree'))

    if not (username.isalnum() and password.isalnum()):
        return render(template_name, message=_('Username and Password is alphabet or num'))

    if User.select().where(User.username == username, User.password == password).count():
        return render(template_name, message=_('User exist'))

    if not (len(username) >= LENGTH['username'] and len(password) >= LENGTH['password']):
        return render(template_name, message=_('Username or Password not enough'))

    user = User.create(
        username=username,
        password=password,
        password_hash=hashlib.sha256(password.encode()).hexdigest(),
        email=email
    )
    UserProfile.create(
        user=user
    )

    signin(user)

    return render('redirect.html', url=URL['setting'])


@get(URL['signin'])
@post(URL['signin'])
def signin_view():
    template_name = 'signin.html'
    if request_is_get():
        return render(template_name)

    username = form_get('username')
    password = form_get('password')

    try:
        user = User.get(User.username == username, User.password == password, User.is_active == True)
    except:
        return render(template_name, message=_('username or password is an error'))

    signin(user)

    return render('redirect.html', url=URL['index'])


@get(URL['signout'])
def signout_view():
    signout()
    return render('redirect.html', url=URL['index'])


@get(URL['account'])
def account_view():
    template_name = 'account.html'
    return render(template_name)


@get(URL['mypage'])
@get(URL['mypage_page'])
def mypage_view(page=1):
    template_name = 'mypage.html'

    user = session_user()
    if user is None:
        abort(404, _('access denied'))

    if request_is_get():
        entries = Entry.select().where(Entry.user == user, Entry.is_active == True).order_by(Entry.created_at.desc())
        return render(template_name, entries=entries, page=page)


@get(URL['edit'])
@post(URL['edit'])
def edit_view(entry_id):
    template_name = 'edit.html'

    user = session_user()
    if user is None:
        abort(404, _('access denied'))

    try:
        entry = Entry.get(Entry.user == user, Entry.id == entry_id, Entry.is_active == True)
    except:
        abort(404)

    cities = City.select()
    pet_categories = PetCategory.select()
    entry_images = Entry_Image.select().where(Entry_Image.user == user, Entry_Image.entry == entry, Entry_Image.is_active == True)
    if request_is_get():
        return render(template_name, entry=entry, entry_images=entry_images, cities=cities, pet_categories=pet_categories)

    if form_get('remove-image'):
        remove_image_id = form_get('image_id')
        try:
            image = Entry_Image.get(Entry_Image.user == user, Entry_Image.id == remove_image_id)
        except:
            abort(404)
        image.is_active = False
        image.save()
        return render('redirect.html', url='')

    if form_get('close'):
        close_entry_id = form_get('entry_id')
        agree = form_get('cb', False)

        if not agree:
            return render('redirect.html', url='')

        try:
            entry = Entry.get(Entry.user == user, Entry.id == close_entry_id)
        except:
            abort(404)

        entry.is_open = False
        entry.save()
        return render('redirect.html', url=URL['mypage'])

    try:
        city = City.get(City.id == int(form_get('city')))
        city_note = form_get('city_note', '')
        pet_category = PetCategory.get(PetCategory.id == int(form_get('pet_category', '')))
        pet_category_note = form_get('pet_category_note', '')
        petname = form_get('petname', '')
        special = form_get('special', '')
        note = form_get('note', '')
        find_at = form_get('date', datetime.datetime.now())
    except:
        return render(template_name, entry=entry, entry_images=entry_images, cities=cities, pet_categories=pet_categories)

    entry.petcategory = pet_category
    entry.petcategory_note = pet_category_note
    entry.city = city
    entry.city_note = city_note
    entry.name = petname
    entry.special = special
    entry.note = note
    entry.find_at = datetime.datetime.strptime(find_at, '%Y-%m-%d %H:%M')
    entry.modified_at = datetime.datetime.now()
    entry.save()

    upload_images = request.files.getlist('images[]')
    upload_images_save('entry', upload_images, user, entry)

    return render('redirect.html', url=URL['search_entry'].replace('<entry_id:int>', str(entry.id)))


@get(URL['setting'])
@post(URL['setting'])
def setting_view():
    template_name = 'setting.html'

    user = session_user()
    if user is None:
        abort(404, _('access denied'))

    if request_is_get():
        user_images = UserProfile_Image.select().where(UserProfile_Image.user == user, UserProfile_Image.is_active == True)
        return render(template_name, user_images=user_images)

    if form_get('remove-image'):
        remove_image_id = form_get('image_id')
        try:
            image = UserProfile_Image.get(UserProfile_Image.user == user, UserProfile_Image.id == remove_image_id)
        except:
            abort(404)
        image.is_active = False
        image.save()
        return render('redirect.html', url='')

    profile = UserProfile.get(UserProfile.user == user)

    user.email = form_get('email', '')
    user.nickname = form_get('nickname', 'anonymous')
    profile.body = form_get('body', '')
    user.save()
    profile.save()

    upload_images = request.files.getlist('images[]')
    upload_images_save('profile', upload_images, user)

    return render('redirect.html', url=URL['user'].replace('<user_id:int>', str(user.id)))


@get(URL['offer'])
def offer_view():
    template_name = 'offer.html'
    return render(template_name)


@get(URL['offer_form'])
@post(URL['offer_form'])
def offer_form_view(offer_type):
    template_name = 'offer_form.html'
    user = session_user()
    if user is None:
        return render('redirect.html', url=URL['offer'])

    cities = City.select()
    pet_categories = PetCategory.select()
    if request_is_get():
        return render(template_name, cities=cities, pet_categories=pet_categories, offer_type=offer_type)

    for (id, name) in OFFER_TYPES.items():
        if name == offer_type:
            offer_id = id
            break

    try:
        city = City.get(City.id == int(form_get('city')))
        city_note = form_get('city_note', '')
        pet_category = PetCategory.get(PetCategory.id == int(form_get('pet_category', '')))
        pet_category_note = form_get('pet_category_note', '')
        petname = form_get('petname', '')
        special = form_get('special', '')
        note = form_get('note', '')
        find_at = form_get('date', datetime.datetime.now())
    except:
        return render(template_name, cities=cities, pet_categories=pet_categories, offer_type=offer_type)

    entry = Entry.create(
        user=user,
        type=offer_id,
        petcategory=pet_category,
        petcategory_note=pet_category_note,
        city=city,
        city_note=city_note,
        name=petname,
        special=special,
        note=note,
        find_at=datetime.datetime.strptime(find_at, '%Y-%m-%d %H:%M'),
        modified_at=datetime.datetime.now(),
    )

    upload_images = request.files.getlist('images[]')
    upload_images_save('entry', upload_images, user, entry)

    return render('redirect.html', url=URL['search'])


@get(URL['search_city'])
def search_city_view():
    template_name = 'search_city.html'
    if request_is_get():
        cities = City.select().where(City.parent == None)
        return render(template_name, cities=cities)

@get(URL['search_type'])
def search_type_view():
    template_name = 'search_type.html'
    if request_is_get():
        petcategories = PetCategory.select()
        return render(template_name, petcategories=petcategories)


@get(URL['search_city_id'])
@get(URL['search_city_id_page'])
def search_city_id_view(city_id, page=1):
    template_name = 'search_list.html'

    try:
        city = City.get(City.id == city_id)
        if city.parent is not None:
            city = city.parent
    except:
        abort(404)
    if request_is_get():
        entries = Entry.select().join(City).where(((Entry.city == city)|(City.parent == city)), Entry.is_active == True)
        print('---')
        print(entries.count())
        return render(template_name, entries=entries.order_by(Entry.created_at.desc()), city=city, page=page)


@get(URL['search_type_id'])
@get(URL['search_type_id_page'])
def search_type_id_view(type_id, page=1):
    template_name = 'search_list.html'

    try:
        petcategory = PetCategory.get(PetCategory.id == type_id)
    except:
        abort(404)
    if request_is_get():
        entries = Entry.select().where(Entry.petcategory == petcategory, Entry.is_active == True)
        return render(template_name, entries=entries.order_by(Entry.created_at.desc()), petcategory=petcategory, page=page)


@get(URL['search'])
@get(URL['search_page'])
@get(URL['search_from'])
@get(URL['search_from_page'])
def search_from_view(offer_type='full', page=1):
    template_name = 'search_list.html'

    for (id, name) in OFFER_TYPES.items():
        if name == offer_type:
            offer_id = id
            break

    if request_is_get():
        if offer_id == 9:
            entries = Entry.select().where(Entry.is_active == True)
        else:
            entries = Entry.select().where(Entry.type == offer_id, Entry.is_active == True)
        return render(template_name, entries=entries.order_by(Entry.created_at.desc()), page=page, offer_type=offer_type)


@get(URL['search_entry'])
@post(URL['search_entry'])
def search_entry_view(entry_id):
    template_name = 'search_entry.html'

    try:
        entry = Entry.get(Entry.id == entry_id, Entry.is_active == True)
    except:
        abort(404)

    if request_is_get():
        entry_images = Entry_Image.select().where(Entry_Image.entry == entry, Entry_Image.is_active == True)
        entry_comments = Comment.select().where(Comment.entry == entry, Comment.is_active == True)
        return render(template_name, entry=entry, entry_images=entry_images, entry_comments=entry_comments)

    user = session_user()
    if user is None:
        return render('redirect.html', url=URL['signup'])

    body = form_get('body')
    parent = form_get('parent')

    if body is None:
        return render('redirect.html', url='')

    Comment.create(
        user=user,
        entry=entry,
        parent=parent,
        body=body,
    )

    return render('redirect.html', url='')


@get(URL['user'])
@get(URL['user_page'])
def user_view(user_id, page=1):
    template_name = 'user.html'

    try:
        page_user = User.get(User.id == user_id, User.is_active == True)
        page_user_profile = UserProfile.get(UserProfile.user == page_user)
    except:
        abort(404)

    if request_is_get():
        page_user_images = UserProfile_Image.select().where(UserProfile_Image.user == page_user, UserProfile_Image.is_active == True)
        entries = Entry.select().where(Entry.user == page_user, Entry.is_active == True).order_by(Entry.created_at.desc())
        return render(template_name, page_user=page_user, page_user_profile=page_user_profile, entries=entries, page_user_images=page_user_images, page=page)


@get('/statics/<filename:path>')
def send_statics(filename):
    return static_file(filename, root=STATIC_DIR)


@get('/images/entry/<filename:path>')
def send_static_images(filename):
    return static_file(filename, root=ENTRY_IMAGE_DIR)


@get('/images/profile/<filename:path>')
def send_static_profiles(filename):
    return static_file(filename, root=PROFILE_IMAGE_DIR)


@error(404)
def error404(err):
    return render('404.html', error=err)


@error(500)
def error500(err):
    return render('500.html', error=err)


if __name__ == '__main__':
    if DEBUG:
        run(host='localhost', port=8080, reloader=True, debug=True)
    else:
        run(server='cgi')

