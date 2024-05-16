from django.contrib.auth.models import User 
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib import messages



def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        print("email, password", email, password)
        if not User.objects.filter(email=email).exists():
            messages.info(request, "This email is not recognised. Please signup to continue.")
            return render(request, "login.html")
        usr = User.objects.get(email=email)
        user = authenticate(request, username=str(usr.username), password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("youtube-index")
        else:
            messages.error(request, "User is none!")
            return render(request, "login.html")
    return render(request, "login.html")

def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password'] 
        confirm_password = request.POST['confirm_password']
        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is taken! Please login if you own this email.")
            return render(request, "signup.html")
        if password != confirm_password:
            messages.error(request, "Password mismatch!")            
            return render(request, "signup.html")
        username = str(email).split("@")[0]
        user = User()
        user.email = email 
        user.username = username
        user.set_password(password)
        user.save()
        messages.success(request, "Signup successful! Please login to continue.")
        return render(request, "login.html")
    
    return render(request, "signup.html")
