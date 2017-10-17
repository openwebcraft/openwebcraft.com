---
title: "Clear Linux Desktop Setup"
featured_image: "/img/clearlinux_logo_wire.jpg"
date: 2017-09-21T23:00:12+02:00
tags: 
- clearlinux
- clr
- linux
- gnome
draft: false
---

How I've set up my Clear Linux (GNOME) desktop environment…

<!--more-->

## Clear Linux Installation

**TL;DR** By simply following [the Clear Linux Getting-Started guide](https://clearlinux.org/documentation/clear-linux/getting-started/bare-metal-install/bare-metal-install.html) the installation experience is quite polished and overall pretty straight forward!

- Remember booting w/ Ethernet (LAN) cable attached.
- Choose  "Custom installation option..." whenever possible. This is especially important when aiming for desktop use! Do **NOT** use *Automatic installation of Clear Linux OS latest*, but actually continue w/ custom options… ALWAYS.
- For keyboard selection choose `de-latin1-nodeadkeys`.
- For network requirements *Set static IP configuration*.

Basic System Tweaking:

```bash
mkdir ~/code
mkdir ~/.bashrc.d 
chmod 700 ~/.bashrc.d
mkdir -p ~/.local/share/gnome-shell/extensions
sudo mkdir -p /usr/local/bin
sudo mkdir -p /usr/local/lib
sudo mkdir -p /opt
sudo systemctl start sshd
sudo systemctl enable sshd
```

In order to use `~/.bashrc.d` directory instead of bloated `.bashrc` one needs to add this to `.bashrc`:

```bash
for file in ~/.bashrc.d/*.bashrc;
do
	source "$file"
done
```
Then, when creating individual files inside the `~/.bashrc.d`, e.g. `golang.bashrc`, one needs to remeber to give them execution rights:

```bash
chmod +x ~/.bashrc.d/*.bashrc
```

Increase limit for *inotify* watches:

```bash
cat /proc/sys/fs/inotify/max_user_watches
echo fs.inotify.max_user_watches=32768 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

For sanity w/ additional binaries it helps creating a file `/etc/system-release` w/ contents: `Clear Linux OS for Intel Architecture`.

## System settings and "Pimping the bash"

Adjust time and locale simply via GNOME settings…

Adjust keyboard keymap:

- globally (ie. for shell) via `sudo localectl set-keymap de-latin1-nodeadkeys` — likely already set by installer
- for desktop simply via GNOME settings…

Install a minimal but [informative and fancy bash prompt for Git users](https://github.com/magicmonty/bash-git-prompt):

```bash
cd ~
git clone https://github.com/magicmonty/bash-git-prompt.git .bash-git-prompt --depth=1
```

Then, add to the `~/.bashrc`:

```bash
GIT_PROMPT_ONLY_IN_REPO=1
source ~/.bash-git-prompt/gitprompt.sh
```

Test:

```bash
cd ~/.bash-git-prompt/
✔ ~/.bash-git-prompt [master|✔] 
19:36 $ 
```

### Fonts

Install [FIRA CODE](https://github.com/tonsky/FiraCode) font by download latest version and extracting/ copying contents of `ttf` folder to `~/.fonts` followed by `fc-cache -fv`.

### gtop

A awesome [system monitoring dashboard for terminal](https://github.com/aksakalli/gtop).

equired bundles:

- `nodejs-basic`

```
sudo npm install gtop -g
```

### current

Install [current-cli](https://github.com/stve/current-cli/blob/master/README.md) to see what language versions are configured in your current environment (`npm i -g current-cli`)

## Software Installation

For sanity (we always want `sudo swupd verify --fix` to succeed!) we're only using either software available in [Clear Linux bundles](https://github.com/clearlinux/clr-bundles/tree/master/bundles) or binaries distributed as `.tar.gz`w/ requirements that can be resolved from Clear Linux bundles.

### Software Development Essentials (ie. `*-basics`)

`sudo swupd bundle-add nodejs-basic go-basic java-basic php-basic containers-basic R-basic R-extras`

### Simplenote

Beloved (syncing) note app of choice. :-)

Download `.tar.gz` from here <https://simplenote.com/> and extract to `/opt/simplenote`.

Create symlink: `sudo ln -s /opt/simplenote/Simplenote /usr/local/bin/simplenote`

Add icon to GNOME like so: `gnome-desktop-item-edit ~/.local/share/applications/ --create-new`:

```bash
[…]
Icon[en_US]=/opt/simplenote/Simplenote.png
Name[en_US]=Simplenote
Exec=simplenote
Name=Simplenote
Icon=/opt/simplenote/Simplenote.png
```

### Docker

Required bundles:

- `containers-basic`

One needs to add her/ his user to group `docker` like so: `sudo usermod -G docker -a matthias` and re-login.

### Docker Compose

```bash
sudo -i
curl -L https://github.com/docker/compose/releases/download/1.16.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
exit
docker-compose -version
```

### Scaleway

My cloud provider of choice!

Required bundles:

- `go-basic`

Add to the `~/.bashrc`:

```bash
export GOPATH=~/go
export PATH=$PATH:$GOPATH/bin
```

Then install [Scaleway CLI](https://github.com/scaleway/scaleway-cli): 

```bash
GO15VENDOREXPERIMENT=1 go get -u github.com/scaleway/scaleway-cli/cmd/scw
```

### Visual Studio Code

Preferred coding editor.

Required bundles:

- `games` (required for `libgconf-2`)

Download `.tar.gz` for Linux x64 from <https://code.visualstudio.com/> and extract to `~/opt/vscode`.

Create symlink: `sudo ln -s /opt/vscode/code /usr/local/bin/code`

Add icon to GNOME like so:q: `gnome-desktop-item-edit ~/.local/share/applications/ --create-new`:

```bash
[…]
Icon[en_US]=code
Name[en_US]=VSCode
Exec=code
Name=VS Code
Icon=code
```

### GitKraken

Required bundles:

- `desktop-dev` (required for `libgnome-keyring`)

Add to the `~/.bashrc`:

```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lo
```

... and create symlink to workaround (hack) missing libraries: `sudo ln -s /lib64/libcurl.so.4 /usr/local/lib/libcurl-gnutls.so.4`

Then, download `.zip` from <https://www.gitkraken.com/download/> and extract to `~/opt/gitkraken`.

Create symlink: `sudo ln -s /opt/gitkraken/gitkraken /usr/local/bin/gitkraken`

Add icon to GNOME like so: `gnome-desktop-item-edit ~/.local/share/applications/ --create-new`:

```bash
[…]
Icon[en_US]=gitkraken
Name[en_US]=GitKraken
Exec=gitkraken
Name=GitKraken
Icon=gitkraken
```

### Install Robot 3T

Download MongoDB (Binary Installation <https://www.mongodb.com/download-center> and extract to `/opt/mongodb`. Also make sure to add it to the path: `export PATH=$PATH:/opt/mongodb/bin`

Download Robo 3T <https://robomongo.org/download> and extract into `/opt/robot3t. 

To not interfer w/ other (locally build) Qt applications and in order to use *Robomongo* icon from theme, create a executable file `/opt/robot3t/bin/robomongo`:

```bash
#!/bin/bash
LD_LIBRARY_PATH=/usr/local/lib
LIBRARY_PATH=$LD_LIBRARY_PATH
QT_PLUGIN_PATH=
/opt/robo3t/bin/robo3t
```

Then add icon to GNOME like so: `gnome-desktop-item-edit ~/.local/share/applications/ --create-new`

```bash
Icon[en_US]=robomongo
Exec=/opt/robo3t/bin/robomongo
Name[en_US]=Robo 3T
Name=Robo3T
Icon=robomongo
```

### DBeaver

Download latest `tar.gz` archiv of community edition for Linux 64bit from [dbeaver.com](https://dbeaver.jkiss.org/download/) and extract to `/opt/dbeaver`.

Add icon to GNOME like so:q: `gnome-desktop-item-edit ~/.local/share/applications/ --create-new`:

```bash
[…]
Icon[en_US]=dbeaver
Exec=/opt/dbeaver/dbeaver
Name[en_US]=DBeaver
Name=DBeaver
Icon=dbeaver
```

### CrossFTP

Required bundles:

- `java-basic`

Download latest *Portable* version from here <http://www.crossftp.com/download.htm> and extract into `/opt/crossftp`.

Edit `/opt/crossftp/run_client.sh` adding the following line:

```
#!/bin/sh
cd /opt/crossftp
[…]
```

Add icon to GNOME like so:q: `gnome-desktop-item-edit ~/.local/share/applications/ --create-new`:

```bash
[…]
Icon[en_US]=/opt/crossftp/logo_big.png
Name[en_US]=CrossFTP
Exec=/opt/crossftp/run_client.sh
Name=CrossFTP
Icon=/opt/crossftp/logo_big.png
```

### PHP Composer

Required bundles:

- `php-basic`

Download latest release version of *Composer*, as of writing <https://getcomposer.org/download/1.5.2/composer.phar>...

```bash
sudo mkdir -p /usr/local/bin
sudo mv /home/matthias/Downloads/composer.phar /usr/local/bin/composer
sudo chmod +x /usr/local/bin/composer
composer -v
```

Add to the `~/.bashrc`:

```bash
export PATH=$PATH:~/.config/composer/vendor/bin/
```

Download http://curl.haxx.se/ca/cacert.pem and copy certificate PEM file into known location, e.g.:

```bash
mkdir -p ~/certs
cd ~/certs
wget http://curl.haxx.se/ca/cacert.pem
```

Add to the `~/.bashrc`:

```bash
export COMPOSER_CAFILE=~/certs/cacert.pem
```

### Hugo

Download latest release for Linux 64bit from <https://github.com/gohugoio/hugo/releases> and extract the `hugo`binary to `/usr/local/bin/hugo`.

### Tresorit

Download and run installer script from <https://tresorit.com/de/download/linux>...

Add to GNOME Startup Applications via `Tweak Tool`.

## Camlistore

Download latest release <https://camlistore.org/download> and extract to `/opt/camlistore`.

Add to the `~/.bashrc`:

```bash
export PATH=$PATH:/opt/camlistore
```

### LibreOffice (Flatpak)

Simply follow the guide to [install and run the LibreOffice Flatpak image](https://clearlinux.org/documentation/clear-linux/tutorials/flatpak/flatpak.html#add-libreoffice-to-your-gnome-desktop)…


### YubiKey

To set up the Clear Linux system for Universal 2nd Factor (U2F) with YubiKey simply follow [this guide](https://www.yubico.com/support/knowledge-base/categories/articles/can-set-linux-system-use-u2f/) and install the Firefox Add-on [U2F Support Add-on](https://addons.mozilla.org/en-US/firefox/addon/u2f-support-add-on/).

## GNOME Shell Extensions

Currently GNOME extensions can not be installed via <https://extensions.gnome.org/> because even w/ the *GNOME Shell integration extension* installed/ running, a native host connector is not detected.

Offline-installtion to the rescue!

One needs to download and unpack the extensions, and move it into extensions dir like so:

```bash
mv ~/Downloads/clipboard-indicator@tudmotu.com.v26.shell-extension ~/.local/share/gnome-shell/extensions/clipboard-indicator@tudmotu.com
```

Even though the extension is practically installed it is yet disabled. In
order to enable it, one need to use `gnome-tweak-tools`: find the extension (e.g. titled 'Clipboard Indicator'), in the *Extensions* screen and turn it **On**.
One may need to restart the shell (*Alt+F2* and insert `r` in the prompt) for the extension to be listed there.

### Mandatory

- [Caffeine](https://extensions.gnome.org/extension/517/caffeine/) —› `~/.local/share/gnome-shell/extensions/caffeine@patapon.info`
- [Clipboard Indicator](https://extensions.gnome.org/extension/779/clipboard-indicator/) —› `~/.local/share/gnome-shell/extensions/clipboard-indicator@tudmotu.com`
- [system-monitor](https://extensions.gnome.org/extension/120/system-monitor/) —› `~/.local/share/gnome-shell/extensions/system-monitor@paradoxxx.zero.gmail.com` (though charts in menu look weird)
- [gtile](https://extensions.gnome.org/extension/28/gtile/) —› `~/.local/share/gnome-shell/extensions/gTile@vibou`

{{< talk >}}