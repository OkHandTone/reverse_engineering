from django.contrib import admin

from auth_management.models import AuthUser

from .models import Business


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_on', 'updated_on')
    list_filter = ('created_on',)
    search_fields = ('name', 'owner__username', 'owner__email')
    readonly_fields = ('id', 'created_on', 'updated_on')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'owner':
            kwargs['queryset'] = AuthUser.objects.filter(user_type=AuthUser.UserType.CLIENT)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
