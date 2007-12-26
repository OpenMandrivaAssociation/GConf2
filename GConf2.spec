%define pkgname		GConf
%define api_version	2
%define	lib_major	4
%define lib_name	%mklibname %{name}_ %{lib_major}
%define lib_namedev	%mklibname -d %{name}

# Version of required packages
%define req_orbit_version	2.4.0
%define req_glib_version	2.9.1

Summary:	A configuration database system for GNOME 2
Name:		%{pkgname}%{api_version}
Version: 2.20.1
Release:	%mkrel 3
License:	LGPL
Group:		Graphical desktop/GNOME
URL:		http://www.gnome.org/projects/gconf/
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

Source0: 	ftp://ftp.gnome.org/pub/GNOME/sources/%{pkgname}/%{pkgname}-%{version}.tar.bz2
Source1:	gconf.sh
Source2:	gconf.csh
# (fc) add GCONF_TMPDIR variable to use a different dir than TMPDIR for locking (Mdk bug 6140) (GNOME bug #497113)
Patch0:		GConf-2.4.0-tmpdir.patch
# (fc) reload database when schemas are installed/uninstalled (GNOME bug #328697)
Patch1:		GConf-2.12.1-reload.patch
Conflicts:	GConf < 1.0.6
BuildRequires:  libglib2.0-devel >= %{req_glib_version}
BuildRequires:	libxml2-devel
BuildRequires:	libgtk+2-devel
BuildRequires:	libORBit2-devel >= %{req_orbit_version}
BuildRequires:  autoconf2.5
BuildRequires:  gtk-doc
BuildRequires:  perl-XML-Parser
BuildRequires:	libldap-devel
Requires:	%{lib_name} = %{version}
# needed by patch1
Requires:	psmisc

%description
GConf is a configuration data storage mechanism scheduled to
ship with GNOME 2.0. GConf does work without GNOME however; it
can be used with plain GTK+, Xlib, KDE, or even text mode
applications as well.


%package -n %{lib_name}
Summary:	%{summary}
Group:		%{group}
Provides:	lib%{name} >= %{version}-%{release}
Requires:  	%{name} >= %{version}
Requires:	libORBit2 >= %{req_orbit_version}

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
Requires:	libORBit2-devel
Requires:	libglib2-devel >= %{req_glib_version}
Obsoletes: %mklibname -d %{name}_ 4

%description -n %{lib_namedev}
GConf is a configuration data storage mechanism scheduled to
ship with GNOME 2.0. GConf does work without GNOME however; it
can be used with plain GTK+, Xlib, KDE, or even text mode
applications as well.

This package contains the header files and libraries needed to develop
applications using GConf.

%prep
%setup -q -n %{pkgname}-%{version}
%patch0 -p1 -b .tmpdir
%patch1 -p1 -b .reload

%build

%configure2_5x --enable-gtk-doc

%make

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

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/gconf/{gconf.xml.local-defaults,gconf.xml.local-mandatory}

cat << EOF > $RPM_BUILD_ROOT%{_sysconfdir}/gconf/2/local-defaults.path
xml:readonly:/etc/gconf/gconf.xml.local-defaults
include "\$(HOME)/.gconf.path.defaults"
EOF

cat << EOF > $RPM_BUILD_ROOT%{_sysconfdir}/gconf/2/local-mandatory.path
xml:readonly:/etc/gconf/gconf.xml.local-mandatory
include "\$(HOME)/.gconf.path.mandatory"
EOF

%{find_lang} %{name}

# remove unpackaged files
rm -f $RPM_BUILD_ROOT%{_libdir}/GConf/%{api_version}/*.a

%clean
rm -rf %{buildroot}

# remove buggy symlink
%post
update-alternatives --install %{_bindir}/gconftool gconftool /usr/bin/gconftool-%{api_version} 20
if [ "$1" = "2" ]; then 
		update-alternatives --auto gconftool
fi

%post -n %{lib_name} -p /sbin/ldconfig
%postun -n %{lib_name} -p /sbin/ldconfig

%files -f %{name}.lang
%defattr(-, root, root)
%doc README
%config(noreplace) %{_sysconfdir}/profile.d/*
%{_bindir}/gconftool*
%{_bindir}/gconf-merge-tree
%_mandir/man1/gconftool-2.1*
%if "%{_lib}" != "lib"
%{_prefix}/lib/gconfd-%{api_version}
%endif
%{_libexecdir}/gconfd-%{api_version}
%{_libexecdir}/gconf-sanity-check-%{api_version}
%dir %{_libdir}/GConf
%dir %{_libdir}/GConf/%{api_version}
%{_libdir}/GConf/%{api_version}/*.so
%config(noreplace) %{_sysconfdir}/gconf/%{api_version}
%dir %{_sysconfdir}/gconf
%dir %{_sysconfdir}/gconf/gconf.xml*
%dir %{_sysconfdir}/gconf/schemas
%{_datadir}/sgml/gconf
%{_datadir}/GConf

%files -n %{lib_name}
%defattr(-, root, root)
%doc README
%{_libdir}/lib*.so.*

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


