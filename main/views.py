
from django.shortcuts import render, get_object_or_404, redirect
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages   
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from subscriptions.models import Plan, Subscription, Profile

# Create your views here.

def home(request):

    plans = Plan.objects.all()
    active_subscription = None
    subscription_category = None

    if request.user.is_authenticated:
        
        try:
            # active_subscription = Subscription.objects.filter(user=request.user, active=True).first()
            active_subscription = Subscription.objects.get(user=request.user, active=True)
            subscription_category = active_subscription.get_plan_category()

        except Subscription.DoesNotExist:
            active_subscription = None

    context = {
        'plans': plans,  
        'active_subscription': active_subscription,
        'subscription_category': subscription_category,
    }
    return render(request, 'home.html', context)


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Logged In!")
                  
            # Ensure the user has a profile
            try:
                profile = user.profile
            except Profile.DoesNotExist:
                Profile.objects.create(user=user)
                
            return redirect('home')
        
        else:
            messages.success(request, "There Was An Error Logging In, Please Try Again...")
            return redirect('home')
    else:
         return render(request, 'registration/login.html')


def register_user(request):
    if request.method == 'POST':
          form = UserRegistrationForm(request.POST)
          if form.is_valid():
               user = form.save(commit=False)
               user.set_password(form.cleaned_data['password1'])
               user.save()
               login(request, user)
               messages.success(request, "You Have Successfully Registered! Welcome!")
               return redirect('home')
    else:
          form = UserRegistrationForm()
          return render(request, 'registration/register.html', {'form':form})
     
    return render(request, 'registration/register.html', {'form':form})


def logout_user(request):
	logout(request)
	messages.success(request, "You Have Been Logged Out...")
	return redirect('home')
















