from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from offermanager.cevirici import *

# Create your models here.
STATUS_CHOICES = [('0', _('Draft')),
                  ('1', _('Approved')),
                  ('2', _('Unapproved')),
                  ('3', _('Cancel')),
                  ]

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(_('Department'), max_length=64, blank=True)
    phone = models.CharField(_('Phone'), max_length=16, blank=True)
    def __str__(self):
        return '%s %s - %s' %(self.user.first_name, self.user.last_name, self.phone)

class Customer(models.Model):
    name = models.CharField(_('Customer Name'), max_length=64)
    address = models.CharField(_('Address'), max_length=128, blank=True)
    phone = models.CharField(_('Phone'), max_length=16, blank=True)
    email = models.EmailField(_('E Mail'), max_length=48, blank=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    created_by = models.ForeignKey(User,
                                   on_delete=models.CASCADE,
                                   blank=True,
                                   verbose_name = _('Created by'),
                                   related_name='customers')
    updated_at= models.DateTimeField(_('Updated at'), auto_now=True)
    updated_by = models.ForeignKey(User,
                                   on_delete=models.CASCADE,
                                   verbose_name = _('Updated by'),
                                   related_name='customers_updates',
                                   blank=True)
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    def offers(self):
        return Offer.objects.filter(customer=self, active=True).count()

    def draft_offers(self):
        return Offer.objects.filter(customer=self, active=True, status='0').count()

    def approved_offers(self):
        return Offer.objects.filter(customer=self, active=True, status='1').count()

    def unapproved_offers(self):
        return Offer.objects.filter(customer=self, active=True, status='2').count()

    def cancel_offers(self):
        return Offer.objects.filter(customer=self, active=True, status='3').count()

class Offer(models.Model):
    customer = models.ForeignKey(Customer,
                                 verbose_name=_('Customer'),
                                 on_delete=models.CASCADE)
    date = models.DateTimeField(_('Date'), default=timezone.now)
    terms = models.TextField(_('Terms'), max_length=640, blank=True)
    status = models.CharField(_('Status'),
                              max_length=1,
                              default=0,
                              choices=STATUS_CHOICES)
    active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    created_by = models.ForeignKey(User,
                                   on_delete=models.CASCADE,
                                   blank=True,
                                   verbose_name = _('Created by'),
                                   related_name='offers')
    updated_at= models.DateTimeField(_('Updated at'), auto_now=True)
    updated_by = models.ForeignKey(User,
                                   on_delete=models.CASCADE,
                                   verbose_name = _('Updated by'),
                                   related_name='offers_updates',
                                   blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = _('Offer')
        verbose_name_plural = _('Offers')

    def employee(self):
        o = Offer.objects.get(pk=self.id)
        a = User.objects.get(pk=o.created_by.id)
        e = Employee.objects.get(user_id=a)
        return e

    def total_items_(self):
        total = 0
        items = self.offeritem_set.all()
        for item in items:
            total += item.qty * item.cost
        return round(total, 2)

    def total_tax_(self):
        total = 0
        items = self.offeritem_set.all()
        for item in items:
            total += item.qty * item.cost * item.tax / 100
        return round(total, 2)

    def total_(self):
        total = self.total_items_() + self.total_tax_()
        return round(total, 2)
        
    def yaziyla(self):
        a = str(self.total_()).split('.')
        lira = Cevirici(a[0])
        kurus = Cevirici(a[1])
        yaziyla = "Teklif tutarı yalnız : %s TL %s KR'dir." %(lira.yaz, kurus.yaz)
        return yaziyla

    def total_items(self):
        return "{:,}".format(self.total_items_())

    def total_tax(self):
        return "{:,}".format(self.total_tax_())

    def total(self):
        return "{:,}".format(self.total_())    

    def status_offer(self):
        if '1' not in self.status:
            return False
        else:
            return True

    status_offer.admin_order_field = 'status'
    status_offer.boolean = True
    status_offer.short_description = _('The offer has approved?')

    def draft(self):
        return self.status == '0'

    def approved(self):
        return self.status == '1'

    def unapproved(self):
        return self.status == '2'

    def cancel(self):
        return self.status == '3'

class OfferItem(models.Model):
    UnitType = models.TextChoices('UnitType', 'AD M2 M3 KG')
    offer = models.ForeignKey(Offer,
                              on_delete=models.CASCADE)
    type = models.CharField(_('Type'), max_length=64)
    unit = models.TextField(_('Unit'),
                            max_length=2,
                            blank=True,
                            choices=UnitType.choices)
    qty = models.DecimalField(_('Qty'),
                              decimal_places=2,
                              default=1.00,
                              max_digits=10)
    cost = models.DecimalField(_('Cost'),
                               decimal_places=4,
                               default=0.0000,
                               max_digits=10)
    tax = models.IntegerField(_('Tax'), default=0)

    class Meta:
        verbose_name = _('Offer item')
        verbose_name_plural = _('Offer items')

    def total(self):
        return "{:,}".format(round((self.cost * self.qty), 2))
