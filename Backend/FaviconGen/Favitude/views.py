from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.conf import settings
import os
from . import utils

# ... existing imports ...

# Create your views here.
def home(request):
  return render(request, 'Favitude/index.html')  

def about(request):
  return render(request, 'Favitude/about.html')


from django.contrib.auth import authenticate, login, logout

# ... (existing imports)

def login_page(request):
  if request.user.is_authenticated:
      return redirect('Hill:home_page')

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

def logout_view(request):
    logout(request)
    return redirect('Hill:landing_page')

@login_required
def home_page(request):
  
  return render(request, 'Favitude/home.html')


def signup_page(request):
  if request.user.is_authenticated:
      return redirect('Hill:home_page')

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
          # Specify the backend since we have multiple configured
          login(request, user, backend='django.contrib.auth.backends.ModelBackend')
          return redirect('Hill:home_page')
          
  return render(request, 'Favitude/signup.html')  

def contact_page(request):
  return render(request, 'Favitude/contact.html')

def error_page(request):
  return render(request, 'Favitude/error.html')

@login_required
def generate_page(request):
  return render(request, 'Favitude/generate.html')

@login_required
def imageGen_page(request):
  if request.method == 'POST' and request.FILES.get('image'):
      image = request.FILES['image']
      try:
          zip_file = utils.generate_favicon_from_image(image)
          return FileResponse(
              zip_file, 
              as_attachment=True, 
              filename='favicons.zip'
          )
      except Exception as e:
          messages.error(request, f"Error generating favicon: {str(e)}")
          
  return render(request, 'Favitude/imageGen.html')         

@login_required
def documentation_page(request):
  return render(request, 'Favitude/documentation.html')  

@login_required
def tutorial_page(request):
  return render(request, 'Favitude/tutorial.html')   

@login_required
def gen_from_text_page(request):
  if request.method == 'POST':
      text = request.POST.get('text')
      # Use defaults if empty
      font_size = request.POST.get('fsize') # Will be empty string if not provided
      bg_shape = request.POST.get('Background')
      font_color = request.POST.get('fcolor')
      bg_color = request.POST.get('bcolor')
      font_type = request.POST.get('ftype') # Note: Template ID is ftype, need to check name attr
      
      if text:
          try:
              zip_file = utils.generate_favicon_from_text(text, font_size, bg_shape, font_color, bg_color, font_type)
              return FileResponse(
                  zip_file,
                  as_attachment=True,
                  filename='favicons_text.zip'
              )
          except Exception as e:
              messages.error(request, f"Error generating favicon: {str(e)}")
      else:
           messages.error(request, "Please enter some text")
           
  return render(request, 'Favitude/gen_from_text.html')     

def privacy_page(request):
  return render(request, 'Favitude/privacy.html')       

@login_required
def download_favicon(request, filename):
    # Security: Whitelist allowed files to prevent arbitrary file access
    ALLOWED_FILES = {
        'Frame1.png', 'Frame2.png', 'Frame3.png', 'Frame5.png',
        'check.png', 'convert.png'
    }
    
    if filename not in ALLOWED_FILES:
        messages.error(request, "Invalid file requested.")
        return redirect('Hill:landing_page')
        
    file_path = os.path.join(settings.BASE_DIR, 'Favitude/static/images/images-home', filename)
    
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    else:
        messages.error(request, "File not found.")
        return redirect('Hill:landing_page')

def FAQs_page(request):
  return render(request, 'Favitude/FAQs.html')   