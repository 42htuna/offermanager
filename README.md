# offermanager
Python (Django) teklif ve müşteri yönetim uygulaması[cite: 1]

### Gereksinimler
* pip (Python paketlerini yüklemek için)[cite: 1]
* django[cite: 1]

### Temel Kurulum
* Bu kılavuz, işletim sistemi olarak Debian/Ubuntu kullanıldığını varsayar. Yönetici yetkileri **sudo** kullanılarak alınır.[cite: 1]
* RPM tabanlı sistemler de benzer olmalıdır. Windows teorik olarak mümkündür ancak test edilmemiştir.[cite: 1]
* Uygulama **/opt/offermanager** dizinine kurulacaktır.[cite: 1]
* Temel kurulum, uygulamayı çalışır hale getirecektir ancak canlı ortam (production) kullanımı için uygun değildir.[cite: 1]

1. pip kurulumunu yapın:
```bash
$ sudo apt-get install python3 python3-pip
```[cite: 1]

2. pip'i en son sürüme güncelleyin (pip ile sudo kullanırken -H bayrağı gereklidir):
```bash
$ sudo -H pip install --upgrade pip
```[cite: 1]

3. requirements.txt dosyasındaki bağımlılıkları yükleyin:
```bash
$ pip install -r requirements.txt
```[cite: 1]

4. OfferManager'ı Github deposundan indirin. İsteğe bağlı olarak, Zip dosyasını https://github.com/42htuna/offermanager/archive/master.zip adresinden de indirebilirsiniz:
```bash
$ git clone [https://github.com/42htuna/offermanager](https://github.com/42htuna/offermanager) --branch master
$ sudo cp -r offermanager /opt
$ cd /opt/offermanager
```[cite: 1]

5. Ortamınıza uygun şekilde `offermanager/settings.py` dosyasındaki aşağıdaki satırları düzenleyin:
```python
# Buraya en az 50 karakter uzunluğunda rastgele bir metin girin. Bu, özetlenmiş (hashed) şifreleri güvende tutacaktır.
SECRET_KEY = 'abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()<>{}'

# Sistem saatiyle eşleşecek şekilde ayarlayın
TIME_ZONE = 'UTC'
```[cite: 1]

6. Uygulama veritabanını oluşturun:
```bash
python manage.py makemigrations offermanager
```[cite: 1]

```bash
python manage.py makemigrations
```[cite: 1]

```bash
python manage.py migrate
```[cite: 1]

7. Bir yönetici (admin) kullanıcısı oluşturun:
```bash
python manage.py createsuperuser
Username (leave blank to use 'root'): admin
Email address: admin@home.local
Password:
Password (again):
Superuser created successfully.
```[cite: 1]

8. Bu aşamada, uygulamayı Python'un geliştirme sunucusuyla çalıştırmak için yeterli yapılandırmaya sahip olmalısınız. Aşağıdaki komutu çalıştırın ve tarayıcınızdan http://localhost:8000 adresine gidin:
```bash
python manage.py runserver 0.0.0.0:8000
```[cite: 1]

9. DEBUG Ayarı:
```settings.py
DEBUG = False
```[cite: 1]

Statik dosyalara erişebilmek için "--insecure" parametresini ekleyin:
```bash
python manage.py runserver 0.0.0.0:8000 --insecure
```[cite: 1]

Gunicorn ile çalıştırmak için:
```bash
python manage.py collectstatic --noinput
```[cite: 1]

```bash
gunicorn offermanager.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 90
```[cite: 1]

Waitress ile çalıştırmak için:
```bash
python manage.py collectstatic --noinput
```[cite: 1]

```bash
waitress-serve --port=8000 offermanager.wsgi:application
```[cite: 1]

10. ALLOWED_HOSTS Ayarı:
```settings.py
ALLOWED_HOSTS = ['127.0.0.1','localhost',]
ALLOWED_HOSTS += ['192.168.1.{}'.format(i) for i in range(256)]
#ALLOWED_HOSTS += ['192.168.{}.{}'.format(i,j) for i in range(256) for j in range(256)]
```[cite: 1]

### SQLite3 Yerine MySQL Kullanımı
1. MySQL istemcisini ve Python MySQL sürücüsünü yükleyin:
```bash
$ sudo apt-get install mariadb-client
$ sudo -H pip install mysqlclient
```[cite: 1]

2. MySQL veritabanını ve kullanıcısını oluşturun:
```bash
$ mysql -u root -p [-h servername]
```[cite: 1]

```sql
create database 'offermanager';
grant all on 'offermanager'.* to 'offermanager'@'%' identified by 'mysecretpassword';
exit;
```[cite: 1]

