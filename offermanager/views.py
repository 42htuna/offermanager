from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from itertools import chain
import datetime, time, os
from django.utils.translation import ugettext_lazy as _
from offermanager.models import Customer, Offer, OfferItem, Document, DocumentAttachment

# Create your views here.

# Administrative settings
def users(request):
    return None

# User login
def login_view(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if (user is not None):
			login(request, user)
			return HttpResponseRedirect(reverse('index'))
		else:
			context = {'error_message' : _('Unable to login! Please check username and password then try again.'),}
			return render(request, 'login.html', context)
	else:
		return render(request, 'login.html')

# User logout
def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')

# List all customers
@login_required(login_url='login/')
def customer_list(request):
	customers = Customer.objects.filter()
	context = {'title' : _('Customer List'), 'customers' : customers,}
	return render(request, 'customers.html', context)

# Show specific customer details
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

# Add new customer
@login_required(login_url='login/')
def new_customer(request):
    if request.method == 'POST':
        c = Customer(name=request.POST['name'],
                     address=request.POST['address'],
                     phone=request.POST['phone'],
                     email=request.POST['email'],
                     created_by=request.user,
                     updated_by=request.user)
        c.save()
        if 'savecreate' in request.POST:
            i = Offer(customer=c,
                      created_by=request.user,
                      updated_by=request.user)
            i.save()
            return HttpResponseRedirect(reverse('offer', args=(i.id,)))
        elif 'savecreate_doc' in request.POST:
            i = Document(customer=c,
                         created_by=request.user,
                         updated_by=request.user)
            i.save()
            return HttpResponseRedirect(reverse('document', args=(i.id,)))
        else:
            return HttpResponseRedirect(reverse('customer_list'))
    else:
	       return render(request, 'new_customer.html')

# Update customer
@login_required(login_url='login/')
def update_customer(request, customer_id):
    c = get_object_or_404(Customer, pk=customer_id)
    c.name = request.POST['name']
    c.address = request.POST['address']
    c.phone = request.POST['phone']
    c.email = request.POST['email']
    c.updated_by = request.user
    c.save()
    return HttpResponseRedirect(reverse('customer', args=(c.id,)))

# Delete customer
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

# Default offer list, show 25 recent offers
@login_required(login_url='login/')
def index(request):
    offers = Offer.objects.filter(created_by=request.user, active=1).order_by('-date')[:25]
    context = {'title' : _('Recent Offers'), 'offer_list' : offers,}
    return render(request, 'index.html', context)

# Show big list of all offers
@login_required(login_url='login/')
def all_offers(request):
    offers = Offer.objects.filter(created_by=request.user, active=1).order_by('-date')
    context = {'title' : _('All Offers'), 'offer_list' : offers,}
    return render(request, 'index.html', context)

# Show draft offers
@login_required(login_url='login/')
def draft_offers(request):
    offers = Offer.objects.filter(created_by=request.user, active=1, status='0').order_by('-date')
    context = {'title' : _('Draft Offers'), 'offer_list' : offers,}
    return render(request, 'index.html', context)

# Show approved offers
@login_required(login_url='login/')
def approved_offers(request):
    offers = Offer.objects.filter(created_by=request.user, active=1, status='1').order_by('-date')
    context = {'title' : _('Approved Offers'), 'offer_list' : offers,}
    return render(request, 'index.html', context)

# Show unapproved offers
@login_required(login_url='login/')
def unapproved_offers(request):
    offers = Offer.objects.filter(created_by=request.user, active=1, status='2').order_by('-date')
    context = {'title' : _('Unapproved Offers'), 'offer_list' : offers,}
    return render(request, 'index.html', context)

# Show cancel offers
@login_required(login_url='login/')
def canceled_offers(request):
    offers = Offer.objects.filter(created_by=request.user, active=1, status='3').order_by('-date')
    context = {'title' : _('Canceled Offers'), 'offer_list' : offers,}
    return render(request, 'index.html', context)

# Display a specific offer
@login_required(login_url='login/')
def offer(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id, created_by=request.user, active=1)
    context = {'title' : _('Offer ') + str(offer_id), 'offer' : offer,}
    return render(request, 'offer.html', context)

# Search for offer
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

# Create new offer
@login_required(login_url='login/')
def new_offer(request):
	# If no customer_id is defined, create a new offer
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
			i = Offer(customer=customer,
                      created_by=request.user,
                      updated_by = request.user)
			i.save()
			return HttpResponseRedirect(reverse('offer', args=(i.id,)))
	else:
		# Customer list needed to populate select field
		customers = Customer.objects.order_by('name')
		context = {'title' : _('New Offer'), 'customer_list' : customers,}
		return render(request, 'new_offer.html', context)

# Update offer
@login_required(login_url='login/')
def update_offer(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id, created_by=request.user, active=1)
    try:
        offer.date = datetime.datetime.strptime(request.POST['date'], "%d/%m/%Y")
        offer.status = request.POST['status']
        offer.terms = request.POST['terms']
        offer.save()
    except (KeyError, Offer.DoesNotExist):
        return render(request, 'offer.html', {'offer': offer, 'error_message': _('Unable to update offer!'),})
    else:
        context = {'confirm_update' : True, 'title' : _('Offer ') + str(offer_id), 'offer' : offer,}
        return render(request, 'offer.html', context)

# Delete an offer
@login_required(login_url='login/')
def delete_offer(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id, created_by=request.user, active=1)
    offer.delete()
    return HttpResponseRedirect(reverse('index'))

# Passive Offer
@login_required(login_url='login/')
def passive_offer(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id, created_by=request.user, active=1)
    offer.active = False
    offer.save()
    return HttpResponseRedirect(reverse('index'))

# Print offer
@login_required(login_url='login/')
def print_offer(request, offer_id):
    offer = get_object_or_404(Offer, pk=offer_id, created_by=request.user, active=1)
    context = {'title' : _('Offer ') + str(offer_id), 'offer' : offer,}
    return render(request, 'print_offer.html', context)

# Add offeritem to offer
@login_required(login_url='login/')
def add_item(request, offer_id):
	offer = get_object_or_404(Offer, pk=offer_id)
	try:
		i = offer.offeritem_set.create(type=request.POST['type'],
                                       qty=request.POST['qty'],
                                       unit=request.POST['unit'],
                                       cost=request.POST['cost'],
                                       tax=request.POST['tax'],)
		i.save()
	except (KeyError, Offer.DoesNotExist):
		context = {'offer': offer, 'error_message': _('Not all fields were completed.'),}
		return render(request, 'offer.html', context)
	else:
		return HttpResponseRedirect(reverse('offer', args=(offer.id,)))

# Delete offeritem from offer
@login_required(login_url='login/')
def delete_item(request, offeritem_id, offer_id):
	item = get_object_or_404(OfferItem, pk=offeritem_id)
	offer = get_object_or_404(Offer, pk=offer_id)
	try:
		item.delete()
	except (KeyError, OfferItem.DoesNotExist):
		context = {'offer': offer, 'error_message': _('Item does not exist.'),}
		return render(request, 'offer.html', context)
	else:
		return HttpResponseRedirect(reverse('offer', args=(offer.id,)))

# Accounting report
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
			# Sum of all approved offers
			offertotal = 0
			for i in approvedoffers:
				if i.active == True:
					offertotal += i.total_()
			context = {'start' : start, 'end' : end, 'offers' : approvedoffers, 'offertotal' : "{:,}".format(offertotal),}
			return render(request, 'accounting.html', context)
	else:
		return render(request, 'accounting.html')

# Default document list, show 25 recent documents
@login_required(login_url='login/')
def recent_documents(request):
    documents = Document.objects.filter(created_by=request.user).order_by('-date')[:25]
    context = {'title' : _('Recent Documents'), 'document_list' : documents,}
    return render(request, 'documents.html', context)

# Show big list of all documents
@login_required(login_url='login/')
def all_documents(request):
    documents = Document.objects.filter(created_by=request.user).order_by('-date')
    context = {'title' : _('All Documents'), 'document_list' : documents,}
    return render(request, 'documents.html', context)

# Show cheques
@login_required(login_url='login/')
def cheques(request):
    documents = Document.objects.filter(created_by=request.user, documenttype='0').order_by('-date')
    context = {'title' : _('Cheques'), 'document_list' : documents,}
    return render(request, 'documents.html', context)

# Show bonds
@login_required(login_url='login/')
def bonds(request):
    documents = Document.objects.filter(created_by=request.user, documenttype='1').order_by('-date')
    context = {'title' : _('Bonds'), 'document_list' : documents,}
    return render(request, 'documents.html', context)

# Show receipts
@login_required(login_url='login/')
def receipts(request):
    documents = Document.objects.filter(created_by=request.user, documenttype='2').order_by('-date')
    context = {'title' : _('Receipts'), 'document_list' : documents,}
    return render(request, 'documents.html', context)

# Show others
@login_required(login_url='login/')
def others(request):
    documents = Document.objects.filter(created_by=request.user, documenttype='3').order_by('-date')
    context = {'title' : _('Others'), 'document_list' : documents,}
    return render(request, 'documents.html', context)

# Display a specific document
@login_required(login_url='login/')
def document(request, document_id):
    document = get_object_or_404(Document, pk=document_id, created_by=request.user)
    context = {'title' : _('Document ') + str(document_id), 'document' : document,}
    return render(request, 'document.html', context)

# Create new document
@login_required(login_url='login/')
def new_document(request):
	# If no customer_id is defined, create a new document
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
		# Customer list needed to populate select field
		customers = Customer.objects.order_by('name')
		context = {'title' : _('New Document'), 'customer_list' : customers,}
		return render(request, 'new_document.html', context)

# Update document
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

# Delete an document
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

# Upload attachment for document
@login_required(login_url='login/')
def upload_document_attachment(request, document_id):
    myfile = request.FILES['file']
    document = get_object_or_404(Document, pk=document_id)
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

# Delete attachment from document
@login_required(login_url='login/')
def delete_document_attachment(request, document_id, documentattachment_id):
    documentattachment = get_object_or_404(DocumentAttachment, pk=documentattachment_id)
    document = get_object_or_404(Document, pk=document_id)
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
