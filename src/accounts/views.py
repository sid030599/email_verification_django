import imp
from lib2to3.pgen2 import token
import uuid
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from accounts.models import Profile
# Create your views here.

@login_required(login_url = '/')
def home(request):
    return render(request , 'home.html')


def login_attempt(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username = username).first()
        if user_obj is None:
            messages.success(request, 'User not found.')
            return redirect('/login')
        
        
        profile_obj = Profile.objects.filter(user = user_obj ).first()

        if not profile_obj.is_verified:
            messages.success(request, 'Profile is not verified check your mail.')
            return redirect('/login')

        user = authenticate(username = username , password = password)
        if user is None:
            messages.success(request, 'Wrong password.')
            return redirect('/login')
        
        login(request , user)
        return redirect('/')

    return render(request , 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            if User.objects.filter(username = username).first():
                messages.success(request, 'user already exists')

                return redirect('/register')
            if User.objects.filter(email = email).first():
                messages.success(request, 'email already exists')

                return redirect('/register')

            user_obj = User(username = username, email = email)
            user_obj.set_password(password)
            user_obj.save()
            auth_token = str(uuid.uuid4())
            profile_obj = Profile(user= user_obj, auth_token = auth_token)
            profile_obj.save()
            send_mail_after_reg(email, auth_token )

            return redirect('/token')
        except Exception as e: 
            print(e)
    

    return render(request, 'register.html')


def verify(request , auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token = auth_token).first()
    

        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'Your account has been already verified.')
                return redirect('/login')

            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Your account has been verified.')
            return redirect('/login')
        else:
            return redirect('/error')
    except Exception as e:
        print(e)
        return redirect('/')

def error_page(request):
    return  render(request , 'error.html')








def success(request):
    return render(request, 'success.html')

def token_send(request):
    return render(request, 'token_send.html')


def send_mail_after_reg(email, token):
    subjects = 'your account to be varified'
    message = f'Hi paste the link to varify your account http://127.0.0.1:8000/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subjects, message, email_from, recipient_list)
