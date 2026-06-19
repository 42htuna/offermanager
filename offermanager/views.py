import datetime
import os
import time

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from offermanager.models import (
    Customer,
    Document,
    DocumentAttachment,
    Offer,
    OfferItem,
    OfferStock,
)

def users(request):
    return None

def login_view(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user:
			login(request, user)
			return HttpResponseRedirect(reverse('index'))
		else:
			context = {'error_message' : _('Unable to login! Please check username and password then try again.'),}
			return render(request, 'login.html', context)
	else:
		return render(request, 'login.html')

def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')

@login_required(login_url='login/')
def customer_list(request):
	customers = Customer.objects.order_by('id')
	context = {'title' : _('Customer List'), 'customers' : customers,}
	return render(request, 'customers.html', context)

@login_required(login_url='login/')
def customer(request, customer_id):
	customer = get_object_or_404(Customer, pk=customer_id)
	offers = Offer.objects.filter(customer=customer, created_by=request.user, active=1)
	documents = Document.objects.filter(customer=customer, created_by=request.user)
	context = {'title' : _('Customer info')+" - %s" % customer.name,
               'customer' : customer,
               'offers' : offers,
               'documents' : documents,}
	return render(request, 'customer.html', context)

@login_required(login_url='login/')
def new_customer(request):
    if request.method == 'POST':
        name_input = request.POST['name'].strip()
        
        if Customer.objects.filter(name__iexact=name_input).exists():
            context = {
                'error_message': f"'{name_input}' isimli bir müşteri zaten kayıtlı!",
                'post_data': request.POST
            }
            return render(request, 'new_customer.html', context)
            
        c = Customer(name=name_input,
                     address=request.POST['address'],
                     phone=request.POST['phone'],
                     email=request.POST['email'],
                     created_by=request.user,
                     updated_by=request.user)
        c.save()
        
        if 'savecreate' in request.POST:
            i = Offer(customer=c, created_by=request.user, updated_by=request.user)
            i.save()
            return HttpResponseRedirect(reverse('offer', args=(i.id,)))
        elif 'savecreate_doc' in request.POST:
            i = Document(customer=c, created_by=request.user, updated_by=request.user)
            i.save()
            return HttpResponseRedirect(reverse('document', args=(i.id,)))
        else:
            return HttpResponseRedirect(reverse('customer_list'))
    else:
        return render(request, 'new_customer.html')

@login_required(login_url='login/')
def update_customer(request, customer_id):
    c = get_object_or_404(Customer, pk=customer_id)
    
    if request.method == 'POST':
        name_input = request.POST['name'].strip()
        
        if Customer.objects.filter(name__iexact=name_input).exclude(pk=customer_id).exists():
            
            context = {
                'customer': c,
                'error_message': f"'{name_input}' ismi başka bir müşteri tarafından kullanılıyor!"
            }
            return render(request, 'customer.html', context)
            
        c.name = name_input
        c.address = request.POST['address']
        c.phone = request.POST['phone']
        c.email = request.POST['email']
        c.updated_by = request.user
        c.save()
        
        return HttpResponseRedirect(reverse('customer', args=(c.id,)))

@login_required(login_url='login/')
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    o = Offer.objects.filter(customer=customer_id).count()
    d = Document.objects.filter(customer=customer_id).count()
    if o == 0 and d == 0:
        customer.delete()
    else:
        context = {'error_message' : _('Unable to delete, because there is a recording of this customer!'),}
        return render(request, 'customer.html', context)
    return HttpResponseRedirect(reverse('customer_list'))

@login_required(login_url='login/')
def index(request):
    offers = Offer.objects.filter(created_by=request.user, active=1).order_by('-date')[:25]
    context = {'title' : _('Recent Offers'), 'offer_list' : offers,}
    return render(request, 'index.html', context)

@login_required(login_url='login/')
def all_offers(request):
    offers = Offer.objects.filter(created_by=request.user, active=1).order_by('-date')
    context = {'title' : _('All Offers'), 'offer_list' : offers,}
    return render(request, 'index.html', context)

@login_required(login_url='login/')
def draft_offers(request):
    offers = Offer.objects.filter(created_by=request.user, active=1, status='0').order_by('-date')
    context = {'title' : _('Draft Offers'), 'offer_list' : offers,}
    return render(request, 'index.html', context)

@login_required(login_url='login/')
def approved_offers(request):
    offers = Offer.objects.filter(created_by=request.user, active=1, status='1').order_by('-date')
    context = {'title' : _('Approved Offers'), 'offer_list' : offers,}
    return render(request, 'index.html', context)

@login_required(login_url='login/')
def unapproved_offers(request):
    offers = Offer.objects.filter(created_by=request.user, active=1, status='2').order_by('-date')
    context = {'title' : _('Unapproved Offers'), 'offer_list' : offers,}
    return render(request, 'index.html', context)

@login_required(login_url='login/')
def canceled_offers(request):
    offers = Offer.objects.filter(created_by=request.user, active=1, status='3').order_by('-date')
    context = {'title' : _('Canceled Offers'), 'offer_list' : offers,}
    return render(request, 'index.html', context)

@login_required(login_url='login/')
def offer(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id, created_by=request.user, active=1)
    stocks = OfferStock.objects.all()   
    context = {
        'title' : _('Offer ') + str(offer_id), 
        'offer' : offer,
        'stocks': stocks,
    }
    return render(request, 'offer.html', context)

@login_required(login_url='login/')
def search_offer(request):
    offer_id = request.POST['id']
    if offer_id:
        offers = Offer.objects.filter(created_by=request.user, active=1, pk=offer_id)
        if offers:
            return print_offer(request, offer_id)
        else:
            context = {'error_message' : _('No offers!'),}
            return render(request, 'print_offer.html', context)
    else:
        return render(request, 'print_offer.html')

@login_required(login_url='login/')
def new_offer(request):
	if request.method == 'POST':
		customer_id = request.POST['customer_id']
		if customer_id == 'None':
			customers = Customer.objects.order_by('name')
			context = {'title' : _('New Offer'),
                       'customer_list' : customers,
                       'error_message' : _('Please select a customer.'),}
			return render(request, 'new_offer.html', context)
		else:
			customer = get_object_or_404(Customer, pk=customer_id)
			i = Offer(customer=customer, created_by=request.user, updated_by=request.user)
			i.save()
			return HttpResponseRedirect(reverse('offer', args=(i.id,)))
	else:
		customers = Customer.objects.order_by('name')
		context = {'title' : _('New Offer'), 'customer_list' : customers,}
		return render(request, 'new_offer.html', context)

@login_required(login_url='login/')
def update_offer(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id, created_by=request.user, active=1)
    try:
        offer.date = datetime.datetime.strptime(request.POST['date'], "%d/%m/%Y")
        offer.status = request.POST['status']
        offer.terms = request.POST['terms']
        offer.save()
        stocks = OfferStock.objects.all()
    except (KeyError, Offer.DoesNotExist):
        return render(request, 'offer.html', {'offer': offer, 'error_message': _('Unable to update offer!'),})
    else:
        context = {'confirm_update' : True, 'title' : _('Offer ') + str(offer_id), 'offer' : offer, 'stocks':stocks}
        #return render(request, 'offer.html', context) # Popup menu active
        return HttpResponseRedirect(reverse('offer', args=(offer.id,)))

@login_required(login_url='login/')
def delete_offer(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id, created_by=request.user, active=1)
    offer.delete()
    return HttpResponseRedirect(reverse('index'))

@login_required(login_url='login/')
def passive_offer(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id, created_by=request.user, active=1)
    offer.active = False
    offer.save()
    return HttpResponseRedirect(reverse('index'))

@login_required(login_url='login/')
def print_offer(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id, created_by=request.user, active=1)
    context = {'title' : _('Offer ') + str(offer_id), 'offer' : offer,}
    return render(request, 'print_offer.html', context)

@login_required(login_url='login/')
def print_offer_withoutlogo(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id, created_by=request.user, active=1)
    context = {'title' : _('Offer ') + str(offer_id), 'offer' : offer,}
    return render(request, 'print_offer_withoutlogo.html', context)

@login_required(login_url='login/')
def add_item(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id, created_by=request.user)
    try:
        stock_name = request.POST.get('type', '').strip()
        if stock_name:
            OfferStock.objects.get_or_create(type=stock_name)
        i = offer.offeritem_set.create(
            type=stock_name,
            qty=request.POST['qty'],
            unit=request.POST['unit'],
            cost=request.POST['cost'],
            tax=request.POST['tax'],
        )
        i.save()
    except (KeyError, Offer.DoesNotExist):
        context = {'offer': offer, 'error_message': _('Not all fields were completed.'),}
        return render(request, 'offer.html', context)
    else:
        return HttpResponseRedirect(reverse('offer', args=(offer.id,)))

@login_required(login_url='login/')
def delete_item(request, offeritem_id, offer_id):
	item = get_object_or_404(OfferItem, pk=offeritem_id)
	offer = get_object_or_404(Offer, pk=offer_id, created_by=request.user)
	try:
		item.delete()
	except (KeyError, OfferItem.DoesNotExist):
		context = {'offer': offer, 'error_message': _('Item does not exist.'),}
		return render(request, 'offer.html', context)
	else:
		return HttpResponseRedirect(reverse('offer', args=(offer.id,)))

@login_required(login_url='login/')
def accounting(request):
	if request.method == 'POST':
		start = datetime.datetime.strptime(request.POST['start'], "%d/%m/%Y")
		end = datetime.datetime.strptime(request.POST['end'], "%d/%m/%Y")
		if start > end:
			context = {'error_message' : _('Start date must be before end date!'),}
			return render(request, 'accounting.html', context)
		else:
			approvedoffers = Offer.objects.filter(date__gt=start).filter(date__lt=end).filter(status = '1', created_by=request.user, active=1)
			alloffers = Offer.objects.filter(date__gt=start).filter(date__lt=end).filter(created_by=request.user, active=1)
			offertotal = 0
			for i in approvedoffers:
				if i.active == True:
					offertotal += i.total_()
			context = {'start' : start, 'end' : end, 'offers' : approvedoffers, 'offertotal' : "{:,}".format(offertotal),}
			return render(request, 'accounting.html', context)
	else:
		return render(request, 'accounting.html')

@login_required(login_url='login/')
def recent_documents(request):
    documents = Document.objects.filter(created_by=request.user).order_by('-date')[:25]
    context = {'title' : _('Recent Documents'), 'document_list' : documents,}
    return render(request, 'documents.html', context)

@login_required(login_url='login/')
def all_documents(request):
    documents = Document.objects.filter(created_by=request.user).order_by('-date')
    context = {'title' : _('All Documents'), 'document_list' : documents,}
    return render(request, 'documents.html', context)

@login_required(login_url='login/')
def cheques(request):
    documents = Document.objects.filter(created_by=request.user, documenttype='0').order_by('-date')
    context = {'title' : _('Cheques'), 'document_list' : documents,}
    return render(request, 'documents.html', context)

@login_required(login_url='login/')
def bonds(request):
    documents = Document.objects.filter(created_by=request.user, documenttype='1').order_by('-date')
    context = {'title' : _('Bonds'), 'document_list' : documents,}
    return render(request, 'documents.html', context)

@login_required(login_url='login/')
def receipts(request):
    documents = Document.objects.filter(created_by=request.user, documenttype='2').order_by('-date')
    context = {'title' : _('Receipts'), 'document_list' : documents,}
    return render(request, 'documents.html', context)

@login_required(login_url='login/')
def others(request):
    documents = Document.objects.filter(created_by=request.user, documenttype='3').order_by('-date')
    context = {'title' : _('Others'), 'document_list' : documents,}
    return render(request, 'documents.html', context)

@login_required(login_url='login/')
def document(request, document_id):
    document = get_object_or_404(Document, pk=document_id, created_by=request.user)
    context = {'title' : _('Document ') + str(document_id), 'document' : document,}
    return render(request, 'document.html', context)

@login_required(login_url='login/')
def new_document(request):
	if request.method == 'POST':
		customer_id = request.POST['customer_id']
		if customer_id == 'None':
			customers = Customer.objects.order_by('name')
			context = {'title' : _('New Document'),
                       'customer_list' : customers,
                       'error_message' : _('Please select a customer.'),}
			return render(request, 'new_document.html', context)
		else:
			customer = get_object_or_404(Customer, pk=customer_id)
			i = Document(customer=customer, created_by=request.user, updated_by=request.user)
			i.save()
			return HttpResponseRedirect(reverse('document', args=(i.id,)))
	else:
		customers = Customer.objects.order_by('name')
		context = {'title' : _('New Document'), 'customer_list' : customers,}
		return render(request, 'new_document.html', context)

@login_required(login_url='login/')
def update_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id, created_by=request.user)
    try:
        a = request.POST['amount']
        if a.find(",") != -1:
            a = str(a).replace(",", ".")
        document.date = datetime.datetime.strptime(request.POST['date'], "%d/%m/%Y")
        document.amount = a
        document.documenttype = request.POST['documenttype']
        document.description = request.POST['description']
        document.save()
    except (KeyError, Document.DoesNotExist):
        context = {'document': document, 'error_message': _('Unable to update document!'),}
        return render(request, 'document.html', context)
    else:
        context = {'confirm_update' : True,
                   'title' : _('Document ') + str(document_id),
                   'document' : document,}
        return render(request, 'document.html', context)

