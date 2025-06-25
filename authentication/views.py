from django.shortcuts import render,redirect
from .models import User
import requests
import json
from django.http import JsonResponse
from firebase_admin import auth
from .forms import SignupForm, LoginForm
from django.contrib import messages

FIREBASE_API_KEY = 'AIzaSyA21hPsndPm1DQz5dYuKZW89xb0ixkfeW4'

def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        user_uid = request.session.get("user_uid")  # Check session
        if not user_uid:
            messages.error(request, "You need to log in first.")
            return redirect("auth")  # Redirect to login page
        return view_func(request, *args, **kwargs)
    return wrapper

def auth_view(request):
    signup_form = SignupForm()
    login_form = LoginForm()

    if request.method == "POST":
        if "signup_submit" in request.POST:  # Signup form submitted
            signup_form = SignupForm(request.POST)
            if signup_form.is_valid():
                name = signup_form.cleaned_data["name"]
                email = signup_form.cleaned_data["email"]
                password = signup_form.cleaned_data["password"]

                try:
                    try:
                        user = auth.create_user(email=email, password=password, display_name=name)
                        django_user = User.objects.create(firebase_id=user.uid, email=email, username=name)
                        print("User successfully created in PostgreSQL:", django_user)
                    except Exception as e:
                        print("Error inserting user into PostgreSQL:", str(e))
                    return render(request, "auth/auth.html",{
                        "signup_form": signup_form,
                        "login_form": login_form,
                        "signup_message": "User created successfully! Please log in."
                    })
                except Exception as e:
                    return render(request, "auth/auth.html", {
                        "signup_form": signup_form,
                        "login_form": login_form,  
                        "signup_error": str(e),
                    })

        elif "login_submit" in request.POST:  # Login form submitted
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                email = login_form.cleaned_data["email"]
                password = login_form.cleaned_data["password"]

                try:
                    # Authenticate user via Firebase REST API
                    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
                    payload = {
                        "email": email,
                        "password": password,
                        "returnSecureToken": True
                    }
                    response = requests.post(url, json=payload)
                    data = response.json()
                    if "idToken" in data:  # Authentication successful
                        user_uid = data["localId"]  # Firebase UID
                        request.session["user_uid"] = user_uid
                        request.session.modified = True
                        django_user, created = User.objects.get_or_create(firebase_id=user_uid, defaults={"email": email, "username": email.split("@")[0]})
                        # return render(request, "prediction/predict.html", {
                        #     "signup_form": signup_form,
                        #     "login_form": login_form,
                        #     "login_message": f"Welcome back, {email}!",
                        #     "user_uid": user_uid  # Can be stored in session if needed
                        # })
                        return redirect('predict')
                    else:
                        return render(request, "auth/auth.html", {
                            "signup_form": signup_form,
                            "login_form": login_form,
                            "login_error": "Invalid email or password. Please try again.",
                        })
                    
                except Exception as e:
                    print('error')
                    print(str(e))
                    return render(request, "auth/auth.html", {
                        "signup_form": signup_form,
                        "login_form": login_form,
                        "login_error": 'An unexpected error occurred. Please try again.',
                    })
    return render(request, "auth/auth.html", {
        "signup_form": signup_form,
        "login_form": login_form,
    })

def logout_user(request):
    request.session.flush()  # Clear session
    return redirect("landing")  # Redirect to login page

