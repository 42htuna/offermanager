# offermanager
Python (Django) offer and customer management app

### Requirements
* pip (to install python packages)
* django

### Basic Installation
* This guide assumes Debian/Ubuntu is the running OS. Administrative rights are obtained using **sudo**.
* RPM-based systems should be similar. Windows is theoretically possible but untested.
* The application will be installed to **/opt/offermanager**
* Basic installation will get the application up and running, however it is not suitable for production use.

1. Install pip
```bash
$ sudo apt-get install python3 python3-pip
```

2. Update pip to latest version (using sudo with pip requires the -H flag)
```bash
$ sudo -H pip install --upgrade pip
```

3. Install Django
```bash
$ pip install django
```

4. Download OfferManager from Github repo. Optionally, download the Zip file from https://github.com/42htuna/offermanager/archive/master.zip
```bash
$ git clone https://github.com/42htuna/offermanager --branch master
$ sudo cp -r offermanager /opt
$ cd /opt/offermanager
```

5. Edit the following lines of offermanager/settings.py to match your environment
```python
#  Put a random string at least 50 characters long here. This will keep hashed passwords safe.
SECRET_KEY = 'abcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()<>{}'

# Set to match system time
TIME_ZONE = 'UTC'
```

6. Create the application database
```bash
/opt/offermanager$ sudo python3 manage.py migrate
```

7. Create an admin user
```bash
/opt/offermanager$ sudo python3 manage.py createsuperuser
Username (leave blank to use 'root'): admin
Email address: admin@home.local
Password:
Password (again):
Superuser created successfully.
```

8. At this point, you should have enough configured to run the app using Python's development server. Run the following command and browse to http://localhost:8000
```bash
/opt/offermanager$ sudo python3 manage.py runserver 0.0.0.0:8000
```

9. Setting DEBUG
```settings.py
DEBUG = False
```

Add "--insecure" for access of static files
```bash
/opt/offermanager$ sudo python3 manage.py runserver 0.0.0.0:8000 --insecure
```

10. Setting ALLOWED_HOSTS
```settings.py
ALLOWED_HOSTS = ['127.0.0.1','localhost',]
ALLOWED_HOSTS += ['192.168.1.{}'.format(i) for i in range(256)]
#ALLOWED_HOSTS += ['192.168.{}.{}'.format(i,j) for i in range(256) for j in range(256)]
```

### Using MySQL instead of SQLite3
1. Install MySQL client and Python MySQL driver
```bash
$ sudo apt-get install mariadb-client
$ sudo -H pip install mysqlclient
```

2. Create the MySQL database and user
```bash
$ mysql -u root -p [-h servername]
```
```sql
create database 'offermanager';
grant all on 'offermanager'.* to 'offermanager'@'%' identified by 'mysecretpassword';
exit;
```

4. Update offermanager/settings.py. Find the 'DATABASES' section, comment the sqlite database settings and uncomment the mysql settings.
```python

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

# Use settings below for local sqlite file

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

# Use settings below for MySQL server (requires python-mysql)

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

### Using a production web server
It is highly recommended to use a 'real' web server for running offermanager. This example uses apache, however any wsgi-compatible server will work.

1. Install apache and wsgi module
```bash
$ sudo apt-get install apache2 libapache2-mod-wsgi-py3
$ sudo a2enmod wsgi
```

2. Edit apache config to use wsgi.py included with offermanager and include static and attachments directories
```bash
$ sudo nano /etc/apache2/sites-enabled/000-default.conf
```

```apacheconf
# These lines must be outside of the VirtualHost directive
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

		# The real location of these directories can be moved if desired.
        # Remember to update /opt/offermanager/offermanager/settings.py to reflect changes here.
        Alias /static /opt/offermanager/offermanager/static
</VirtualHost>
```
3. Restart apache and you should be in business!
```bash
$ sudo service apache2 restart
```
