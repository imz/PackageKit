%define _unpackaged_files_terminate_build 1
%set_verify_elf_method strict
# it's also needed for RPM_LD_PRELOAD_packagekit to work (see below).

Summary:   Package management service
Name:      packagekit
Version:   1.2.0
Release:   alt1
License:   LGPL-2.1+
Group:     Other
URL:       http://www.freedesktop.org/software/PackageKit/

# https://github.com/hughsie/PackageKit.git
Source: %name-%version.tar
Patch1: %name-%version-alt.patch

BuildRequires(pre): rpm-build-python3
BuildRequires(pre): meson
BuildRequires: gcc-c++
BuildRequires: gobject-introspection-devel
BuildRequires: gtk-doc
BuildRequires: intltool
BuildRequires: libsqlite3-devel
BuildRequires: libpolkit-devel
BuildRequires: libsystemd-devel
BuildRequires: libapt-devel
BuildRequires: gstreamer1.0-devel
BuildRequires: gst-plugins1.0-devel
BuildRequires: appstream-devel
BuildRequires: bash-completion

BuildRequires: vala-tools
BuildRequires: libgtk+3-devel

# It provides the stuff needed to run the APT backend: the download methods
# (/usr/lib*/apt/methods/), conf files (/etc/apt/), and cache dirs
# (/var/cache/apt/archives/).
Requires: apt

%description
PackageKit is a D-Bus abstraction layer that allows the session user
to manage packages in a secure way using a cross-distro,
cross-architecture API.

%package -n lib%name-glib
Summary: GLib libraries for accessing PackageKit
Group: Other
Requires: %name = %EVR

%description -n lib%name-glib
GLib libraries for accessing PackageKit.
Group: Other

%package cron
Summary: Cron job and related utilities for PackageKit
Group: Other
BuildArch: noarch
Requires: %name = %EVR

%description cron
Crontab and utilities for running PackageKit as a cron job.

%package -n lib%name-glib-devel
Summary: GLib Libraries and headers for PackageKit
Group: Development/Other
Requires: lib%name-glib = %EVR

%description -n lib%name-glib-devel
GLib headers and libraries for PackageKit.

%package gstreamer-plugin
Summary: Install GStreamer codecs using PackageKit
Group: Other
Requires: lib%name-glib = %EVR

%description gstreamer-plugin
The PackageKit GStreamer plugin allows any Gstreamer application to install
codecs from configured repositories using PackageKit.

%package -n lib%name-gtk3-module
Summary: Install fonts automatically using PackageKit
Group: Other
Requires: lib%name-glib = %EVR

%description -n lib%name-gtk3-module
The PackageKit GTK3+ module allows any Pango application to install
fonts from configured repositories using PackageKit.

%package command-not-found
Summary: Ask the user to install command line programs automatically
Group: Other
Requires: lib%name-glib = %EVR

%description command-not-found
A simple helper that offers to install new packages on the command line
using PackageKit.

%package -n python3-module-%name
Summary: Python3 backend for PackageKit
Group: Development/Python3
BuildArch: noarch
Requires: %name = %EVR

%description -n python3-module-%name
Python3 backend for PackageKit.

%prep
%setup
%patch1 -p1

%build
%add_optflags -std=c++14
%add_optflags -D_FILE_OFFSET_BITS=64
%meson \
	-Dpackaging_backend=aptcc \
	-Dsystemd=true \
	-Doffline_update=true \
	-Dgtk_doc=true \
	-Dlocal_checkout=false \
	-Dpython_backend=true \
	-Ddaemon_tests=false \
	%nil

%meson_build

%install
%meson_install

# Create directories for downloaded appstream data
mkdir -p %buildroot%_cachedir/app-info/{icons,xmls}

# create a link that GStreamer will recognise
pushd %buildroot%_libexecdir
ln -s pk-gstreamer-install gst-install-plugins-helper
popd

# enable packagekit-offline-updates.service here for now, till we
# decide how to do it upstream after the meson conversion:
# https://github.com/hughsie/PackageKit/issues/401
# https://bugzilla.redhat.com/show_bug.cgi?id=1833176
mkdir -p %{buildroot}%{_unitdir}/system-update.target.wants/
ln -sf ../packagekit-offline-update.service %{buildroot}%{_unitdir}/system-update.target.wants/packagekit-offline-update.service

