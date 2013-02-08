%define pkgname GConf

%define api 2
%define gi_version 2.0
%define major 4
%define libname %mklibname %{pkgname} %{api} %{major}
%define girname %mklibname gconf-gir %{gi_version}
%define develname %mklibname -d %{pkgname} %{api}

%define url_ver %(echo %{version} | cut -d. -f1,2)

Summary:	A configuration database system for GNOME
Name:		%{pkgname}%{api}
Version:	3.2.6
Release:	1
License:	LGPLv2+
Group:		Graphical desktop/GNOME
URL:		http://www.gnome.org/projects/gconf/
Source0:	http://download.gnome.org/sources/%{pkgname}/%{url_ver}/%{pkgname}-%{version}.tar.xz
Source1:	gconf.sh
Source2:	gconf.csh
Source3:	gconf-schemas.filter
Source4:	gconf-schemas.script
# (fc) reload database when schemas are installed/uninstalled (GNOME bug #328697)
Patch1:		GConf-2.12.1-reload.patch

BuildRequires:	gtk-doc
BuildRequires:	intltool
BuildRequires:	openldap-devel
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(dbus-glib-1)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(gtk+-3.0)
BuildRequires:	pkgconfig(gobject-introspection-1.0)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(polkit-gobject-1)
Requires:	polkit-agent
Requires:	gsettings-desktop-schemas
# needed by patch1
Requires:	psmisc
Requires:	sed
Requires(post):	update-alternatives
Requires:	%{girname} = %{version}-%{release}
Suggests:	dconf

%description
GConf is a configuration data storage mechanism scheduled to
ship with GNOME. GConf does work without GNOME however; it
can be used with plain GTK+, Xlib, KDE, or even text mode
applications as well.

%package -n %{libname}
Summary:	%{summary}
Group:		System/Libraries
Conflicts:	gir-repository < 0.6.5-12

%description -n %{libname}
GConf is a configuration data storage mechanism scheduled to
ship with GNOME. GConf does work without GNOME however; it
can be used with plain GTK+, Xlib, KDE, or even text mode
applications as well.

This package contains necessary libraries to run any programs linked
with GConf.

%package -n %{girname}
Summary:	GObject introspection interface library for %{pkgname}
Group:		System/Libraries

%description -n %{girname}
GObject introspection interface library for %{pkgname}.

%package -n %{develname}
Summary:	Development libraries and headers for GConf
Group:		Development/GNOME and GTK+
Provides:	lib%{name}-devel = %{version}-%{release}
Requires:	%{libname} = %{version}-%{release}
Requires:	%{name} = %{version}-%{release}
Conflicts:	gir-repository < 0.6.5-12

%description -n %{develname}
GConf is a configuration data storage mechanism scheduled to
ship with GNOME. GConf does work without GNOME however; it
can be used with plain GTK+, Xlib, KDE, or even text mode
applications as well.

This package contains the header files and libraries needed to develop
applications using GConf.

%prep
%setup -q -n %{pkgname}-%{version}
%apply_patches

%build
%configure2_5x \
	--with-gtk=3.0 \
	--disable-static \
	--disable-orbit

%make

%install
%makeinstall_std

mkdir -p %{buildroot}%{_sysconfdir}/profile.d
install -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/profile.d/gconf.sh
install -m 755 %{SOURCE2} %{buildroot}%{_sysconfdir}/profile.d/gconf.csh

mkdir %{buildroot}%{_sysconfdir}/gconf/schemas

# Provide /usr/lib/gconfd-2 symlink on lib64 platforms
%if "%{_lib}" != "lib"
mkdir -p %{buildroot}%{_prefix}/lib
ln -s ../%{_lib}/gconfd-%{api} %{buildroot}%{_prefix}/lib/gconfd-%{api}
%endif

mkdir -p %{buildroot}%{_sysconfdir}/gconf/{gconf.xml.local-defaults,gconf.xml.local-mandatory,gconf.xml.system}

cat << EOF > %{buildroot}%{_sysconfdir}/gconf/2/local-defaults.path
xml:readonly:/etc/gconf/gconf.xml.local-defaults
include "\$(HOME)/.gconf.path.defaults"
EOF

cat << EOF > %{buildroot}%{_sysconfdir}/gconf/2/local-mandatory.path
xml:readonly:/etc/gconf/gconf.xml.local-mandatory
include "\$(HOME)/.gconf.path.mandatory"
EOF

# automatic install of gconf schemas on rpm installs
# (see http://wiki.mandriva.com/en/Rpm_filetriggers)
install -d %{buildroot}%{_var}/lib/rpm/filetriggers
install -m 644 %{SOURCE3} %{buildroot}%{_var}/lib/rpm/filetriggers
install -m 755 %{SOURCE4} %{buildroot}%{_var}/lib/rpm/filetriggers

%{find_lang} %{name}

# remove buggy symlink
%post
update-alternatives --install %{_bindir}/gconftool gconftool /usr/bin/gconftool-%{api} 20
if [ "$1" = "2" ]; then 
		update-alternatives --auto gconftool
fi

%triggerpostun -- GConf2 < 2.22.0-4
GCONF_CONFIG_SOURCE=`%{_bindir}/gconftool-2 --get-default-source` %{_bindir}/gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/*.schemas > /dev/null

%files -f %{name}.lang
%doc README
%dir %{_libdir}/GConf
%dir %{_libdir}/GConf/%{api}
%dir %{_sysconfdir}/gconf
%dir %{_sysconfdir}/gconf/gconf.xml*
%dir %{_sysconfdir}/gconf/schemas
%config(noreplace) %{_sysconfdir}/profile.d/*
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.gnome.GConf.Defaults.conf
%config(noreplace) %{_sysconfdir}/gconf/%{api}
%{_sysconfdir}/xdg/autostart/gsettings-data-convert.desktop
%{_bindir}/gsettings-data-convert
%{_bindir}/gconftool*
%{_bindir}/gconf-merge-tree
%{_mandir}/man1/gconftool-2.1*
%{_mandir}/man1/gsettings-data-convert.1*
%if "%{_lib}" != "lib"
%{_prefix}/lib/gconfd-%{api}
%endif
%{_libexecdir}/gconfd-%{api}
%{_libexecdir}/gconf-defaults-mechanism
%{_libdir}/GConf/%{api}/*.so
%{_libdir}/gio/modules/libgsettingsgconfbackend.so
%{_datadir}/polkit-1/actions/org.gnome.gconf.defaults.policy
%{_datadir}/sgml/gconf
%{_datadir}/GConf
%{_datadir}/dbus-1/services/org.gnome.GConf.service
%{_datadir}/dbus-1/system-services/org.gnome.GConf.Defaults.service
%{_var}/lib/rpm/filetriggers/gconf-schemas.*

%files -n %{libname}
%{_libdir}/lib*.so.%{major}*

%files -n %{girname}
%{_libdir}/girepository-1.0/GConf-%{gi_version}.typelib

%files -n %{develname}
%doc ChangeLog TODO NEWS AUTHORS
%doc %{_datadir}/gtk-doc/html/*
%{_bindir}/gsettings-schema-convert
%{_datadir}/aclocal/*
%{_datadir}/gir-1.0/GConf-%{gi_version}.gir
%{_includedir}/gconf/
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%{_mandir}/man1/gsettings-schema-convert.1*


