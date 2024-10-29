# Stripe Subscription App
A simple subscription services application that uses Stripe as a payment method and listens to live events using Stripe Webhooks.

### Video Demo
For the video demo, [click here](https://www.awesomescreenshot.com/video/30838159?key=ddc3f34d6f42938fa74ecbe0c07fabe2).

<br>
**To run this locally, run these commands:**

```html
git clone https://github.com/aqeeladil/stripe-subscription-app.git
cd stripe-subscription-app
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt    (OR pip install django django-environ stripe psycopg2-binary)
```

```html
cd myproject
python manage.py makemigrations
python manage.py migrate
python manage.py create_plans
```


```html
python manage.py createsuperuser
python manage.py runserver
```


Now open http://127.0.0.1:8000/ in your browser to view this project

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
<br>

### To setup the docker container for the stripe-subscription app, you can create an Ubuntu EC2 Instance on AWS and run the below commands.

```
sudo apt update
sudo apt install docker.io -y
```

```
docker run hello-world
sudo systemctl status docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu

```

**NOTE:** : You need to logout and login back for the changes to be reflected.

Use the same command again, to verify that docker is up and running.

```
docker run hello-world
```

Output should look like:

```
....
....
Hello from Docker!
This message shows that your installation appears to be working correctly.
...
...
```

### Clone this repository

```
git clone https://github.com/aqeeladil/stripe-subscription-app.git
cd /stripe-subscription-app/
```

### Login to Docker [Create an account with https://hub.docker.com/]

```
docker login
docker build -t aqeeladil/subscription-app-image:latest .
docker images
docker run -p 8000:8000 -it aqeeladil/subscription-app-image
```

### Push the Image to DockerHub

```
docker push aqeeladil/subscription-app-image
```

<br>







        
