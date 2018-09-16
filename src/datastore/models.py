from django.db import models
from django.template.defaultfilters import slugify

class APIUser(models.Model):
    email = models.fields.EmailField(unique=True)
    name = models.CharField(max_length=256)
    date_of_birth = models.DateField()
    country = models.CharField(max_length=32)
    city = models.CharField(max_length=32)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'User(%s)' % self.email

    class Meta:
        ordering = ['email']


class Receipt(models.Model):
    user = models.ForeignKey(APIUser, on_delete=models.CASCADE)
    shop = models.CharField(max_length=128, blank=True,
                            help_text='Shop name')
    currency = models.CharField(max_length=4, default = 'CHF')
    timestamp = models.DateField(null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}'s receipt from {}".format(self.user, self.timestamp)

    class Meta:
        ordering = ['-timestamp']


class Item(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    kg = models.DecimalField(max_digits=5, decimal_places=3,
                             help_text='Quantity of the item (kg)')
    price = models.DecimalField(max_digits=9, decimal_places=2,
                             help_text='Price of the item (denominated in the currency of the receipt)')
    display_name = models.CharField(max_length=64,
                                    help_text='Saved display name of ingredient')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} ({} kg)".format(self.display_name, self.kg)

    class Meta:
        verbose_name = 'receipt item'
        ordering = ['-created']

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        if not self.itemingredient_set.count():
            # If the slugified item description matches exactly an Abstract Ingredient
            # make an ItemIngredient that's 100% identical with the item itself
            try:
                ai = AbsIngredient.objects.get(handle=slugify(self.display_name))
                ii = ItemIngredient()
                ii.item = self
                ii.abs_ingredient = ai
                ii.concentration = 1
                ii.display_name = self.display_name
            except AbsIngredient.DoesNotExist:
                pass
        return result



class AbsIngredient(models.Model):
    handle = models.CharField(unique=True, max_length=128, blank=True,
                              help_text="unique handle of the AbsIngredient")
    display_name = models.CharField(max_length=128)
    description = models.TextField(help_text="Human-friendly description")
    co2_kg = models.DecimalField(max_digits=5, decimal_places=2,
                                 help_text="Kg CO2 footprint per 1kg")
    energy_kg = models.DecimalField(max_digits=5, decimal_places=2,
                                    help_text="MegaJoules footprint per 1kg")
    water_kg = models.DecimalField(max_digits=5, decimal_places=2,
                                   help_text="cubic meters of water per 1kg")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} ({} kg/{} MJ/{} m^3)".format(self.handle, self.co2_kg, self.energy_kg, self.water_kg)

    class Meta:
        verbose_name = 'abstract ingredient'
        ordering = ['handle']

    def save(self, *args, **kwargs):
        # Auto-generate a handle if it is missing
        if not self.handle:
            self.handle = slugify(self.display_name)
        return super().save(*args, **kwargs)


class ItemIngredient(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    abs_ingredient = models.ForeignKey(
        AbsIngredient, on_delete=models.SET_NULL, null=True)
    display_name = models.CharField(max_length=128,
                                    help_text='Saved display name of ingredient')
    concentration = models.DecimalField(max_digits=4, decimal_places=2,
                                        help_text='Percentage (0-1)')
    co2_fp = models.DecimalField(max_digits=7, decimal_places=2, blank=True, default=0,
                                 help_text='Computed co2 footprint (kg)')
    energy_fp = models.DecimalField(max_digits=7, decimal_places=2, blank=True, default=0,
                                    help_text='Computed energy footprint (MJ)')
    water_fp = models.DecimalField(max_digits=7, decimal_places=2, blank=True, default=0,
                                   help_text='Computed water footprint (m^3)')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}kg of {}".format(self.item.kg, self.display_name)

    class Meta:
        verbose_name = 'item ingredient'
        ordering = ['display_name']

    def save(self, *args, **kwargs):
        if not self.abs_ingredient or not self.co2_fp:
            # Attempt to find a candidate from Abstract ingredients
            abs_in = AbsIngredient.objects.filter(display_name__iexact=self.display_name)
            if abs_in:
                # Since the handle is unique, we'd get a single result at most
                self.abs_ingredient = abs_in[0]
                self.concentration = 1
        if not self.co2_fp and self.abs_ingredient:
            self.co2_fp = self.abs_ingredient.co2_kg * self.concentration * self.item.kg

        if not self.energy_fp and self.abs_ingredient:
            self.energy_fp = self.abs_ingredient.energy_kg * self.concentration * self.item.kg

        if not self.water_fp and self.abs_ingredient:
            self.water_fp = self.abs_ingredient.water_kg * self.concentration * self.item.kg
        return super().save(*args, **kwargs)