@login_required(login_url='login/')
def delete_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id, created_by=request.user)
    for documentattachment in document.documentattachment_set.all():
        a = "./attachments/"+documentattachment.file.name
        os.remove(a)
        z = str(time.asctime())+" "+str(a)+" deleted.\n"
        with open("log.txt", "a") as f:
            f.write(z)
    document.delete()
    return HttpResponseRedirect(reverse('recent_documents'))

@login_required(login_url='login/')
def upload_document_attachment(request, document_id):
    myfile = request.FILES['file']
    document = get_object_or_404(Document, pk=document_id, created_by=request.user)
    fs = FileSystemStorage()
    fs.save(myfile.name, myfile)
    e = document.documentattachment_set.create(file=myfile, displayname=myfile.name)
    e.save()
    z = str(time.asctime())+" ./attachments/document/"+str(myfile)+" added.\n"
    with open("log.txt", "a") as f:
        f.write(z)
    for i in os.listdir("./attachments/"):
        if os.path.isfile("./attachments/"+i) == 1:
            os.remove("./attachments/"+i)
            z = str(time.asctime())+" ./attachments/"+i+" deleted."+"\n"
            with open("log.txt", "a") as f:
                f.write(z)
    return HttpResponseRedirect(reverse('document', args=(document.id,)))

@login_required(login_url='login/')
def delete_document_attachment(request, document_id, documentattachment_id):
    documentattachment = get_object_or_404(DocumentAttachment, pk=documentattachment_id)
    document = get_object_or_404(Document, pk=document_id, created_by=request.user)
    try:
        a = documentattachment.file.name
        fs = FileSystemStorage()
        fs.delete(a)
        z = str(time.asctime())+" ./attachments/"+str(a)+" deleted.\n"
        with open("log.txt", "a") as f:
            f.write(z)
        documentattachment.delete()
    except (KeyError, DocumentAttachment.DoesNotExist):
        context = {'document': document, 'error_message' : _('Unable to delete attachment!'),}
        return render(request, 'document.html', context)
    else:
        return HttpResponseRedirect(reverse('document', args=(document.id,)))
