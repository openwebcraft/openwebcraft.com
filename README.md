# openwebcraft.com@owconbsd.openbsd.amsterdam

## Building Blocks

- Git
- OpenBSD
- certbot
- httpd(8)/ httpd.conf(5)
- httpd-plus
- php74 / php74_fpm
- composer
- Kirby

```sh
su -
pkg_add curl
pkg_add unzip
pkg_add git
# Let's Encrypt Certbot
pkg_add certbot
# php-7.4.16
pkg_add php
# /etc/php-7.4.ini
cat /usr/local/share/doc/pkg-readmes/php-7.4

pkg_add php-curl
ln -sf ../php-7.4.sample/curl.ini /etc/php-7.4/

pkg_add php-gd
ln -s /etc/php-7.4.sample/gd.ini /etc/php-7.4/

# /etc/php-fpm.conf
rcctl enable php74_fpm
rcctl start php74_fpm

# composer
pkg_add composer
```

## Setup

### httpd(8)/httpd(5).conf

[/etc/httpd.conf](httpd.conf)

### Certbot (Let's Encrypt)

```sh
doas certbot renew --force-renewal
```

### Composer

```shd
composer install

composer update
```

## Debian 10 (Buster) Dev Environment

### Setup

Install PHP-7.4 along w/ required modules from sury.org:

```sh
sudo apt install -y curl wget gnupg2 ca-certificates lsb-release apt-transport-https
cd ~/Downloads
wget https://packages.sury.org/php/apt.gpg
sudo apt-key add apt.gpg
echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/php7.list
sudo apt update
sudo apt install -y php7.4 php7.4-cli php7.4-common php7.4-curl php7.4-gd php7.4-ctype php7.4-dom
php --version
```

### Usage

```sh
php composer.phar update
php -S localhost:8000 public/index.php
```