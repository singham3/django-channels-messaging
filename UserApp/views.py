from django.utils.decorators import decorator_from_middleware
from .middleware import *
from django.contrib.auth import authenticate
from .models import *
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.contrib.sessions.models import Session
from rest_framework.decorators import api_view


@decorator_from_middleware(CreateUserMiddleware)
def create_user_view(request, form):
    if request.method == 'POST':
        try:
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user_profile = form.cleaned_data['user_profile']
            user_save = User(email=email, username=username, is_superuser=False, is_staff=False, is_active=True,
                             user_profile=user_profile)
            user_save.set_password(password)
            user_save.save()
            return redirect('/login/')
        except Exception as e:
            return render(request, 'sign-in.html', {'error': str(e)})
    return render(request, 'sign-in.html')


def login_user_view(request):
    if request.method == "POST":
        try:
            username = request.POST.get("username")
            password = request.POST.get("password")
            if User.objects.filter(username=username).exists():
                user = authenticate(username=username, password=password)
                if user is not None:
                    auth.login(request, user)
                    return redirect('/')
            else:
                return render(request, 'sign-in.html', {'error': 'User Not Exists'})
        except Exception as e:
            return render(request, 'sign-in.html', {'error': str(e)})
    return render(request, 'sign-in.html')


def logout_user_view(request):
    auth.logout(request)
    return redirect('/login/')


def home_view(request):
    sessions = Session.objects.filter()
    uid_list = []
    for session in sessions:
        data = session.get_decoded()
        if request.user.id != int(data.get('_auth_user_id', None)):
            uid_list.append(data.get('_auth_user_id', None))
    return render(request, 'messages_chat_with_tabs.html', {'user': User.objects.get(username=request.user),
                                                            'online_user': User.objects.filter(id__in=uid_list)})


@api_view(['GET', 'POST'])
def chat_user_details_view(request, id=None):
    if id is not None:
        json_user_data = model_to_dict(User.objects.get(id=id))
        json_user_data.pop('password')
        return JsonResponse(json_user_data, safe=False, status=200)


def chat(request):
    return render(request, 'chat.html')


def room(request, room_name):
    return render(request, 'chatroom.html', {
        'room_name': room_name
    })
