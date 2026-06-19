# 💼 offermanager

Python (Django) teklif ve müşteri yönetim uygulaması

---

## 📦 Gereksinimler

* pip (Python paketlerini yüklemek için)

* django

---

## ⚙️ Temel Kurulum

* Bu kılavuz, işletim sistemi olarak Debian/Ubuntu kullanıldığını varsayar. Yönetici yetkileri **sudo** kullanılarak alınır.

* RPM tabanlı sistemler de benzer olmalıdır. Windows teorik olarak mümkündür ancak test edilmemiştir.

* Uygulama **/opt/offermanager** dizinine kurulacaktır.

* Temel kurulum, uygulamayı çalışır hale getirecektir ancak canlı ortam (production) kullanımı için uygun değildir.


1. pip kurulumunu yapın:

```bash
$ sudo apt-get install python3 python3-pip
```

2. pip'i en son sürüme güncelleyin (pip ile sudo kullanırken -H bayrağı gereklidir):

```bash
$ sudo -H pip install --upgrade pip
```

3. requirements.txt dosyasındaki bağımlılıkları yükleyin:

```bash
$ pip install -r requirements.txt
```

4. OfferManager'ı Github deposundan indirin. İsteğe bağlı olarak, Zip dosyasını https://github.com/42htuna/offermanager/archive/master.zip adresinden de indirebilirsiniz:

```bash
$ git clone https://github.com/42htuna/offermanager --branch master
$ sudo cp -r offermanager /opt
$ cd /opt/offermanager
```

5. Ortamınıza uygun şekilde `offermanager/settings.py` dosyasındaki aşağıdaki satırları düzenleyin:

```python
# Buraya en az 50 karakter uzunluğunda rastgele bir metin girin. Bu, özetlenmiş (hashed) şifreleri güvende tutacaktır.
SECRET_KEY = 'abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()<>{}'

# Sistem saatiyle eşleşecek şekilde ayarlayın
TIME_ZONE = 'UTC'
```

### 🔑 Güvenlik Anahtarı (.env) Yapılandırması

Projenin kök dizininde (**settings.py**'nin görebileceği konumda) bir **.env** dosyası oluşturun. Terminalde taze bir anahtar üretip bu dosyaya ekleyin:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

```plaintext
# .env dosyasının içeriği
DJANGO_SECRET_KEY=urettiginiz_gizli_anahtar
```

settings.py dosyanızın içini ise bu dosyadan okuyacak şekilde değiştirirsiniz (örneğin django-environ veya python-dotenv kütüphanesi kullanarak):

```python
# settings.py içi
import os
from dotenv import load_dotenv

load_dotenv() # .env dosyasını yükler
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
```
**Özetle:** **SECRET_KEY** aslında **settings.py** içinde bir koddur. Ama en doğru pratik, onu settings.py yanındaki bir **.env** dosyasında gizlemektir.

6. Uygulama veritabanını oluşturun:

```bash
python manage.py makemigrations offermanager
```

```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

7. Bir yönetici (admin) kullanıcısı oluşturun:

```bash
python manage.py createsuperuser
```

```text
Username (leave blank to use 'root'): admin
Email address: admin@home.local
Password:
Password (again):
Superuser created successfully.
```

8. Bu aşamada, uygulamayı Python'un geliştirme sunucusuyla çalıştırmak için yeterli yapılandırmaya sahip olmalısınız. Aşağıdaki komutu çalıştırın ve tarayıcınızdan http://localhost:8000 adresine gidin:

```bash
python manage.py runserver 0.0.0.0:8000
```

9. DEBUG Ayarı:

```settings.py
DEBUG = False
```

Statik dosyalara erişebilmek için "--insecure" parametresini ekleyin:

```bash
python manage.py runserver 0.0.0.0:8000 --insecure
```

Gunicorn ile çalıştırmak için:

```bash
python manage.py collectstatic --noinput
```

```bash
gunicorn offermanager.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 90
```

Waitress ile çalıştırmak için (Windows için en iyi alternatif):

```bash
python manage.py collectstatic --noinput
```

```bash
waitress-serve --port=8000 --threads=16 --connection-limit=200 offermanager.wsgi:application
```

10. ALLOWED_HOSTS Ayarı:

```settings.py
ALLOWED_HOSTS = ['127.0.0.1','localhost',]
ALLOWED_HOSTS += ['192.168.1.{}'.format(i) for i in range(256)]
#ALLOWED_HOSTS += ['192.168.{}.{}'.format(i,j) for i in range(256) for j in range(256)]
```

---

### 🗄️ SQLite3 Yerine MySQL Kullanımı

1. MySQL istemcisini ve Python MySQL sürücüsünü yükleyin:

```bash
$ sudo apt-get install mariadb-client
$ sudo -H pip install mysqlclient
```

2. MySQL veritabanını ve kullanıcısını oluşturun:

```bash
$ mysql -u root -p [-h servername]
```

```sql
create database 'offermanager';
grant all on 'offermanager'.* to 'offermanager'@'%' identified by 'mysecretpassword';
exit;
```

4. `offermanager/settings.py` dosyasını güncelleyin. 'DATABASES' bölümünü bulun, sqlite veritabanı ayarlarını yorum satırı yapın ve mysql ayarlarının yorum işaretlerini kaldırın:

```python
# Veritabanı
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# Yerel sqlite dosyası için aşağıdaki ayarları kullanın

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#         'USER': '',
#         'PASSWORD': '',
#         'HOST': '',
#         'PORT': '',
#     }
# }

# MySQL sunucusu için aşağıdaki ayarları kullanın (python-mysql gerektirir)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'offermanager',
        'USER': 'offermanager',
        'PASSWORD': 'mysecretpassword',
        'HOST': 'servername',
        'PORT': '',
    }
}
```

---

###  🌐 Canlı Ortam (Production) Web Sunucusu Kullanımı

offermanager'ı çalıştırmak için "gerçek" bir web sunucusu kullanmanız şiddetle tavsiye edilir. Bu örnekte Apache kullanılmaktadır ancak WSGI uyumlu herhangi bir sunucu da işinizi görecektir.

1. Apache ve WSGI modülünü yükleyin:

```bash
$ sudo apt-get install apache2 libapache2-mod-wsgi-py3
$ sudo a2enmod wsgi
```

2. Apache yapılandırmasını, offermanager ile birlikte gelen `wsgi.py` dosyasını kullanacak ve statik ile ek (attachments) dizinlerini dahil edecek şekilde düzenleyin:

```bash
$ sudo nano /etc/apache2/sites-enabled/000-default.conf
```

```apacheconf
# Bu satırlar VirtualHost direktifinin dışında olmalıdır
WSGIScriptAlias / /opt/offermanager/offermanager/wsgi.py
WSGIPythonPath /opt/offermanager

