import json
from django.core.management.base import BaseCommand
from django.core import serializers
from offermanager.models import OfferStock, Customer

class Command(BaseCommand):
    help = 'Stok ve Müşteri verilerini JSON formatında dışarı aktarır.'

    def handle(self, *args, **options):
        self.stdout.write("Veritabanından veriler çekiliyor...")
        
        stoklar = list(OfferStock.objects.all())
        musteriler = list(Customer.objects.all())
        
        toplam_kayit = len(stoklar) + len(musteriler)
        self.stdout.write(f"Toplam {len(stoklar)} stok ve {len(musteriler)} müşteri kaydı bulundu.")
        
        if toplam_kayit == 0:
            self.stdout.write(self.style.WARNING("💥 Aktarılacak hiç veri bulunamadı!"))
            return

        # Django serializer ile veriyi güvenli bir şekilde JSON'a çeviriyoruz
        data = serializers.serialize("json", stoklar + musteriler, indent=4)
        
        # Dosyayı UTF-8 olarak güvenli bir şekilde yazıyoruz
        with open("yilsonu_devir.json", "w", encoding="utf-8") as f:
            f.write(data)
            
        self.stdout.write(self.style.SUCCESS(f'✅ BAŞARILI: {toplam_kayit} adet kayıt "yilsonu_devir.json" dosyasına yazıldı.'))
