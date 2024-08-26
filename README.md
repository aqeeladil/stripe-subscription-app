# Stripe Subscription App
A simple subscription services application that uses Stripe as a payment method and listens to live events using Stripe Webhooks.

### Live Demo
You can view the live project [here](https://aqeeladil.site).
For the video demo, [click here](https://www.awesomescreenshot.com/video/30838159?key=ddc3f34d6f42938fa74ecbe0c07fabe2).

<br>
**To run this locally, run these commands:**

```html
git clone https://github.com/aqeeladil/stripe-subscription-app.git
cd stripe-subscription-app
virtualenv venv
pip install -r requirements.txt    (OR pip install django django-environ stripe psycopg2-binary)
```

```html
python manage.py makemigrations
python manage.py migrate
python manage.py create_plans
```


```html
python manage.py createsuperuser
python manage.py runserver
```


Now http://127.0.0.1:8000/ in your browser to view this project

<br>
**To listen to stripe events, run these commands :**

```html
stripe login
stripe listen --forward-to localhost:8000/subscriptions/webhooks/stripe/
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed
stripe trigger customer.subscription.updated
stripe trigger customer.subscription.deleted

```
<br><br>







        
