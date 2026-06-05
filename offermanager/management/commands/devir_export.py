import json
from django.core.management.base import BaseCommand
from django.core import serializers
from django.contrib.auth.models import User
from offermanager.models import Employee, OfferStock, Customer

class Command(BaseCommand):
    help = 'Kullanıcı, Çalışan, Stok ve Müşteri verilerini JSON formatında dışarı aktarır.'

    def handle(self, *args, **options):
        self.stdout.write("Veritabanından veriler çekiliyor...")
        
        users = list(User.objects.all())
        employees = list(Employee.objects.all())
        offer_stocks = list(OfferStock.objects.all())
        customers = list(Customer.objects.all())
        
        toplam_kayit = len(users) + len(employees) + len(offer_stocks) + len(customers)
        
        self.stdout.write(
            f"Bulunan Kayıtlar:\n"
            f"  - {len(users)} Kullanıcı (auth.user)\n"
            f"  - {len(employees)} Çalışan (Employee)\n"
            f"  - {len(offer_stocks)} Stok (OfferStock)\n"
            f"  - {len(customers)} Müşteri (Customer)"
        )
        
        if toplam_kayit == 0:
            self.stdout.write(self.style.WARNING("💥 Aktarılacak hiç veri bulunamadı!"))
            return

        # Tüm listeleri tek bir fixture dizisinde birleştirip JSON'a çeviriyoruz
        tum_veriler = users + employees + offer_stocks + customers
        data = serializers.serialize("json", tum_veriler, indent=4)
        
        with open("devir_verisi.json", "w", encoding="utf-8") as f:
            f.write(data)
            
        self.stdout.write(self.style.SUCCESS(f'\n✅  BAŞARILI: {toplam_kayit} adet kayıt "devir_verisi.json" dosyasına yazıldı.'))        
