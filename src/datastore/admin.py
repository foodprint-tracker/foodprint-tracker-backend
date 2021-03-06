from django.contrib import admin
import datastore.models as models


class APIUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'date_of_birth', 'city')


class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'shop',)
    list_filter = ['user__email']
    pass


class ItemAdmin(admin.ModelAdmin):
    pass


class ItemIngredientAdmin(admin.ModelAdmin):
    pass


class AbsIngredientAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.APIUser, APIUserAdmin)
admin.site.register(models.Receipt, ReceiptAdmin)
admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.ItemIngredient, ItemIngredientAdmin)
admin.site.register(models.AbsIngredient, AbsIngredientAdmin)