4. `offermanager/settings.py` dosyasını güncelleyin. 'DATABASES' bölümünü bulun, sqlite veritabanı ayarlarını yorum satırı yapın ve mysql ayarlarının yorum işaretlerini kaldırın:
```python
# Veritabanı
# [https://docs.djangoproject.com/en/1.10/ref/settings/#databases](https://docs.djangoproject.com/en/1.10/ref/settings/#databases)

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
```[cite: 1]

### Canlı Ortam (Production) Web Sunucusu Kullanımı
offermanager'ı çalıştırmak için "gerçek" bir web sunucusu kullanmanız şiddetle tavsiye edilir. Bu örnekte Apache kullanılmaktadır ancak WSGI uyumlu herhangi bir sunucu da işinizi görecektir.[cite: 1]

1. Apache ve WSGI modülünü yükleyin:
```bash
$ sudo apt-get install apache2 libapache2-mod-wsgi-py3
$ sudo a2enmod wsgi
```[cite: 1]

2. Apache yapılandırmasını, offermanager ile birlikte gelen `wsgi.py` dosyasını kullanacak ve statik ile ek (attachments) dizinlerini dahil edecek şekilde düzenleyin:
```bash
$ sudo nano /etc/apache2/sites-enabled/000-default.conf
```[cite: 1]

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
```[cite: 1]

3. Apache'yi yeniden başlattığınızda sisteminiz hazır olacaktır!
```bash
$ sudo service apache2 restart
```[cite: 1]

---

## 🔄 Yıl Sonu Devir İşlemleri (Veri Aktarımı)

Mevcut sistemdeki **Kullanıcı**, **Çalışan**, **Stok** ve **Müşteri** tablolarını, projenin temel yapısını bozmadan yeni veritabanına aktarmak için aşağıdaki iki yöntemden biri kullanılabilir.[cite: 1]

---

### Yöntem 1: Yerleşik Django Fixtures (Hızlı / Kodsuz Yöntem)

Herhangi bir kod değişikliği yapmadan, tamamen Django'nun yerleşik `dumpdata` ve `loaddata` mekanizmasını kullanan pratik yöntemdir.[cite: 1]

#### 1. Verileri Dışarı Aktarma (Eski/Dolu Veritabanında)
Eski veritabanınız aktifken terminalde aşağıdaki komutu çalıştırarak stok ve müşteri verilerini JSON formatında yedekleyin:

```bash
python manage.py dumpdata auth.user offermanager.employee offermanager.OfferStock offermanager.Customer --indent 4 -o devir_verisi.json
```[cite: 1]

#### 2. Verileri İçe Aktarma (Yeni/Boş Veritabanında)
Yeni veritabanına geçiş yapıp "python manage.py migrate" çalıştırdıktan sonra verileri doğrudan içeri yükleyin:

```bash
python manage.py loaddata devir_verisi.json
```[cite: 1]

---

### Yöntem 2: Özel Yönetim Komutları (Custom Management Commands)
Proje içine gömülü, veritabanı kısıtlamalarını (Foreign Key denetimlerini) geçici olarak bypass ederek verileri esnek bir şekilde içeri basan yöntemdir.[cite: 1]

#### Eski Veritabanında Dışa Aktarma:
Terminalde tek bir komutla ilgili tabloları **devir_verisi.json** adıyla dışarı aktarın:

```bash
python manage.py devir_export
```[cite: 1]

#### Yeni Veritabanında İçe Aktarma:
Yeni veritabanına geçip migrate işlemlerini tamamladıktan sonra verileri direkt içeri basmak için:

```bash
python manage.py devir_import
```[cite: 1]

---

## 🔄 Django dumpdata ve loaddata ile yedekleme (backup.bat/backup.sh):

Verileri Windows ortamından, Linux ortamına aktarırken Türkçe karakterlerin bozulmaması için **-Xutf8** parametresi ile **UTF8** karakter kodlaması seçilmelidir.[cite: 1]

Boş veritabanına geri yükleme yaparken, veri çakışmalarını ve hataları önlemek için de **--exclude** parametresi ile **contenttypes** ve **auth.Permission** tabloları hariç tutulmalıdır.[cite: 1]

### Windows ortamında:

```bash
python -Xutf8 manage.py dumpdata --exclude contenttypes --exclude auth.Permission --format json --indent 4 -o database_backup.json
```[cite: 1]

```bash
.\backup.bat
```[cite: 1]

### Linux ortamında:

```bash
python manage.py dumpdata --exclude contenttypes --exclude auth.Permission --indent 4 -o database_backup.json
```[cite: 1]

```bash
bash backup.sh
```[cite: 1]

---

### Geri yükleme:

```bash
python manage.py loaddata database_backup.json
```[cite: 1]
---
