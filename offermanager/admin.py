from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from . models import Employee, Customer, Offer, OfferItem, Document, DocumentAttachment

# Register your models here.
class EmployeeInline(admin.TabularInline):
    model = Employee
    can_delete = False
    verbose_name_plural = _('Employee')

class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeInline,)

class CustomerAdmin(admin.ModelAdmin):
    fieldsets = [(None,	{'fields': ('name',
                                    'address',
                                    'phone',
                                    'email')}),]
    list_display = ['name',
                    'address',
                    'phone',
                    'email',
                    'created_by',
                    'created_at',
                    'updated_by',
                    'updated_at']
    list_filter = ['created_by',
                   'created_at',
                   'updated_by',
                   'updated_at',]
    search_fields = ['name',
                     'address',
                     'phone',
                     'email',]

    def save_model(self, request, obj, *args, **kwargs):
        if not obj.created_by.id:
            obj.created_by=request.user
        obj.updated_by=request.user
        obj.save()

class OfferItemInline(admin.TabularInline):
    model = OfferItem
    extra = 0

class OfferAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['customer']}),
                 (_('DATE INFORMATION'), {'fields': ['date'], 'classes': ['collapse']}),
                 (_('TERMS OF OFFER'), {'fields': ['terms'], 'classes': ['collapse wide']}),
                 (None, {'fields': ['status', 'active']}),]

    inlines = [OfferItemInline]
    list_display = ['id',
                    'customer',
                    'date',
                    'status',
                    'status_offer',
                    'active',
                    'created_by',
                    'created_at',
                    'updated_by',
                    'updated_at']
    list_filter = ['customer',
                   'date',
                   'status',
                   'active',
                   'created_by',
                   'created_at',
                   'updated_by',
                   'updated_at',]
    search_fields = ['id', 'customer__name', 'terms',]

    def save_model(self, request, obj, *args, **kwargs):
        if not obj.created_by.id:
            obj.created_by=request.user
        obj.updated_by=request.user
        obj.save()

class DocumentAttachmentInline(admin.TabularInline):
    model = DocumentAttachment
    extra = 0

class DocumentAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['customer']}),
                 (_('DATE INFORMATION'), {'fields': ['date'], 'classes': ['collapse']}),
                 (_('DESCRIPTION'), {'fields': ['description'], 'classes': ['collapse wide']}),
                 (None, {'fields': ['documenttype', 'amount']}),]

    inlines = [DocumentAttachmentInline]
    list_display = ['id',
                    'customer',
                    'date',
                    'documenttype',
                    'amount',
                    'created_by',
                    'created_at',
                    'updated_by',
                    'updated_at']
    list_filter = ['customer',
                   'date',
                   'documenttype',
                   'created_by',
                   'created_at',
                   'updated_by',
                   'updated_at',]
    search_fields = ['id', 'customer__name', 'amount', 'description',]

    def save_model(self, request, obj, *args, **kwargs):
        if not obj.created_by.id:
            obj.created_by=request.user
        obj.updated_by=request.user
        obj.save()

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(Document, DocumentAdmin)
