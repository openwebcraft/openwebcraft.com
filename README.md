# openwebcraft.com@owconbsd.openbsd.amsterdam

## Building Blocks

- Git
- OpenBSD
- certbot
- httpd(8)/ httpd.conf(5)
- httpd-plus
- php81 / php81_fpm
- composer
- Kirby

## Setup

### Packages

```sh
su -
pkg_add curl
pkg_add unzip
pkg_add git
# Let's Encrypt Certbot
pkg_add py3-setuptools
pkg_add certbot
# php-8.1.18
pkg_add php
# /etc/php-8.1.ini
cat /usr/local/share/doc/pkg-readmes/php-8.1

pkg_add php-curl
ln -sf /etc/php-8.1.sample/curl.ini /etc/php-8.1/

pkg_add php-gd
ln -s /etc/php-8.1.sample/gd.ini /etc/php-8.1/

# /etc/php-fpm.conf
rcctl enable php81_fpm
rcctl start php81_fpm

# composer
pkg_add composer
```

### Git Repo

Prerequisite: create ssh key on server and ad as "Deploy key" to GitHub repo.

```sh
cd /var/www/htdocs
doas mkdir openwebcraft.com
cd openwebcraft.com
doas chown -R www:www .
doas chmod -R g+w .
doas -G www matthias
# logout/ login
git clone --branch kirbyobsd git@github.com:openwebcraft/openwebcraft.com.git .
composer install
```

### httpd(8)/httpd(5).conf

[/etc/httpd.conf](httpd.conf)

```sh
doas vi /etc/httpd.conf
doas httpd -n
doas rcctl reload httpd
doas rcctl restart httpd
```

### Certbot (Let's Encrypt)

```sh
doas certbot certonly \
  --agree-tos \
  --webroot \
  -w /var/www/htdocs/openwebcraft.com/static \
  -m <email> \
  -d openwebcraft.com,www.openwebcraft.com

# doas certbot renew --force-renewal
```

### HTTP Basic Authentication

```sh
doas mkdir -p /var/www/auth/openwebcraft.com
doas htpasswd /var/www/auth/openwebcraft.com/.htpasswd <username>
doas chown www: /var/www/auth/openwebcraft.com/.htpasswd
doas chmod u-w /var/www/auth/openwebcraft.com/.htpasswd
```

### Chroot

```sh
doas mkdir -p /var/www/etc
doas cp /etc/hosts /etc/resolv.conf /var/www/etc
ln -s /usr/share/zoneinfo/Europe/Berlin /var/www/etc/localtime

doas mkdir -p /var/www/bin
doas cp /bin/sh /var/www/bin
```

### Composer

```shd
composer install

composer update
```

## PHP-8.1 Linux Dev Env for Debian-based distros (incl. elementary OS 6 Odin)

Prerequisite: [Composer](https://getcomposer.org/) installed.

### Setup

#### Debian

```sh
# common package dependencies
sudo apt install -y curl wget gnupg2 ca-certificates lsb-release apt-transport-https

# pre-setup on Debian 10 (Buster)
cd ~/Downloads
wget https://packages.sury.org/php/apt.gpg
sudo apt-key add apt.gpg
echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/php8.list
sudo apt update
```

#### Ubuntu

```sh
sudo add-apt-repository ppa:ondrej/php -y
```

```sh
# install PHP-8.1 along w/ required modules
sudo apt install -y php8.1 php8.1-cli php8.1-common php8.1-curl php8.1-gd php8.1-ctype php8.1-dom php8.1-mbstring
sudo update-alternatives --set php /usr/bin/php8.1
php --version
```

### Usage

```sh
php -S localhost:8000 kirby/router.php
```


```sh
cd static/
python3 -m http.server 8000
```

## Resources

- [Installing Wordpress on OpenBSD](https://openbsd.amsterdam/blog/wordpress.html)