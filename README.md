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

## Setup

### Packages

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
ln -sf /etc/php-7.4.sample/curl.ini /etc/php-7.4/

pkg_add php-gd
ln -s /etc/php-7.4.sample/gd.ini /etc/php-7.4/

# /etc/php-fpm.conf
rcctl enable php74_fpm
rcctl start php74_fpm

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
git clone --branch kirby git@github.com:openwebcraft/openwebcraft.com.git .
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
doas certbot renew --force-renewal
```

### Composer

```shd
composer install

composer update
```

## PHP-7.4 Linux Dev Env for Debian-based distros (incl. elementary OS 6 Odin)

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
echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/php7.list
sudo apt update
```

#### Ubuntu

```sh
sudo add-apt-repository ppa:ondrej/php -y
```

```sh
# install PHP-7.4 along w/ required modules
sudo apt install -y php7.4 php7.4-cli php7.4-common php7.4-curl php7.4-gd php7.4-ctype php7.4-dom php7.4-mbstring
sudo update-alternatives --set php /usr/bin/php7.4
php --version
```

```sh
# install PHP-8.0 along w/ required modules
sudo apt install -y php8.0 php8.0-cli php8.0-common php8.0-curl php8.0-gd php8.0-ctype php8.0-dom php8.0-mbstring
sudo update-alternatives --set php /usr/bin/php8.0
php --version
```

### Usage

```sh
composer update getkirby/cms
php -S localhost:8000 public/index.php
```