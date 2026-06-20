import json
from pathlib import Path

from django.contrib.auth.models import User
from django.core import serializers
from django.core.management.base import BaseCommand

from offermanager.models import Employee, OfferStock, Customer

class Command(BaseCommand):
    help = 'Kullanıcı, Çalışan, Stok ve Müşteri verilerini JSON formatında dışarı aktarır.'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='devir_verisi.json',
            help='Yüklenecek kaynak JSON dosyası'
        )    

    def handle(self, *args, **options):
        
        girilen_dosya = Path(options['file'])
        
        if girilen_dosya.suffix == '.json':
            dosya_json = girilen_dosya
        else:
            self.stdout.write(self.style.ERROR("💥 Hata: Yalnızca JSON desteklenmektedir!"))
            return          
        
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

        tum_veriler = users + employees + offer_stocks + customers
        data = serializers.serialize("json", tum_veriler, indent=4)
        
        with open(dosya_json, "w", encoding="utf-8") as f:
            f.write(data)
            
        self.stdout.write(self.style.SUCCESS(f'\n✅  BAŞARILI: {toplam_kayit} adet kayıt "devir_verisi.json" dosyasına yazıldı.'))        
