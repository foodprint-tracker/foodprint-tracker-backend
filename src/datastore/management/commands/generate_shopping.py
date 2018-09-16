from datastore.models import APIUser, Receipt, Item, AbsIngredient

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify
from django.utils.timezone import utc


from decimal import Decimal
import random
from datetime import date, timedelta, datetime


composite_foods = {
    'Ham Sandwich' : [0.400, 2.80, {'ham':0.1, 'butter':0.01, 'white bread': 80}],
    'Subway sandwich with turkey': [0.600, 4.90, {'turkey':0.15, 'white bread': 80, 'cheese slices':0.2 , }],
    'Burrito': [0.450, 5.60, {'corn':0.1, 'beef':0.3, 'red kideny beans':'0.2'}],
    }

standard_pack = {
    'butter': [0.25,0.4],
    'almonds': [0.2],
    'almond milk':[1,0.5],
    'cheese slices':[0.15],
    'chocolate': [0.1, 0.05],
    'corn': [0.4],
    'dry pasta': [0.75],
    'low fat organic milk': [1, 0.8],
    'non-free range eggs': [0.4],
    'rice milk': [0.8],
    'spaghetti sarbonara pre-made meal': [0.3],
    'eggs': [0.2]
}

store_names = ['Migros','Coop','Denner','Lidl','Aldi', 'Alnatura']

class Command(BaseCommand):
    help = 'Generates shopping data'


    def add_arguments(self, parser):

        parser.add_argument(
            '--count',
            default=10,
            type=int,
            help='Number of users to generate',
        )

    def handle(self, *args, **options):
        count = options['count']
        composite_food_probability = 0.4
        past_days = 365
        start_time = date.today() - timedelta(days=past_days)
        all_names = AbsIngredient.objects.all().values_list('display_name', flat=True)[:]
        max_items = 5
        max_50g = 30

        created = 0
        users = list(APIUser.objects.filter(email='test@test.com'))
        while created < count:
            rcpt = Receipt()
            rcpt.user = random.choice(users)
            rcpt.shop = random.choice(store_names)
            rcpt.currency = 'CHF'
            rcpt.timestamp = datetime.utcnow() - timedelta(days=random.randint(0,past_days), hours=random.randint(6,18))
            rcpt.save()

            # Generate standard, simple foods that are all known as base ingredients
            items = random.randint(1,max_items)
            for index in range(items):
                item = Item()
                item.receipt = rcpt
                item.display_name = random.choice(all_names)
                if item.display_name.lower() in standard_pack:
                    item.kg = random.choice(standard_pack[item.display_name.lower()])
                else:
                    item.kg = random.randint(1,max_50g) * 0.05
                item.price = random.randint(10,30) * item.kg
                item.save()

            self.stdout.write('Created: %s' % rcpt)
            created += 1

