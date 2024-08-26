
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Plan, Subscription
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib import messages   
import stripe
import json
import logging


logger = logging.getLogger('django')

stripe.api_key = settings.STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET


    
@login_required
@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        stripe_plan_id = request.POST.get('stripe_plan_id')
        try:
            # Check if user has an active subscription
            active_subscription = Subscription.objects.filter(user=request.user, active=True).first()
            if active_subscription:
                messages.success(request, "You already have an active subscription! Cancel it to subscribe to a new service.")
                return redirect('home')

            
            # Check if user has a Stripe customer ID
            if not hasattr(request.user, 'stripe_customer_id') or not request.user.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=request.user.email
                )
                request.user.stripe_customer_id = customer['id']
                request.user.save()

            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                customer=request.user.stripe_customer_id,
                line_items=[{'price': stripe_plan_id, 'quantity': 1}],
                mode='subscription',
                success_url=request.build_absolute_uri('/subscriptions/success/') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri('/subscriptions/cancel/'),
            )

            return redirect(checkout_session.url, code=303)

        
        except Subscription.DoesNotExist:
            return JsonResponse({'error': 'No active subscription found.'}, status=400)
        
        except Exception as e:
            messages.success(request, "You already have an active subscription! Cancel it to subscribe to a new service.")
            return redirect('home')


    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def subscription_success(request):
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            customer_id = session.customer
            subscription_id = session.subscription

            # Retrieve the subscription
            stripe_subscription = stripe.Subscription.retrieve(subscription_id)
            stripe_plan_id = stripe_subscription['items']['data'][0]['price']['id']

            # Find the corresponding plan in your database
            try:
                plan = Plan.objects.get(monthly_stripe_plan_id=stripe_plan_id)
            except Plan.DoesNotExist:
                plan = Plan.objects.get(yearly_stripe_plan_id=stripe_plan_id)

            # Save the subscription in your database
            Subscription.objects.create(
                user=request.user,
                plan=plan,
                stripe_subscription_id=subscription_id
            )

            # return render(request, 'subscriptions/subscription_success.html')
            messages.success(request, "Subscription created successfully.")
            return redirect('home')

        except Exception as e:
            logger.error(f"Error retrieving session: {e}")
            messages.success(request, "You already have an active subscription! Cancel it to subscribe to a new service.")
            return redirect('home')
            

    return JsonResponse({'error': 'Invalid session_id'}, status=400)



@login_required
def subscription_cancel(request):
    if request.method == 'POST':
        try:
            # Find the user's active subscription
            subscription = Subscription.objects.get(user=request.user, active=True)
            
            stripe.Subscription.delete(subscription.stripe_subscription_id)

            # Mark the subscription as inactive and record the cancellation time
            subscription.active = False
            subscription.canceled_at = timezone.now()
            subscription.save()

            # Redirect or return success response
            messages.success(request, "Your subscription has been canceled successfully..")
            return redirect('home')
        

        except Subscription.DoesNotExist:
            messages.error(request, "No active subscription found.")
            return redirect('home')
        
        except Exception as e:
            logger.error(f"Error canceling subscription: {e}")
            messages.error(request, f"An error occurred: {e}")
            return redirect('home')
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload: {e}")
        # return HttpResponse(status=400)
        return JsonResponse({'error': str(e)}, status=400)

    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        # Invalid signature
        return JsonResponse({'error': str(e)}, status=400)


    # Handle the event
    if event['type'] == 'invoice.payment_succeeded':
        handle_invoice_payment_succeeded(event['data']['object'])
    elif event['type'] == 'invoice.payment_failed':
        handle_invoice_payment_failed(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'])
    else:
        logger.info(f"Unhandled event type {event['type']}")

    # Add more event types as needed


    return JsonResponse({'status': 'success'})

    

def handle_invoice_payment_succeeded(invoice):
    subscription_id = invoice['subscription']
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        subscription.active = True
        subscription.save()
        logger.info(f"Subscription {subscription_id} payment succeeded.")
    except Subscription.DoesNotExist:
        logger.error(f"Subscription with ID {subscription_id} does not exist.")

def handle_invoice_payment_failed(invoice):
    subscription_id = invoice['subscription']
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        subscription.active = False
        subscription.save()
        logger.info(f"Subscription {subscription_id} payment failed.")
    except Subscription.DoesNotExist:
        logger.error(f"Subscription with ID {subscription_id} does not exist.")

def handle_subscription_updated(subscription):
    stripe_subscription_id = subscription['id']
    try:
        subscription_record = Subscription.objects.get(stripe_subscription_id=stripe_subscription_id)
        # Update the subscription record with the new details
        plan_id = subscription['items']['data'][0]['plan']['id']
        try:
            # plan = Plan.objects.get(stripe_plan_id=plan_id)
            plan = Plan.objects.get(monthly_stripe_plan_id=plan_id) or Plan.objects.get(yearly_stripe_plan_id=plan_id)
            subscription_record.plan = plan
            subscription_record.save()
            logger.info(f"Subscription {stripe_subscription_id} updated to plan {plan_id}.")
        except Plan.DoesNotExist:
            logger.error(f"Plan with ID {plan_id} does not exist.")
    except Subscription.DoesNotExist:
        logger.error(f"Subscription with ID {stripe_subscription_id} does not exist.")

def handle_subscription_deleted(subscription):
    stripe_subscription_id = subscription['id']
    try:
        subscription_record = Subscription.objects.get(stripe_subscription_id=stripe_subscription_id)
        subscription_record.active = False
        subscription_record.save()
        logger.info(f"Subscription {stripe_subscription_id} deleted.")
    except Subscription.DoesNotExist:
        logger.error(f"Subscription with ID {stripe_subscription_id} does not exist.")


