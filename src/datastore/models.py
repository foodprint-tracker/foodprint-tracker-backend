from django.db import models


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
    display_name = models.CharField(max_length=64,
                                    help_text='Saved display name of ingredient')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}kg of {}".format(self.kg, self.display_name)

    class Meta:
        verbose_name = 'receipt item'
        ordering = ['-created']



class AbsIngredient(models.Model):
    handle = models.CharField(unique=True, max_length=128,
                              help_text="unique handle of the AbsIngredient")
    display_name = models.CharField(max_length=128)
    description = models.TextField(help_text="Human-friendly description")
    co2_kg = models.DecimalField(max_digits=5, decimal_places=2,
                                 help_text="CO2 footprint per 1kg")
    energy_kg = models.DecimalField(max_digits=5, decimal_places=2,
                                    help_text="kWh footprint per 1kg")
    water_kg = models.DecimalField(max_digits=5, decimal_places=2,
                                   help_text="liters of water per ingredient")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} ({} kg/{} kWh/{} l)".format(self.handle, self.co2_kg, self.energy_kg, self.water_kg)

    class Meta:
        verbose_name = 'abstract ingredient'
        ordering = ['handle']


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
                                    help_text='Computed energy footprint (kWh)')
    water_fp = models.DecimalField(max_digits=7, decimal_places=2, blank=True, default=0,
                                   help_text='Computed water footprint (l)')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}kg of {}".format(self.item.kg, self.display_name)

    class Meta:
        verbose_name = 'item ingredient'
        ordering = ['display_name']

    def save(self, *args, **kwargs):
        if not self.abs_ingredient:
            # Attempt to find a candidate from Abstract ingredients
            abs_in = AbsIngredient.objects.filter(display_name__iexact=self.handle)
            if abs_in:
                # Since the handle is unique, we'd get a single result at most
                self.abs_ingredient = abs_in[0]
        if not self.co2_fp:
            self.co2_fp = self.abs_ingredient.co2_kg * self.concentration * self.item.kg

        if not self.energy_fp:
            self.energy_fp = self.abs_ingredient.energy_kg * self.concentration * self.item.kg

        if not self.water_fp:
            self.water_fp = self.abs_ingredient.water_kg * self.concentration * self.item.kg
        return super().save(*args, **kwargs)
