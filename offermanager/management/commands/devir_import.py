import json
from django.core.management.base import BaseCommand
from django.core import serializers
from django.db import connection

class Command(BaseCommand):
    help = 'Yıl sonu devir verilerini bütünlük kontrollerini es geçerek içeri aktarır.'

    def handle(self, *args, **options):
        self.stdout.write("Veri aktarım işlemi başlatılıyor...")
        
        try:
            with open("devir_verisi.json", "r", encoding="utf-8") as f:
                data = f.read()
            
            if not data.strip():
                self.stdout.write(self.style.ERROR('💥 HATA: "devir_verisi.json" dosyasının içi boş!'))
                return
                
            # Foreign Key / Veritabanı kısıtlamalarını geçici olarak kapatıyoruz
            with connection.constraint_checks_disabled():
                count = 0
                for obj in serializers.deserialize("json", data):
                    obj.save()
                    count += 1
                    
            self.stdout.write(self.style.SUCCESS(f'\n✅ BAŞARILI: {count} adet kayıt yeni veritabanına sorunsuz aktarıldı!'))
            
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('💥 HATA: "devir_verisi.json" dosyası bulunamadı. Önce devir_export komutunu çalıştırın.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'💥 Beklenmedik bir hata oluştu: {str(e)}'))
