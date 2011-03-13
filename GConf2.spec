%define pkgname		GConf
%define api_version	2
%define	lib_major	4
%define lib_name	%mklibname %{name}_ %{lib_major}
%define lib_namedev	%mklibname -d %{name}

# Version of required packages
%define req_orbit_version	2.4.0
%define req_glib_version	2.25.12

%define giolibname %mklibname gio2.0_ 0
Summary:	A configuration database system for GNOME 2
Name:		%{pkgname}%{api_version}
Version: 2.32.1
Release:	%mkrel 1
License:	LGPLv2+
Group:		Graphical desktop/GNOME
URL:		http://www.gnome.org/projects/gconf/
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

Source0: 	ftp://ftp.gnome.org/pub/GNOME/sources/%{pkgname}/%{pkgname}-%{version}.tar.bz2
Source1:	gconf.sh
Source2:	gconf.csh
Source3:        gconf-schemas.filter	 
Source4:        gconf-schemas.script
# (fc) reload database when schemas are installed/uninstalled (GNOME bug #328697)
Patch1:		GConf-2.12.1-reload.patch
Conflicts:	GConf < 1.0.6
BuildRequires:  libglib2-devel >= %{req_glib_version}
BuildRequires:	libxml2-devel
BuildRequires:	libgtk+2-devel
BuildRequires:	polkit-1-devel
BuildRequires:	libORBit2-devel >= %{req_orbit_version}
BuildRequires:  dbus-glib-devel
BuildRequires:  autoconf2.5
BuildRequires:  gtk-doc
BuildRequires:  intltool
BuildRequires:	libldap-devel
BuildRequires:	gobject-introspection-devel
Requires:	polkit-agent
Requires:	%{lib_name} = %{version}
# needed by patch1
Requires:	psmisc
Requires:	sed
Requires(post):	update-alternatives

%description
GConf is a configuration data storage mechanism scheduled to
ship with GNOME 2.0. GConf does work without GNOME however; it
can be used with plain GTK+, Xlib, KDE, or even text mode
applications as well.

%package sanity-check
Summary:	Sanity checker for %{pkgname}%{api_version}
Group:		%{group}
Conflicts: %name < 2.21.90-2mdv

%description sanity-check
gconf-sanity-check is a tool to check the sanity of a %{pkgname}%{api_version}
installation.

%package -n %{lib_name}
Summary:	%{summary}
Group:		System/Libraries
Provides:	lib%{name} >= %{version}-%{release}
Requires:  	%{name} >= %{version}
Requires:	libORBit2 >= %{req_orbit_version}
Conflicts: gir-repository < 0.6.5-12
Requires(post): %giolibname >= 2.23.4-2mdv
Requires(postun): %giolibname >= 2.23.4-2mdv

%description -n %{lib_name}
GConf is a configuration data storage mechanism scheduled to
ship with GNOME 2.0. GConf does work without GNOME however; it
can be used with plain GTK+, Xlib, KDE, or even text mode
applications as well.

This package contains necessary libraries to run any programs linked
with GConf.

%package -n %{lib_namedev}
Summary:	Development libraries and headers for GConf
Group:		Development/GNOME and GTK+
Conflicts:	libGConf1-devel < 1.0.6
Provides:	lib%{name}-devel = %{version}-%{release}
Requires:	%{lib_name} = %{version}
Requires: 	%name-sanity-check = %version
Requires:	libORBit2-devel
Requires:	libglib2-devel >= %{req_glib_version}
Requires:  dbus-glib-devel
Obsoletes: %mklibname -d %{name}_ 4
Conflicts: gir-repository < 0.6.5-12

%description -n %{lib_namedev}
GConf is a configuration data storage mechanism scheduled to
ship with GNOME 2.0. GConf does work without GNOME however; it
can be used with plain GTK+, Xlib, KDE, or even text mode
applications as well.

This package contains the header files and libraries needed to develop
applications using GConf.

%prep
%setup -q -n %{pkgname}-%{version}
%apply_patches

%build
# <mrl> 20080110 texpdf is currently fork-bombing :(
%configure2_5x --disable-gtk-doc --with-gtk=2.0

%make

%check
make check

%install
rm -rf $RPM_BUILD_ROOT

%makeinstall_std

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/profile.d
install -m 755 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/gconf.sh
install -m 755 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/gconf.csh

mkdir %{buildroot}%{_sysconfdir}/gconf/schemas