<VirtualHost *:80>
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined

        <Directory /opt/offermanager>
                Options Indexes MultiViews FollowSymLinks
                Require all granted
        </Directory>

        <Directory /opt/offermanager/offermanager>
                <Files wsgi.py>
                        Require all granted
                </Files>
        </Directory>

		# Bu dizinlerin gerçek konumu istenirse değiştirilebilir.
        # Buradaki değişiklikleri yansıtmak için /opt/offermanager/offermanager/settings.py dosyasını güncellemeyi unutmayın.
        Alias /static /opt/offermanager/offermanager/static
</VirtualHost>
```

3. Apache'yi yeniden başlattığınızda sisteminiz hazır olacaktır!

```bash
$ sudo service apache2 restart
```

---

## 🔄 Yıl Sonu Devir İşlemleri (Veri Aktarımı)

Mevcut sistemdeki **Kullanıcı**, **Çalışan**, **Stok** ve **Müşteri** tablolarını, projenin temel yapısını bozmadan yeni veritabanına aktarmak için aşağıdaki iki yöntemden biri kullanılabilir.

---

### ⭐ Yöntem A : Yerleşik Django Fixtures (Hızlı / Kodsuz Yöntem)

Herhangi bir kod değişikliği yapmadan, tamamen Django'nun yerleşik **`dumpdata`** ve **`loaddata`** mekanizmasını kullanan pratik yöntemdir.

#### 1. Verileri dışarı aktarma (Eski/Dolu Veritabanında)

Eski veritabanınız aktifken terminalde aşağıdaki komutu çalıştırarak stok ve müşteri verilerini JSON formatında yedekleyin.

```bash
python manage.py dumpdata auth.user offermanager.employee offermanager.OfferStock offermanager.Customer --indent 4 -o devir_verisi.json
```

#### 2. Verileri içe aktarma (Yeni/Boş Veritabanında)

Yeni veritabanına geçiş yapıp "python manage.py migrate" çalıştırdıktan sonra verileri doğrudan içeri yükleyin.

```bash
python manage.py loaddata devir_verisi.json
```

---

### ⭐ Yöntem B : Özel Yönetim Komutları

Proje içine gömülü, veritabanı kısıtlamalarını (Foreign Key denetimlerini) geçici olarak bypass ederek verileri esnek bir şekilde içeri basan yöntemdir.

#### 1. Verileri dışarı aktarma (Eski/Dolu Veritabanında)

Terminalde tek bir komutla ilgili tabloları **devir_verisi.json** adıyla dışarı aktarın.

```bash
python manage.py devir_export
```

#### 2. Verileri içe aktarma (Yeni/Boş Veritabanında)

Yeni veritabanına geçip migrate işlemlerini tamamladıktan sonra verileri direkt içeri basmak için:

```bash
python manage.py devir_import
```

---

## 💾 Django dumpdata ve loaddata ile yedekleme (backup.bat/backup.sh)

Verileri Windows ortamından, Linux ortamına aktarırken Türkçe karakterlerin bozulmaması için **-Xutf8** parametresi ile **UTF8** karakter kodlaması seçilmelidir.

Boş veritabanına geri yükleme yaparken, veri çakışmalarını ve hataları önlemek için de **--exclude** parametresi ile **contenttypes** ve **auth.Permission** tabloları hariç tutulmalıdır.

### Windows ortamında

```bash
python -Xutf8 manage.py dumpdata --exclude contenttypes --exclude auth.Permission --format json --indent 4 -o database_backup.json
```

```bash
.\backup.bat
```
### Linux ortamında

```bash
python manage.py dumpdata --exclude contenttypes --exclude auth.Permission --indent 4 -o database_backup.json
```

```bash
bash backup.sh
```
---

### Geri yükleme

```bash
python manage.py loaddata database_backup.json
```

---

## 🔭 Proje Görünümü

![Proje Görünümü](https://github.com/42htuna/offermanager/blob/master/offermanager/static/images/offer.png)
