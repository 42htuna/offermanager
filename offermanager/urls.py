"""myofferproject URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from offermanager import views
from django.conf import settings

app_name = "offermanager"

urlpatterns = [
    
    # # # DEFAULT
    path('', views.index, name='index'),

    # # # LANGUAGES
    path('i18n/', include('django.conf.urls.i18n')),

    # # # ADMIN
    path('admin/', admin.site.urls),
    path('admin/', views.users, name='admin'),

    # # # USER AUTHENTICATION
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # # # CUSTOMERS
    path('customers/', views.customer_list, name='customer_list'),
    path('customer/<int:customer_id>/', views.customer, name='customer'),
    path('customer/new/', views.new_customer, name='new_customer'),
    path('customer/<int:customer_id>/update/', views.update_customer, name='update_customer'),
    path('customer/<int:customer_id>/delete/', views.delete_customer, name='delete_customer'),

    # # # OFFERS
    path('offer/all/', views.all_offers, name='all_offers'),
    path('offer/draft/', views.draft_offers, name='draft_offers'),
    path('offer/approved/', views.approved_offers, name='approved_offers'),
    path('offer/unapproved/', views.unapproved_offers, name='unapproved_offers'),
    path('offer/canceled/', views.canceled_offers, name='canceled_offers'),
    path('offer/<int:offer_id>/', views.offer, name='offer'),
    path('offer/search/', views.search_offer, name='search_offer'),
    path('offer/new/', views.new_offer, name='new_offer'),
    path('offer/<int:offer_id>/update/', views.update_offer, name='update_offer'),
    path('offer/<int:offer_id>/delete/', views.delete_offer, name='delete_offer'),
    path('offer/<int:offer_id>/passive/', views.passive_offer, name='passive_offer'),
    path('offer/<int:offer_id>/print/', views.print_offer, name='print_offer'),
    path('offer/<int:offer_id>/print/withoutlogo/', views.print_offer_withoutlogo, name='print_offer_withoutlogo'),

    # # # ITEMS
    path('offer/<int:offer_id>/item/add/', views.add_item, name='add_item'),
    path('offer/<int:offer_id>/item/<int:offeritem_id>/delete/', views.delete_item, name='delete_item'),

    # # # REPORTS
    path('accounting/', views.accounting, name='accounting'),
    
    # # # DOCUMENTS
    path('document/recent/', views.recent_documents, name='recent_documents'),
    path('document/all/', views.all_documents, name='all_documents'),
    path('document/cheque/', views.cheques, name='cheques'),
    path('document/bond/', views.bonds, name='bonds'),
    path('document/receipt/', views.receipts, name='receipts'),
    path('document/other/', views.others, name='others'),
    path('document/<int:document_id>/', views.document, name='document'),
    path('document/new/', views.new_document, name='new_document'),
    path('document/<int:document_id>/update/', views.update_document, name='update_document'),
    path('document/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    
    # # # ATTACHMENTS
    path('document/<int:document_id>/attachments/add/', views.upload_document_attachment, name='upload_document_attachment'),
    path('document/<int:document_id>/attachments/<int:documentattachment_id>/delete/', views.delete_document_attachment, name='delete_document_attachment'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