# get rid of test backend
rm -f %buildroot%_libdir/packagekit-backend/libpk_backend_test_*.so
rm -rf %buildroot%_datadir/PackageKit/helpers/test_spawn

# Following scripts seems unused, and it needs to be patched for ALT should it be used
rm -f %buildroot%_datadir/PackageKit/pk-upgrade-distro.sh

# Remove unused files
rm -f %buildroot%_datadir/PackageKit/helpers/aptcc/pkconffile.nodiff

touch %buildroot%_localstatedir/PackageKit/upgrade_lock

%find_lang PackageKit

# We have to choose against which executable to verify the symbols
# in the backend modules. I've chosen the one that rarely gets to be used
# (packagekit-direct), so that it receives more "testing" and problems like
# https://github.com/PackageKit/PackageKit/issues/477 don't stay unnoticed.
#export RPM_LD_PRELOAD_packagekit=%buildroot%_libexecdir/packagekitd
export RPM_LD_PRELOAD_packagekit=%buildroot%_libexecdir/packagekit-direct
export RPM_FILES_TO_LD_PRELOAD_packagekit='%_libdir/packagekit-backend/*.so'
# To rely on this feature, one should have set_verify_elf_method strict

%post
SYSTEMCTL=systemctl
if sd_booted && "$SYSTEMCTL" --version >/dev/null 2>&1; then
	"$SYSTEMCTL" daemon-reload
	if [ "$RPM_INSTALL_ARG1" -eq 1 ]; then
		"$SYSTEMCTL" -q preset %name
	else
		# only request stop of service, don't restart it
		"$SYSTEMCTL" is-active --quiet %name && %_bindir/pkcon quit ||:
	fi
fi

%preun
%preun_service %name ||:

%triggerin -- librpm7
# only on update of librpm7
if [ $2 -eq 2 ] ; then
	# if librpm7 is updated, prohibit packagekit to start and ask it to quit
	touch %_localstatedir/PackageKit/upgrade_lock
	SYSTEMCTL=systemctl
	sd_booted && $SYSTEMCTL is-active --quiet %name && %_bindir/pkcon quit ||:
fi
:

%triggerpostun -- librpm7
# after librpm7 is updated, allow packagekit to restart on request
# it may be a good idea to move this to librpm7 package's delayed actions
rm -f %_localstatedir/PackageKit/upgrade_lock ||:
:

%files -f PackageKit.lang
%doc COPYING
%doc README AUTHORS NEWS
%dir %_datadir/PackageKit
%dir %_datadir/PackageKit/helpers
%dir %_sysconfdir/PackageKit
%dir %_localstatedir/PackageKit
%dir %_cachedir/app-info
%dir %_cachedir/app-info/icons
%dir %_cachedir/app-info/xmls
%dir %_libdir/packagekit-backend
%config(noreplace) %_sysconfdir/PackageKit/PackageKit.conf
%config(noreplace) %_sysconfdir/PackageKit/Vendor.conf
%config %_sysconfdir/dbus-1/system.d/*
%_man1dir/pkcon.1*
%_man1dir/pkmon.1*
%_datadir/polkit-1/actions/*.policy
%_datadir/polkit-1/rules.d/*
%_datadir/bash-completion/completions/pkcon
%_libexecdir/packagekitd
%_libexecdir/packagekit-direct
%_bindir/pkmon
%_bindir/pkcon
%exclude %_libdir/libpackagekit*.so.*
%ghost %verify(not md5 size mtime) %_localstatedir/PackageKit/transactions.db
%ghost %_localstatedir/PackageKit/upgrade_lock
%_datadir/dbus-1/system-services/*.service
%_datadir/dbus-1/interfaces/*.xml
%_unitdir/packagekit-offline-update.service
%_unitdir/packagekit.service
%_unitdir/system-update.target.wants/
%_libexecdir/pk-*offline-update
%config %_sysconfdir/apt/apt.conf.d/20packagekit
%_libdir/packagekit-backend/libpk_backend_aptcc.so

%files -n lib%name-glib
%_libdir/*packagekit-glib2.so.*
%_libdir/girepository-1.0/PackageKitGlib-1.0.typelib

%files cron
%config %_sysconfdir/cron.daily/packagekit-background.cron
%config(noreplace) %_sysconfdir/sysconfig/packagekit-background

%files gstreamer-plugin
%_libexecdir/pk-gstreamer-install
%_libexecdir/gst-install-plugins-helper

%files -n lib%name-gtk3-module
%_libdir/gtk-3.0/modules/*.so
%_libdir/gnome-settings-daemon-3.0/gtk-modules/*.desktop

%files command-not-found
%_sysconfdir/profile.d/*
%_libexecdir/pk-command-not-found
%config(noreplace) %_sysconfdir/PackageKit/CommandNotFound.conf

%files -n lib%name-glib-devel
%_libdir/libpackagekit-glib2.so
%_pkgconfigdir/packagekit-glib2.pc
%dir %_includedir/PackageKit
%dir %_includedir/PackageKit/packagekit-glib2
%_includedir/PackageKit/packagekit-glib*/*.h
%_datadir/gir-1.0/PackageKitGlib-1.0.gir
%_datadir/gtk-doc/html/PackageKit
%_datadir/vala/vapi/packagekit-glib2.vapi
%_datadir/vala/vapi/packagekit-glib2.deps