# Provide /usr/lib/gconfd-2 symlink on lib64 platforms
%if "%{_lib}" != "lib"
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib
ln -s ../%{_lib}/gconfd-%{api_version} $RPM_BUILD_ROOT%{_prefix}/lib/gconfd-%{api_version}
%endif

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/gconf/{gconf.xml.local-defaults,gconf.xml.local-mandatory,gconf.xml.system}

cat << EOF > $RPM_BUILD_ROOT%{_sysconfdir}/gconf/2/local-defaults.path
xml:readonly:/etc/gconf/gconf.xml.local-defaults
include "\$(HOME)/.gconf.path.defaults"
EOF

cat << EOF > $RPM_BUILD_ROOT%{_sysconfdir}/gconf/2/local-mandatory.path
xml:readonly:/etc/gconf/gconf.xml.local-mandatory
include "\$(HOME)/.gconf.path.mandatory"
EOF

# automatic install of gconf schemas on rpm installs	 
# (see http://wiki.mandriva.com/en/Rpm_filetriggers)	 
install -d %buildroot%{_var}/lib/rpm/filetriggers	 
install -m 644 %{SOURCE3} %buildroot%{_var}/lib/rpm/filetriggers	 
install -m 755 %{SOURCE4} %buildroot%{_var}/lib/rpm/filetriggers	 

%{find_lang} %{name}

# remove unpackaged files
rm -f $RPM_BUILD_ROOT%{_libdir}/{gio/modules/,GConf/%{api_version}}/*.a

%clean
rm -rf %{buildroot}

# remove buggy symlink
%post
update-alternatives --install %{_bindir}/gconftool gconftool /usr/bin/gconftool-%{api_version} 20
if [ "$1" = "2" ]; then 
		update-alternatives --auto gconftool
fi

%triggerpostun -- GConf2 < 2.22.0-4mdv
GCONF_CONFIG_SOURCE=`%{_bindir}/gconftool-2 --get-default-source` %{_bindir}/gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/*.schemas > /dev/null

%files -f %{name}.lang
%defattr(-, root, root)
%doc README
%config(noreplace) %{_sysconfdir}/profile.d/*
%config(noreplace) %_sysconfdir/dbus-1/system.d/org.gnome.GConf.Defaults.conf
%_sysconfdir/xdg/autostart/gsettings-data-convert.desktop
%_bindir/gsettings-data-convert
%_bindir/gsettings-schema-convert
%{_bindir}/gconftool*
%{_bindir}/gconf-merge-tree
%_mandir/man1/gconftool-2.1*
%_mandir/man1/gsettings-data-convert.1*
%_mandir/man1/gsettings-schema-convert.1*
%if "%{_lib}" != "lib"
%{_prefix}/lib/gconfd-%{api_version}
%endif
%{_libexecdir}/gconfd-%{api_version}
%{_libexecdir}/gconf-defaults-mechanism
%dir %{_libdir}/GConf
%dir %{_libdir}/GConf/%{api_version}
%{_libdir}/GConf/%{api_version}/*.so
%config(noreplace) %{_sysconfdir}/gconf/%{api_version}
%dir %{_sysconfdir}/gconf
%dir %{_sysconfdir}/gconf/gconf.xml*
%dir %{_sysconfdir}/gconf/schemas
%{_datadir}/polkit-1/actions/org.gnome.gconf.defaults.policy
%{_datadir}/sgml/gconf
%{_datadir}/GConf
%{_datadir}/dbus-1/services/org.gnome.GConf.service
%{_datadir}/dbus-1/system-services/org.gnome.GConf.Defaults.service
%{_var}/lib/rpm/filetriggers/gconf-schemas.*

# (blino) split gconf-sanity-check not to require gtk in GConf2
%files sanity-check
%{_libexecdir}/gconf-sanity-check-%{api_version}

%files -n %{lib_name}
%defattr(-, root, root)
%doc README
%{_libdir}/lib*.so.*
%_libdir/gio/modules/libgsettingsgconfbackend.so
%_libdir/gio/modules/libgsettingsgconfbackend.la
%_libdir/girepository-1.0/GConf-2.0.typelib

%files -n %{lib_namedev}
%defattr (-, root, root)
%doc ChangeLog TODO NEWS AUTHORS
%doc %{_datadir}/gtk-doc/html/*
%{_datadir}/aclocal/*
%{_includedir}/*
%{_libdir}/*.so
%attr(644,root,root) %{_libdir}/*a
%{_libdir}/pkgconfig/*
%attr(644,root,root) %{_libdir}/GConf/%{api_version}/*.la
%_datadir/gir-1.0/GConf-2.0.gir


