from django.shortcuts import HttpResponse, render, redirect # For Render Html Files or Redirect Pages
from django.contrib.auth import authenticate, login, logout # For Authenticate Users
from django.contrib.auth.models import User # For Users Informations And Create New Users
from django.contrib import messages # For Using Django Messages
from pytube import YouTube # For Downloading Youtube Videos Or Audios
import os


## Home Page Method
def home(request):
  
  return render(request, 'index.html')

## LogIn Page Method
def logIn(request):
  # Log In Users
  if request.method=="POST":
    userName = request.POST.get("userName")
    userPass = request.POST.get("userPass")
    
    # Authenticate & Login User 
    auth = authenticate(request, username=userName, password=userPass)
    if auth is not None:
      login(request, auth)
      messages.success(request,f"Welcome, {auth}")
      print("Authenticated!",auth)
    else:
      messages.error(request, "Invalid username or password !", extra_tags="danger")
      print("Invalid User.")
      
  return redirect("/")

## SignUp Page Method
def signUp(request):
  # Get Values From Name Attributes
  if request.method=="POST":
    firstName = request.POST.get("firstName")
    lastName = request.POST.get("lastName")
    newUser = request.POST.get("newUser")
    newEmail = request.POST.get("newEmail")
    newPass = request.POST.get("newPass")
    conPass = request.POST.get("conPass")
    
    # Validate New User Details
    if newUser.isidentifier() == False or len(newUser) < 3 or len(newUser) > 10:
      messages.error(request, "Please choose a valid username !", extra_tags="danger")
      return redirect("/")
      
    if newPass != conPass or len(newPass) < 8:
      messages.error(request, "password do not match !", extra_tags="danger")
      return redirect("/")
    
    # Create A New User (!) Handle IntegrityError Error
    try:
      user = User.objects.create_user(username=newUser, email=newEmail, password=newPass)
      user.first_name = firstName # Add Last Name
      user.last_name = lastName # Add First Name
      user.save() # Save User
    except:
      messages.error(request, "Username not available!", extra_tags="danger")
      return redirect("/")
    
    # Login User
    login(request, user)
    messages.success(request, f"Welcome To Our Family {user.username}")
    print("New User Join,",user) # Display In Server
  
  else:
    return HttpResponse("<h1 style='text-align:center;'>404 Error!</h1>") # 404 Error! Text
  
  return redirect("/")
  
## LogOut Page Method
def logOut(request):
  logout(request) # Logout User
  return redirect("/")
  
## Media Page Method
def media(request):
  if request.method == "GET":
    url = request.GET.get("url") # Get Url
    
    global resoures # Global Dictionary Send Datas
    
    # Handle Invalid Urls
    try:
      yt = YouTube(url) # Access Youtube Video or Create Objects
    except:
      messages.error(request, "Invalid URL !", extra_tags="danger")
      return redirect("/")
    
    resoures = { # Resources Dictionary Send To Download Method
        'embedUrl' : url.split("/")[-1],
        'youtubeObj' : yt,
        'itags' :  {}
      }
    # Filtering All Video Resolutions And Storing Their Itags
    for i in yt.streams.filter(progressive=True,subtype="mp4"):
      resoures["itags"][i.resolution] = i.itag
     
  return render(request, 'media.html', resoures)
  
## Download Page Method
def download(request):
  
  if request.method == "POST":
    radioBtn = request.POST.get("radioBtn")
    checkBox = request.POST.get("checkBox")
    
    if radioBtn != None:
      resoures['youtubeObj'].streams.get_by_itag(resoures['itags'][radioBtn]).download("/sdcard/Download")
      messages.success(request, "Video Downloaded")
    else:
      print("None")
      
    if checkBox != None:
      audio = resoures['youtubeObj'].streams.filter(only_audio=True)[-1] # Select High Quality Audio
      audio.download("/sdcard/Download") # Audio Download
      
      # Changing Extention webm to mp3
      os.chdir("/sdcard/Download") # Change Directory
      audioTitle = audio.default_filename # Get Audio File Name
      os.rename(audioTitle , audioTitle.replace("webm","mp3")) # Change Extention
      messages.success(request, "Audio Downloaded")
      
    else:
      print("None")
  else:
    return HttpResponse("<h1 style='text-align:center;'>404 Error!</h1>") # 404 Error! Text

  return redirect("/")
  
