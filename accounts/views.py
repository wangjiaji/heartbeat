from forms import SignupForm, LoginForm, UserPasswordResetForm
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from heartbeat.http import HttpResponseCreated, HttpResponseOK, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseAccepted
from heartbeat.api import get_api_resource
from django.shortcuts import get_object_or_404
from models import User
from api import UserResource

@require_POST
def register(request):
    form = SignupForm(request.POST)
    if form.is_valid():
        form.save()
        user = authenticate(
            username=form.cleaned_data.get('username'),
            password=form.cleaned_data.get('password1'))
        auth_login(request, user)
        return HttpResponseCreated(get_api_resource(request, UserResource, user), need_dump=False)
    return HttpResponseForbidden(form.errors)

@require_POST
def login(request):
    form = LoginForm(data=request.POST)
    if form.is_valid():
        user = form.get_user()
        auth_login(request, user)
        return HttpResponseOK(get_api_resource(request, UserResource, user), need_dump=False)
    return HttpResponseForbidden(form.errors)

@require_POST
@login_required
def reset_password(request):
    form = UserPasswordResetForm(request.POST)
    if form.is_valid():
        form.save()
        return HttpResponseOK()
    return HttpResponseForbidden(form.errors)

def logout(request):
    auth_logout(request)
    return HttpResponseOK()

@login_required
@require_POST
def add_friend(request, follow_id):
    if follow_id == request.user.id:
        return HttpResponseForbidden('Cannot add yourself')
    followed = get_object_or_404(User, pk=follow_id)

    if request.POST.get('action', 'add') != 'remove':
        request.user.follow(followed)
    else:
        request.user.unfollow(followed)
    return HttpResponseAccepted()

@require_POST
@login_required
def upload_avatar(request):
    user = request.user
    avatar = request.FILES.get('avatar')
    if avatar:
        if user.avatar:
            user.avatar.delete(False)
        user.avatarn = avatar
        user.save()
        resp = HttpResponseCreated()
        resp['Location'] = user.avatar.url
        return resp
    else:
        return HttpResponseBadRequest('No avatar file found')

@require_GET
@login_required
def get_feeds(request):
    feeds = request.user.get_feeds()
    return HttpResponseOK(feeds)

