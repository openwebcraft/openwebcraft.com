---
title: "Install RStudio Desktop on Clear Linux"
featured_image: "/img/clearlinux_logo_wire_rstudio.jpg"
date: 2018-11-22T19:45:00+02:00
tags: 
- clearlinux
- clr
- linux
- r
- rstudio
- rstudio-desktop
draft: false
---

How I've installed (a.k.a build from src) RStudio — for now only Desktop — on my Clear Linux desktop environment — **UPDATED 2018-11-22 on `clear-26430`**…

<!--more-->

## 1. Install Clear Linux Dependencies

First things first. Let's install dependencies via clear bundles…

```bash
sudo swupd bundle-add qt-basic qt-basic-dev R-basic R-extras java-basic
```

## 2. Get the latest RStudio Desktop Source Code 

The RStudio Desktop needs to be build/ installed from source. 

Let's get started by cloning <https://github.com/rstudio/rstudio/>…

```bash
git clone https://github.com/rstudio/rstudio.git; cd rstudio
```

## 3. Install RStudio Desktop's Common Linux Dependencies

```bash
cd dependencies/common; ./install-common; cd -
```

## 4. Install RStudio Desktop's Qt 5.11.1 Dependecy into `$HOME/`

```
./dependencies/linux/install-qt-sdk
```

## 5. Build and Install RStudio Desktop

Finally, let's build and install…

```bash
mkdir build
cd build
cmake .. -DRSTUDIO_TARGET=Desktop -DCMAKE_BUILD_TYPE=Release
sudo make install
```

One thing to note though: the `sudo make install` step did not succeed on first run, instead failing with rather strange java errors.

A simple clean build `sudo make clean` and then again `sudo make install` solved it for me — build succeeded. :-)

## 6. Start RStudio Desktop

In order to start *RStudio Desktop*, you only have to specifiy the `LD_LIBRARY_PATH` like so:

```bash
LD_LIBRARY_PATH=~/Qt5.11.1/5.11.1/gcc_64/lib /usr/local/lib/rstudio/bin/rstudio
```

One could certainly tweak the build to get rid of `LD_LIBRARY_PATH`.

For integration with GNOME desktop one might want to add an icon like so: `gnome-desktop-item-edit ~/.local/share/applications/ --create-new`:

```bash
[…]
Icon[en_US]=rstudio
Name[en_US]=RStudio
Exec=env LD_LIBRARY_PATH=~/Qt5.11.1/5.11.1/gcc_64/lib /usr/local/lib/rstudio/bin/rstudio
Name=RStudio
Icon=rstudio
```

{{< talk >}}