---
title: "Build Sailfish OS for Sony Xperia™ X"
featured_image: "/img/sonyxperiax_sailfishos-2-1-1-26-f5121.jpg"
date: 2017-09-23T00:19:36+02:00
tags:
- sailfishos
- jolla
- linux
- sony
- xperiax
- mobile
draft: false
---

Notes taken while following along the official guide "Sailfish OS Hardware Adaptation Development Kit for Sony Xperia X"…

<!--more-->

The long awaitet blog post is finally here: [Opening Sailfish OS HW Adaptation Source Code for Sony Xperia™ X](https://blog.jolla.com/xperiax-open-source-hw-adaptation/).

And, guess what? Only one day prior to the announcement of the first publicly available *Hardware Adaptation sources and instructions for Sailfish X, aka Sailfish OS for Sony Xperia™ X* my [Sony Xperia X](https://www.sonymobile.com/global-en/products/phones/xperia-x/) had arrived.

Soooo, no excuses anymore, right?

**GO** :-)

**DISCLAIMER** The following are my personal notes, taken while following along the AWESOME(!) guide [Sailfish OS Hardware Adaptation Development Kit for Sony Xperia X](https://sailfishos.org/wiki/Sailfish_X_Build_and_Flash) and accompanying community documentation. It is totally not my intend to duplicate documentation — it's just a journal of the required steps when starting from scratch, compiled into a singe doc.

## My host setup

- hardware: [Slimbook KATANA](https://slimbook.es/en/ultrabook-katana-en), Intel Core i7-6500U, 16GB RAM, mSata SSD
- OS: Debian 9.1 stretch (*x86_64 Linux 4.9.0-3-amd64*)

## 1. Install Platform SDK

Setting up required environment variables, partly mixed w/ build instructions from [Sailfish OS Hardware Adaptation Development Kit for Sony Xperia X](https://sailfishos.org/wiki/Sailfish_X_Build_and_Flash)

```bash
cat <<'EOF' > $HOME/.hadk.env
export PLATFORM_SDK_ROOT="/srv/mer"
export ANDROID_ROOT="$HOME/hadk"
export VENDOR="sony"
export DEVICE="f5121"
export HABUILD_DEVICE="suzu" 
# ARCH conflicts with kernel build
export PORT_ARCH="armv7hl"
EOF
cat <<'EOF' >> $HOME/.mersdkubu.profile
function hadk() { source $HOME/.hadk.env; echo "Env setup for $DEVICE"; }
export PS1="HABUILD_SDK [\${DEVICE}] $PS1"
hadk
EOF
cat <<'EOF' >> $HOME/.mersdk.profile
function hadk() { source $HOME/.hadk.env; echo "Env setup for $DEVICE"; }
hadk
EOF
```

Slightly adopted from <https://sailfishos.org/wiki/Platform_SDK_Installation>…

Add to `~/.bashrc`: 

```bash
export SAILFISHOS_PLATFORM_SDK_ROOT=/srv/mer
export PLATFORM_SDK_ROOT=$SAILFISHOS_PLATFORM_SDK_ROOT
alias sfossdk=$PLATFORM_SDK_ROOT/sdks/sfossdk/mer-sdk-chroot
```

Then:

```bash
source ~/.bashrc
curl -k -O http://releases.sailfishos.org/sdk/installers/latest/Jolla-latest-SailfishOS_Platform_SDK_Chroot-i486.tar.bz2 ;
sudo mkdir -p $SAILFISHOS_PLATFORM_SDK_ROOT/sdks/sfossdk ;
sudo tar --numeric-owner -p -xjf Jolla-latest-SailfishOS_Platform_SDK_Chroot-i486.tar.bz2 -C $SAILFISHOS_PLATFORM_SDK_ROOT/sdks/sfossdk  ;
echo 'PS1="PlatformSDK $PS1"' > ~/.mersdk.profile ;
echo '[ -d /etc/bash_completion.d ] && for i in /etc/bash_completion.d/*;do . $i;done'  >> ~/.mersdk.profile ;
sfossdk

PlatformSDK matthias@debbook:~$ 
```

## 2. Preparing the Platform SDK

```bash
PlatformSDK matthias@debbook:~$ 

sudo zypper in android-tools createrepo zip
```

## 3.  Setting up an Android Build Environment

Following the [Sailfish OS Hardware Adaptation Development Kit Documentation](https://sailfishos.org/wp-content/uploads/2017/09/SailfishOS-HardwareAdaptationDevelopmentKit-2.0.0.pdf)…

```bash
PlatformSDK matthias@debbook:~$ 

TARBALL=ubuntu-trusty-android-rootfs.tar.bz2
curl -O http://img.merproject.org/images/mer-hybris/ubu/$TARBALL
UBUNTU_CHROOT=$PLATFORM_SDK_ROOT/sdks/ubuntu
sudo mkdir -p $UBUNTU_CHROOT
sudo tar --numeric-owner -xjf $TARBALL -C $UBUNTU_CHROOT
```

## 4.  Entering Ubuntu Chroot

```bash
PlatformSDK matthias@debbook:~$ 

ubu-chroot -r $PLATFORM_SDK_ROOT/sdks/ubuntu

HABUILD_SDK [f5121] matthias@debbook:~$

sudo apt-get update
sudo apt-get install bsdmainutils
sudo apt-get install openjdk-7-jdk
sudo update-java-alternatives -s java-1.7.0-openjdk-amd64
sudo apt-get install rsync vim unzip
```

## 5. Checking out CyanogenMod Source and Building…

```bash
PlatformSDK matthias@debbook:~$ 

git config --global user.name "Matthias Geisler"
git config --global user.email "matthias"@openwebcraft.com"
``` 

Install `repo` command <https://source.android.com/source/downloading#installing-repo>…

From here  on we're going to use the build instructions from [Sailfish OS Hardware Adaptation Development Kit for Sony Xperia X](https://sailfishos.org/wiki/Sailfish_X_Build_and_Flash)

```bash
HABUILD_SDK [f5121] matthias@debbook:~$

sudo mkdir -p $ANDROID_ROOT
sudo chown -R $USER $ANDROID_ROOT
cd $ANDROID_ROOT
repo init -u git://github.com/mer-hybris/android.git -b hybris-sony-aosp-6.0.1_r80-20170902
repo sync -j1000 --fetch-submodules
source build/envsetup.sh
# Please download Sony Xperia X Software binaries for AOSP Marshmallow (Android 6.0.1) from
# https://developer.sonymobile.com/downloads/tool/software-binaries-for-aosp-marshmallow-6-0-1-loire/
# and unzip its contents in this directory like this:
unzip ~/Downloads/SW_binaries_for_Xperia_AOSP_*.zip
export USE_CCACHE=1
lunch aosp_$DEVICE-userdebug
make -j10 hybris-hal

[…]
Install: out/target/product/suzu/hybris-boot.img
Install: out/target/product/suzu/hybris-recovery.img

#### make completed successfully (10:25 (mm:ss)) ####

HABUILD_SDK [f5121] matthias@debbook:~$ 
```

## 6. Se up Scratchbox2 Target

Download the latest `"SailfishOS-armv7hl` from <http://releases.sailfishos.org/sdk/latest/targets/targets.json>…

```bash
PlatformSDK matthias@debbook:~

sudo zypper in -t pattern Mer-SB2-armv7hl

sdk-assistant create $VENDOR-$DEVICE-$PORT_ARCH ~/Downloads/Jolla-2.1.0.10-Sailfish_SDK_Target-armv7hl.tar.bz2
```

Create `~/main.c`:

```bash
#include <stdlib.h>
#include <stdio.h>
int main(void) {
printf("Hello, world!\n");
return EXIT_SUCCESS;
}
```
Compile and test:

```bash
sb2 -t $VENDOR-$DEVICE-$PORT_ARCH gcc main.c -o test
sb2 -t $VENDOR-$DEVICE-$PORT_ARCH ./test
```
## 7. Packaging

```bash
PlatformSDK matthias@debbook:~

cd $ANDROID_ROOT
rpm/dhd/helpers/build_packages.sh --droid-hal
git clone --recursive https://github.com/mer-hybris/droid-config-$DEVICE hybris/droid-configs
if [ -z "$(grep community_adaptation $ANDROID_ROOT/hybris/droid-configs/rpm/droid-config-$DEVICE.spec)" ]; then
  sed -i '/%include droid-configs-device/i%define community_adaptation 1\n' $ANDROID_ROOT/hybris/droid-configs/rpm/droid-config-$DEVICE.spec
fi
if [ -z "$(grep patterns-sailfish-consumer-generic $ANDROID_ROOT/hybris/droid-configs/patterns/jolla-configuration-$DEVICE.yaml)" ]; then
  sed -i "/Summary: Jolla Configuration $DEVICE/i- patterns-sailfish-consumer-generic\n- patterns-sailfish-store-applications\n- pattern:sailfish-porter-tools\n" $ANDROID_ROOT/hybris/droid-configs/patterns/jolla-configuration-$DEVICE.yaml
fi
rpm/dhd/helpers/build_packages.sh --configs
sb2 -t $VENDOR-$DEVICE-$PORT_ARCH -m sdk-install -R zypper in droid-hal-$DEVICE-kernel
sb2 -t $VENDOR-$DEVICE-$PORT_ARCH -m sdk-install -R zypper in --force-resolution droid-hal-$DEVICE-kernel-modules
rpm/dhd/helpers/build_packages.sh --mw=https://github.com/sailfishos/initrd-helpers
rpm/dhd/helpers/build_packages.sh --mw=https://github.com/nemomobile/hw-ramdisk
rpm/dhd/helpers/build_packages.sh --mw=https://github.com/sailfishos/yamui
git clone --recursive https://github.com/mer-hybris/droid-hal-img-boot-$DEVICE hybris/mw/droid-hal-img-boot-$DEVICE
rpm/dhd/helpers/build_packages.sh --mw=https://github.com/mer-hybris/droid-hal-img-boot-$DEVICE
```

```bash
HABUILD_SDK [f5121] matthias@debbook:~$

sudo apt-get install rsync
cd $ANDROID_ROOT/..
mkdir syspart
cd syspart
repo init -u git://github.com/mer-hybris/android.git -b syspart-sony-aosp-6.0.1_r80-20170902
repo sync -j1000 --fetch-submodules
source build/envsetup.sh
unzip ~/Downloads/SW_binaries_for_Xperia_AOSP_*.zip
export USE_CCACHE=1
lunch aosp_$DEVICE-userdebug
make -j10  libnfc-nci bluetooth.default_32 systemtarball

[...]
Target system fs tarball: out/target/product/suzu/system.tar.bz2
build/tools/mktarball.sh out/host/linux-x86/bin/fs_get_stats out/target/product/suzu system out/target/product/suzu/system.tar out/target/product/suzu/system.tar.bz2 out/target/product/suzu/system

#### make completed successfully (02:16:23 (hh:mm:ss)) ####
```

```bash
PlatformSDK matthias@debbook:~

cd $ANDROID_ROOT/../syspart
git clone https://github.com/mer-hybris/droid-system-$DEVICE
mb2 -t $VENDOR-$DEVICE-$PORT_ARCH -s droid-system-$DEVICE/rpm/droid-system-$DEVICE.spec build
rm -f $ANDROID_ROOT/droid-local-repo/$DEVICE/droid-system-*.rpm
mv RPMS/droid-system-$DEVICE-0.1.1-1.armv7hl.rpm $ANDROID_ROOT/droid-local-repo/$DEVICE/
createrepo "$ANDROID_ROOT/droid-local-repo/$DEVICE"
sb2 -t $VENDOR-$DEVICE-$PORT_ARCH -m sdk-install -R zypper ref
```

```bash
HABUILD_SDK [f5121] matthias@debbook:~$
 
cd $ANDROID_ROOT
git clone https://github.com/mer-hybris/audioflingerglue external/audioflingerglue
git clone https://github.com/sailfishos/droidmedia external/droidmedia

source build/envsetup.sh
lunch aosp_$DEVICE-userdebug
make -j10 libdroidmedia_32 minimediaservice minisfservice libaudioflingerglue_32 miniafservice
```

```bash
PlatformSDK matthias@debbook:~

cd $ANDROID_ROOT
DROIDMEDIA_VERSION=$(git --git-dir external/droidmedia/.git describe --tags | sed -r "s/\-/\+/g")
DEVICE=$HABUILD_DEVICE rpm/dhd/helpers/pack_source_droidmedia-localbuild.sh $DROIDMEDIA_VERSION
mkdir -p hybris/mw/droidmedia-localbuild/rpm
cp rpm/dhd/helpers/droidmedia-localbuild.spec hybris/mw/droidmedia-localbuild/rpm/droidmedia.spec
sed -ie "s/0.0.0/$DROIDMEDIA_VERSION/" hybris/mw/droidmedia-localbuild/rpm/droidmedia.spec
mv hybris/mw/droidmedia-$DROIDMEDIA_VERSION.tgz hybris/mw/droidmedia-localbuild
rpm/dhd/helpers/build_packages.sh --build=hybris/mw/droidmedia-localbuild
rpm/dhd/helpers/build_packages.sh --mw=https://github.com/sailfishos/gst-droid.git

DEVICE=$HABUILD_DEVICE rpm/dhd/helpers/pack_source_audioflingerglue-localbuild.sh
mkdir -p hybris/mw/audioflingerglue-localbuild/rpm
cp rpm/dhd/helpers/audioflingerglue-localbuild.spec hybris/mw/audioflingerglue-localbuild/rpm/audioflingerglue.spec
mv hybris/mw/audioflingerglue-0.0.1.tgz hybris/mw/audioflingerglue-localbuild
rpm/dhd/helpers/build_packages.sh --build=hybris/mw/audioflingerglue-localbuild
rpm/dhd/helpers/build_packages.sh --mw=https://github.com/mer-hybris/pulseaudio-modules-droid-glue.git

git clone --recursive https://github.com/mer-hybris/droid-hal-version-$DEVICE hybris/droid-hal-version-$DEVICE
rpm/dhd/helpers/build_packages.sh --version

[...]
----------------------DONE! Now proceed on creating the rootfs------------------
```

## 8. Create the Sailfish OS root filesystem

```bash
PlatformSDK matthias@debbook:~

cd $ANDROID_ROOT
HA_REPO="repo --name=adaptation-community-common-$DEVICE-@RELEASE@"
HA_DEV="repo --name=adaptation-community-$DEVICE-@RELEASE@"
KS="Jolla-@RELEASE@-$DEVICE-@ARCH@.ks"
sed \
"/$HA_REPO/i$HA_DEV --baseurl=file:\/\/$ANDROID_ROOT\/droid-local-repo\/$DEVICE" \
$ANDROID_ROOT/hybris/droid-configs/installroot/usr/share/kickstarts/$KS \
> $KS
```

```bash
PlatformSDK matthias@debbook:~

cd $ANDROID_ROOT
rpm/dhd/helpers/build_packages.sh --configs
```

Save the contents of [Mic-loop.patch](https://sailfishos.org/wiki/Mic-loop.patch) as `~/Downloads/mic-loop.patch`.

```bash
PlatformSDK matthias@debbook:~

RELEASE=2.1.1.26 # if your sb2 target is 2.1.0, do not worry about that
sudo zypper in lvm2 atruncate pigz
sudo ssu ar unbreakmic http://repo.merproject.org/obs/home:/sledge:/branches:/mer-tools:/devel/latest_i486/
sudo zypper ref unbreakmic
sudo zypper in droid-tools
sudo zypper in --force mic
cd /usr/lib/python2.7/site-packages/mic/
sudo patch -p1 --dry-run < ~/Downloads/mic-loop.patch
# ensure above worked, then
sudo patch -p1 < ~/Downloads/mic-loop.patch
cd $ANDROID_ROOT
sudo mic create loop --arch=$PORT_ARCH \
    --tokenmap=ARCH:$PORT_ARCH,RELEASE:$RELEASE,EXTRA_NAME:$EXTRA_NAME \
    --record-pkgs=name,url     --outdir=sfe-$DEVICE-$RELEASE$EXTRA_NAME \
    $ANDROID_ROOT/Jolla-@RELEASE@-$DEVICE-@ARCH@.ks

[...]
Info: The new image can be found here:
  /home/matthias/hadk/sfe-f5121-2.1.1.26/Jolla-2.1.1.26-f5121-armv7hl.ks
  /home/matthias/hadk/sfe-f5121-2.1.1.26/Jolla-2.1.1.26-f5121-armv7hl.ks
  /home/matthias/hadk/sfe-f5121-2.1.1.26/Jolla-2.1.1.26-f5121-armv7hl.packages
  /home/matthias/hadk/sfe-f5121-2.1.1.26/Jolla-2.1.1.26-f5121-armv7hl.urls
  /home/matthias/hadk/sfe-f5121-2.1.1.26/Jolla-2.1.1.26-f5121-armv7hl.xml
  /home/matthias/hadk/sfe-f5121-2.1.1.26/SailfishOS-2.1.1.26-f5121-0.0.1.1.tar.bz2
  /home/matthias/hadk/sfe-f5121-2.1.1.26/extracting-README.txt
  /home/matthias/hadk/sfe-f5121-2.1.1.26/hw-release
  /home/matthias/hadk/sfe-f5121-2.1.1.26/sailfish-release

Info: Finished.
```
## 9. Flashing

```bash
PlatformSDK matthias@debbook:~

mkdir flashing
cd flashing
tar -xvf $ANDROID_ROOT/sfe-$DEVICE-$RELEASE$EXTRA_NAME/SailfishOS-*.tar.bz2
cd SailfishOS-*/
```
Act upon instructions in the `flashing-README.txt`…

Unlock bootloader: <https://developer.sonymobile.com/unlockbootloader/unlock-yourboot-loader/>

```bash
fastboot -i 0x0fce oem unlock 0xUNLOCK_CODE
...
OKAY [  0.180s]
finished. total time: 0.180s
```

If the above fails w/ `FAILED (remote: Command not allowed)` make sure to enable *OEM unlock* in developer options.

…and flash the phone:

```bash
matthias@debbook:~

apt-get install android-tools-fastboot

cd SailfishOS-*/
bash ./flash.sh
```

If `gcc [^se]*.c sha1.c sparse_crc32.c ext4_utils.c extent.c -o make_ext4fs -lz` gives error:

```bash
output_file.c:30:18: fatal error: zlib.h: No such file or directory
 #include <zlib.h>
                  ^
compilation terminated.
```

Simply install the missing w/ `sudo apt-get install libz-dev`.

DONE :-)

{{< tweet 911351102905503744 >}}

UPDATE 2017-09-23 — The installable image generated by my build can be downloaded [here](https://drive.google.com/open?id=0BwOvmHZd_nB6QlN5eFQ1YVNyelk). **DISCLAIMER: Flash it at YOUR OWN RISK (see above section 9.). I'M NOT RESPONSIBLE for you or your phone.**

{{< talk >}}