%files -n python3-module-%name
%python3_sitelibdir_noarch/*


%package checkinstall
Summary: Immediately test PK when installing this package
Group: Other
BuildArch: noarch
Requires: apt-under-pkdirect-checkinstall

%description checkinstall
Immediately test PackageKit when installing this package.

%files checkinstall


%changelog
* Fri Jun 05 2020 Aleksei Nikiforov <darktemplar@altlinux.org> 1.2.0-alt1
- Updated to upstream version 1.2.0.

* Wed Apr 01 2020 Aleksei Nikiforov <darktemplar@altlinux.org> 1.1.13-alt1
- Updated to upstream version 1.1.13.

* Mon Oct 14 2019 Aleksei Nikiforov <darktemplar@altlinux.org> 1.1.12-alt12
- Imported changes from upstream.

* Mon Sep 30 2019 Aleksei Nikiforov <darktemplar@altlinux.org> 1.1.12-alt11
- Improved provision of information about obsoleting and obsoleted packages.

* Tue Sep 17 2019 Aleksei Nikiforov <darktemplar@altlinux.org> 1.1.12-alt10
- Added support for lua scripts.
- Disabled verbose logging for packagekit service.
- Pulled minor fixes and updates from upstream.

* Fri Aug 30 2019 Aleksei Nikiforov <darktemplar@altlinux.org> 1.1.12-alt9
- Added special formatting for ALT repositories origin.
- Fixed displaying obsoleted packages in output of 'pkcon get-updates'.

* Fri Aug 30 2019 Aleksei Nikiforov <darktemplar@altlinux.org> 1.1.12-alt8
- Fixed processing obsoletes during upgrades (Closes: #36342).

* Wed Jun 26 2019 Ivan Zakharyaschev <imz@altlinux.org> 1.1.12-alt7
- Fixed support for refreshCache action. (Thx Aleksei Nikiforov darktemplar@)

* Thu Jun 13 2019 Aleksei Nikiforov <darktemplar@altlinux.org> 1.1.12-alt6
- Rebuilt with new Apt.

* Wed Feb 06 2019 Aleksei Nikiforov <darktemplar@altlinux.org> 1.1.12-alt5
- Fixed crash during showing errors.
- Enabled verbose logging for packagekit service.

* Fri Feb 01 2019 Aleksei Nikiforov <darktemplar@altlinux.org> 1.1.12-alt4
- Fixed stopping service without finishing current request.

* Thu Jan 31 2019 Aleksei Nikiforov <darktemplar@altlinux.org> 1.1.12-alt3
- Updated build dependencies.

* Mon Jan 28 2019 Aleksei Nikiforov <darktemplar@altlinux.org> 1.1.12-alt2
- Forced stopping and blocked restarting of packagekit service during
  upgrade of librpm7, improved locking (Closes: #35987).

* Tue Dec 18 2018 Aleksei Nikiforov <darktemplar@altlinux.org> 1.1.12-alt1
- Initial build for ALT.
