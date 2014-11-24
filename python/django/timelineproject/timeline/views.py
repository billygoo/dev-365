import base64
import json
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from timeline.models import *

def need_auth(functor):
    def try_auth(request, *args, **kwargs):
        print request.META
        if 'HTTP_AUTHORIZATION' in request.META:
            basicauth = request.META['HTTP_AUTHORIZATION']
            user = None
            try:
                print basicauth.split(' ')
                b64key = basicauth.split(' ')[1]
                key = base64.decodestring(b64key)
                print "key:%s" % key
                username, pw = key.split(':')
                print 'username : %s' % username

                user = authenticate(username=username, password=pw)
            except Exception, err:
                print err
                pass
            print 'user : %s' % user
            if user:
                login(request, user)
                request.META['user'] = user
                return functor(request, *args, **kwargs)
        logout(request)
        response = HttpResponse()
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic realm="Timeline Service'
        return response
    return try_auth

def serialize(objs):
    serialized = []
    for obj in objs:
        serialized.append(obj.serialize())
    return serialized

def to_json(objs, status=200):
    j = json.dumps(objs, ensure_ascii=False)
    print '-------------------------------------------------------'
    print j
    print '-------------------------------------------------------'
    return HttpResponse(j, status=status, content_type='application/json; charset=utf-8')

@need_auth
def timeline_view(request):
    messages = Message.objects.order_by('-created').all()
    ignore = request.user.userprofile.get_ignorelist()
    messages = messages.exclude(user__id__in=ignore)
    try:
        tweet_per_page = int(request.GET.get('per_page', 10))
        page_num = int(request.GET.get('page', 1))

        pages = Paginator(messages, tweet_per_page)

        resp = {
            'total_page': pages.num_pages,
            'total_count': pages.count,
            'messages': serialize(pages.page(page_num).object_list)
        }

        return to_json(resp)
    except:
        resp = {
            'status': 'pagination error',
        }
        return to_json(resp, 400)

@need_auth
def message_create_view(request):
    if request.method != 'POST':
        return to_json({'status': 'bad request'}, 400)

    message = Message()
    try:
        message.user = request.user
        message.message = request.POST.get('message', '')
        message.save()
        return to_json({'status':'create success'})
    except:
        return to_json({'status':'bad request'}, 400)

@need_auth
def message_view(request, num):
    try:
        message = Message.objects.get(id=num)
        return to_json(message.serialize())
    except:
        return to_json({'status':'not found'}, 400)

@need_auth
def message_delete_view(request, num):
    try:
        message = Message.objects.get(id=num)
        if message.user == request.user:
            message.delete()
            return to_json({'status': 'deleted'})
        else:
            return to_json({'status': 'forbidden'}, 401)
    except:
        return to_json({'status': 'not found'}, 400)

@need_auth
def like_view(request, num):
    try:
        message = Message.objects.get(id=num)
        like = Like()
        like.user = request.user
        like.message = message
        like.save()
        return to_json({'status': 'created'})
    except:
        return to_json({'status': 'bad request'}, 400)

@need_auth
def find_view(request):
    query = request.GET.get('query', '')

    result = Message.objects.filter(Q(message__contains=query) |
                                    Q(user__userprofile__nickname__contains=query))
    return to_json(serialize(result))

def user_view(request, method):
    if method == 'create' and request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            if User.objects.filter(username__exact=username).count():
                return HttpResponse('duplicate id', 400)
            user = User.objects.create_user(username, password=password)
            user.first_name = request.POST.get('name', '')
            user.save()

            profile = UserProfile()
            profile.user = user
            profile.save()
            return to_json({'status':'create success'})
        except:
            pass
    elif method == 'update' and request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('oldpassword')
            newpassword = request.POST.get('newpassword')
            user = User.objects.get(username__exact=username)
            if user.check_password(password) is False:
                return HttpResponse('wrong password', status=400)
            else:
                user.set_password(newpassword)
                user.first_name = request.POST.get('name', user.first_name)
                user.save()
                return to_json({'status':'updated'})
        except:
            pass
    elif method == 'list':
        users = UserProfile.objects.all()
        return to_json(serialize(users))

    return to_json({'status':'bad request'}, status=400)

@need_auth
def name_view(request):
    if request.method == 'GET':
        data = {
            'name': request.user.first_name,
        }
        return to_json(data)
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            request.user.first_name = name
            request.user.save()
            return to_json({'status': 'updated'})
        except:
            pass
    return to_json({'status': 'bad request'}, 400)

@need_auth
def checkpassword_view(request):
    try:
        if request.method == 'POST':
            password = request.POST.get('password')
            if request.user.check_password(password):
                return to_json({'status': 'ok'})
    except:
        pass
    return to_json({'status': 'no'})

@need_auth
def setpassword_view(request):
    try:
        if request.method == 'POST':
            password = request.POST.get('password')
            if password:
                request.user.set_password(password)
                request.user.save()
                return to_json({'status': 'ok'})
    except:
        pass
    return to_json({'status': 'no'})

@need_auth
def profile_view(request, username=None):
    if username is None:
        username = request.user

    if request.method == 'GET':
        try:
            userprofile = User.objects.get(username=username).userprofile
            return to_json(userprofile.serialize())
        except Exception, err:
            print err
            pass
    elif request.method == 'POST':
        profile = request.user.userprofile
        profile.nickname = request.POST.get('nickname', profile.nickname)
        profile.comment = request.POST.get('comment', profile.comment)
        profile.country = request.POST.get('country', profile.country)
        profile.url = request.POST.get('url', profile.url)
        ignores = request.POST.get('ignore', None)
        if ignores:
            ignores = json.loads(ignores)
            profile.set_ignorelist(ignores)
        profile.save()
        return to_json({'status': 'updated'})
    return to_json({'status': 'not found'}, 400)

@need_auth
def login_view(request):
    return to_json({'status': 'ok', 'user': request.user.userprofile.serialize()})

def serve_html(request, page):
    return render_to_response(page+'.html')