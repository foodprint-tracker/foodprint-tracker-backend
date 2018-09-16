from datastore.models import APIUser

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

from decimal import Decimal
import random
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Reads names from a file and create users based on them'


    def add_arguments(self, parser):
        parser.add_argument('names_filename',)
        parser.add_argument('cities_filename',)

        parser.add_argument(
            '--count',
            default=10,
            type=int,
            help='Number of users to generate',
        )

    def handle(self, *args, **options):
        names_fname = options['names_filename']
        cities_fname = options['cities_filename']
        count = options['count']
        created = 0

        with open(cities_fname, 'r') as f:
            all_cities = f.readlines()

        weighted_cities = []
        weight = len(all_cities)
        for city in all_cities:
            weighted_cities += [city.strip()]*weight
            weight -= 1

        with open(names_fname, 'r') as f:
            all_names = f.readlines()


        while all_names and created < count:
            index = random.randint(0, len(all_names) - 1)
            selected = all_names.pop(index)
            if ',' in selected:
                last_name, first_name = selected.split(',',1)
                clean_name = '{} {}'.format(first_name.strip(), last_name.strip())
            else:
                clean_name = selected.strip()

            if APIUser.objects.filter(name=clean_name):
                continue

            user = APIUser()
            user.name = clean_name
            user.email = '%s@example.com' % slugify(clean_name).replace('-','.')
            user.date_of_birth = date(1960, 1,1) + timedelta (days=random.randint(0, 365*40))
            user.country = 'Switzerland'
            user.city = random.choice(weighted_cities)
            user.save()
            created += 1
            self.stdout.write('Created user: %s' % user)

