---
title: "Install RStudio Desktop on Clear Linux"
featured_image: "/img/clearlinux_logo_wire_rstudio.jpg"
date: 2017-10-17T23:00:12+02:00
tags: 
- clearlinux
- clr
- linux
- r
- rstudio
- rstudio-desktop
draft: false
---

How I've installed (a.k.a build from src) RStudio — for now only Desktop — on my Clear Linux desktop environment…

<!--more-->

Install RStudio Desktop on Clear Linux

## Desktop

The RStudio Desktop needs to be build/ installed from source. 

Let's get started by cloning <https://github.com/rstudio/rstudio/>…

### Install dependencies

[It seems](https://bugreports.qt.io/browse/QTBUG-48353) that *Qt v5.4.x* requires *GStreamer v0.10.x*.

So, download and extract latest v0.10.x *gstreamer* <https://gstreamer.freedesktop.org/src/gstreamer/gstreamer-0.10.36.tar.bz2>…

… and apply *patch*:

```bash
---
 gst/parse/grammar.y | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

diff --git a/gst/parse/grammar.y b/gst/parse/grammar.y
index 24fc87b..24fe906 100644
--- a/gst/parse/grammar.y
+++ b/gst/parse/grammar.y
@@ -36,7 +36,7 @@
 
 typedef void* yyscan_t;
 
-int priv_gst_parse_yylex (void * yylval_param , yyscan_t yyscanner);
+int priv_gst_parse_yylex (yyscan_t yyscanner);
 int priv_gst_parse_yylex_init (yyscan_t scanner);
 int priv_gst_parse_yylex_destroy (yyscan_t scanner);
 struct yy_buffer_state * priv_gst_parse_yy_scan_string (char* , yyscan_t);
-- 
```

Then build *gstreamer*.

```bash
export LD_LIBRARY_PATH=/usr/local/lib/
./autogen.sh --disable-gtk-doc
make
sudo make install
```

Next, download and extract <https://gstreamer.freedesktop.org/src/gst-plugins-base/gst-plugins-base-0.10.36.tar.bz2>…

… and build * gst-plugins-base*:

```bash
export LD_LIBRARY_PATH=/usr/local/lib/
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:~/Downloads/gstreamer-0.10.36/pkgconfig
./autogen.sh --disable-gtk-doc
make
sudo make install
```

Now, install additional, common depdencies for *rstudio* like so:

```bash
cd rstudio
cd ./dependencies/common; ./install-common; cd -
./dependencies/linux/install-qt-sdk
sudo swupd bundle-add R-basic R-extras java-basic
```

### Make RStudio

One needs to set the runtime shared library search path using the `-rpath`linker option by adding the following to e.g. `rstudio/CMakeGlobals.txt`:

```bash
SET(CMAKE_EXE_LINKER_FLAGS 
          "${CMAKE_EXE_LINKER_FLAGS} -Wl,-rpath -Wl,/usr/local/lib")
```

Then follow along the instructions in `INSTALL`, essentially:

```bash
mkdir build
cd build
cmake .. -DRSTUDIO_TARGET=Desktop -DCMAKE_BUILD_TYPE=Release
sudo make install
```

### GNOME Integration

The execution of the binary requires the Qt plugins configured like so: `export QT_PLUGIN_PATH=~/Qt5.4.0/5.4/gcc_64/plugins`

You might want to move the build result dir to `/opt` and add icon to GNOME like so: `gnome-desktop-item-edit ~/.local/share/applications/ --create-new`:

```bash
[…]
Icon[en_US]=rstudio
Name[en_US]=RStudio
Exec=/opt/rstudio/bin/rstudio
Name=RStudio
Icon=rstudio
```

## Server

TODO

{{< talk >}}