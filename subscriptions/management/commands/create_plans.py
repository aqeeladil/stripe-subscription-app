# subs_billing/management/commands/create_plans.py
from django.core.management.base import BaseCommand
from subscriptions.models import Plan

class Command(BaseCommand):
    help = 'Create initial subscription plans'

    def handle(self, *args, **kwargs):
        plans = [
            {
                "name": "Basic",
                "monthly_plan": 10.00,
                "monthly_stripe_plan_id": "price_1234",
                "yearly_plan": 100.00,
                "yearly_stripe_plan_id": "price_5678"
            },
            {
                "name": "Premium",
                "monthly_plan": 20.00,
                "monthly_stripe_plan_id": "price_9101",
                "yearly_plan": 200.00,
                "yearly_stripe_plan_id": "price_1121"
            },
            {
                "name": "Enterprise",
                "monthly_plan": 30.00,
                "monthly_stripe_plan_id": "price_3141",
                "yearly_plan": 300.00,
                "yearly_stripe_plan_id": "price_5161"
            }
        ]

        for plan_data in plans:
            plan, created = Plan.objects.get_or_create(**plan_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created plan: {plan.name}'))
            else:
                self.stdout.write(f'Plan already exists: {plan.name}')
