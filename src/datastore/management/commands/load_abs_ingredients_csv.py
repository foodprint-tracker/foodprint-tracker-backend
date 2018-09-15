from datastore.models import AbsIngredient

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

import csv
from decimal import Decimal

class Command(BaseCommand):
    help = 'Reads the abstract ingredients off a CSV formatted file'


    def add_arguments(self, parser):
        parser.add_argument('filename',)

    def handle(self, *args, **options):
        fname = options['filename']
        with open(fname, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                if reader.line_num == 1:
                    self.stdout.write('Found header: %s' % line)
                    continue
                self.stdout.write('%s' % line)
                name, co2, energy, water = line[:4]

                ai,created = AbsIngredient.objects.get_or_create(
                    handle=slugify(name),
                    defaults = {
                        'display_name': name,
                        'co2_kg': Decimal(co2) if co2 else 0,
                        'energy_kg': Decimal(energy) if energy else 0,
                        'water_kg': Decimal(water) if water else 0,
                    }
                )

                if created:
                    self.stdout.write('Created Abstract Ingredient: %s' % ai)