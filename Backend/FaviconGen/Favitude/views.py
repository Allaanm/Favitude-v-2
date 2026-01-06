from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.
def home(request):
  return render(request, 'Favitude/index.html')  

def about(request):
  return render(request, 'Favitude/about.html')


def login_page(request):
  if request.method == 'POST':
      username = request.POST.get('username')
      password =  request.POST.get('password')
      
      user = authenticate(request, username=username, password=password)
      
      if user is not None:
          login(request, user)
          return redirect('Hill:home_page')
      else:
          messages.error(request, 'Username or Password was incorrect')
  
  return render(request, 'Favitude/login.html')

def home_page(request):
  
  return render(request, 'Favitude/home.html')


def signup_page(request):
  if request.method == 'POST':
      username = request.POST.get('username')
      email = request.POST.get('email')
      password = request.POST.get('password')
      
      if User.objects.filter(username=username).exists():
          messages.error(request, 'Username already taken')
      elif User.objects.filter(email=email).exists():
           messages.error(request, 'Email already registered')
      else:
          user = User.objects.create_user(username=username, email=email, password=password)
          user.save()
          login(request, user)
          return redirect('Hill:home_page')
          
  return render(request, 'Favitude/signup.html')  

def contact_page(request):
  return render(request, 'Favitude/contact.html')

def error_page(request):
  return render(request, 'Favitude/error.html')

def generate_page(request):
  return render(request, 'Favitude/generate.html')

def imageGen_page(request):
  return render(request, 'Favitude/imageGen.html')         

def documentation_page(request):
  return render(request, 'Favitude/documentation.html')  

def tutorial_page(request):
  return render(request, 'Favitude/tutorial.html')   

def gen_from_text_page(request):
  return render(request, 'Favitude/gen_from_text.html')     

def privacy_page(request):
  return render(request, 'Favitude/privacy.html')       

def FAQs_page(request):
  return render(request, 'Favitude/FAQs.html')   