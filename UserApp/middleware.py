from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render
from django.shortcuts import redirect
from .forms import *
from django.contrib import auth

View_class = ['login_user_view', 'create_user_view']


class CommonMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            if view_func.__name__ in View_class:
                if request.user.is_authenticated:
                    return redirect("/")
            else:
                if not request.user.is_authenticated:
                    auth.logout(request)
                    return redirect('/login/')
                else:
                    return None
        except Exception as e:
            return render(request, 'sign-in.html', {'error': str(e)})


class CreateUserMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.method == "POST":
            form = CreateUserForm(request.POST, request.FILES)

            if not form.is_valid():
                return render(request, 'sign-in.html', {'form': form})
            else:
                return view_func(request, form)
