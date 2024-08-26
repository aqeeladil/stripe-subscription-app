from django.urls import path
from . import views

urlpatterns = [
    path('success/', views.subscription_success, name='success'),
    path('cancel/', views.subscription_cancel, name='subscription_cancel'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
