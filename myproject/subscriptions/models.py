
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Plan(models.Model):
    name = models.CharField(max_length=100)
    monthly_plan = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_stripe_plan_id = models.CharField(max_length=100)
    yearly_plan = models.DecimalField(max_digits=10, decimal_places=2)
    yearly_stripe_plan_id = models.CharField(max_length=100)


    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Plans"
    
    def __str__(self):
        return self.name
    

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # current_period_end = models.DateTimeField(null=True, blank=True)  # Track subscription period end
    canceled_at = models.DateTimeField(null=True, blank=True)  # Track cancellation date/time
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} - {'Active' if self.active else 'Inactive'}"

    def cancel(self):
        """Cancel the subscription"""
        self.active = False
        self.canceled_at = timezone.now()
        self.save()

    def get_plan_category(self):
        if self.plan.monthly_stripe_plan_id:
            return "Monthly"
        elif self.plan.yearly_stripe_plan_id:
            return "Yearly"
        return "Unknown"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username
        
