%define pkgname	GConf

%define api	2
%define gi_version	2.0
%define major	4
%define libname	%mklibname %{pkgname} %{api} %{major}
%define girname	%mklibname gconf-gir %{gi_version}
%define develname	%mklibname -d %{pkgname} %{api}

%define url_ver %(echo %{version} | cut -d. -f1,2)

Summary:	A configuration database system for GNOME
Name:		%{pkgname}%{api}
Version:	3.2.5
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

%package sanity-check
Summary:	Sanity checker for %{pkgname}%{api}
Group:		%{group}

%description sanity-check
gconf-sanity-check is a tool to check the sanity of a %{pkgname}%{api}
installation.

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

# (blino) split gconf-sanity-check not to require gtk in GConf2
%files sanity-check
%{_libexecdir}/gconf-sanity-check-%{api}

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



%changelog
* Wed Apr 25 2012 Matthew Dawkins <mattydaw@mandriva.org> 3.2.5-1
+ Revision: 793266
- new version 3.2.5

* Mon Dec 05 2011 ZÃ© <ze@mandriva.org> 3.2.3-4
+ Revision: 737999
- clean duplicated buildrequires
- modules need to installed with gconf
- rebuild

* Mon Nov 21 2011 GÃ¶tz Waschk <waschk@mandriva.org> 3.2.3-3
+ Revision: 732127
- readd dep on main package to devel package

* Tue Nov 15 2011 Matthew Dawkins <mattydaw@mandriva.org> 3.2.3-2
+ Revision: 730765
- rebuild
  cleaned up spec
  removed req by lib & devel for main pkg, removes dep loop
  moved module from lib to main pkg
  removed old conflicts & obsoletes
  changed lib_namedev to develname
  organized files list for readability
  removed dup README from lib pkg

* Thu Nov 10 2011 Matthew Dawkins <mattydaw@mandriva.org> 3.2.3-1
+ Revision: 729903
- new version 3.2.3
  sync'd spec with mga
  removed defattr
  removed clean section
  removed mdv from releases
  converted RPM_BUILD_ROOT to buildroot

* Fri Jul 01 2011 GÃ¶tz Waschk <waschk@mandriva.org> 2.32.5-1
+ Revision: 688527
- new version

* Thu Jun 16 2011 GÃ¶tz Waschk <waschk@mandriva.org> 2.32.4-1
+ Revision: 685638
- new version
- xz tarball

* Sun May 22 2011 Funda Wang <fwang@mandriva.org> 2.32.3-2
+ Revision: 677054
- add req on gconf-tool to  devel package

* Tue Apr 26 2011 Funda Wang <fwang@mandriva.org> 2.32.3-1
+ Revision: 659097
- update to new version 2.32.3

* Sun Apr 10 2011 GÃ¶tz Waschk <waschk@mandriva.org> 2.32.2-2
+ Revision: 652283
- depend on gsettings-desktop-schemas

* Mon Apr 04 2011 GÃ¶tz Waschk <waschk@mandriva.org> 2.32.2-1
+ Revision: 650300
- new version

* Tue Mar 22 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 2.32.1-2
+ Revision: 647699
- drop invalid provides for library package
- fix dependency loop

  + Funda Wang <fwang@mandriva.org>
    - drop unused requires

* Sun Mar 13 2011 Funda Wang <fwang@mandriva.org> 2.32.1-1
+ Revision: 644139
- New version 2.32.1
- build with gtk2.0 for now

* Sat Feb 26 2011 Funda Wang <fwang@mandriva.org> 2.32.0-4
+ Revision: 639956
- drop gio module hackup

* Wed Feb 16 2011 Per Ã˜yvind Karlsen <peroyvind@mandriva.org> 2.32.0-3
+ Revision: 637995
- revert back to using legacy mandriva file triggers for now

* Mon Feb 14 2011 GÃ¶tz Waschk <waschk@mandriva.org> 2.32.0-2
+ Revision: 637706
- new version

  + Funda Wang <fwang@mandriva.org>
    - convert rpm file trigger into rpm5 standard trigger

* Mon Sep 27 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.32.0-1mdv2011.0
+ Revision: 581439
- update to new version 2.32.0

* Mon Sep 13 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.31.91-3mdv2011.0
+ Revision: 577925
- rebuild for new g-i
- fix postun script

* Tue Aug 31 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.31.91-2mdv2011.0
+ Revision: 574656
- add scripts for gio modules

* Mon Aug 30 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.31.91-1mdv2011.0
+ Revision: 574500
- update to new version 2.31.91

* Thu Aug 05 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.31.7-1mdv2011.0
+ Revision: 566129
- new version
- bump glib dep
- drop patch 2

* Fri Jul 30 2010 Funda Wang <fwang@mandriva.org> 2.31.6-1mdv2011.0
+ Revision: 563737
- add patch from upstream to build with latest glib

  + GÃ¶tz Waschk <waschk@mandriva.org>
    - new version
    - bump glib dep
    - enable introspection support

* Tue Mar 30 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.28.1-1mdv2010.1
+ Revision: 529660
- update to new version 2.28.1

* Tue Mar 16 2010 Oden Eriksson <oeriksson@mandriva.com> 2.28.0-2mdv2010.1
+ Revision: 521834
- rebuilt for 2010.1

* Tue Sep 22 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.28.0-1mdv2010.0
+ Revision: 447372
- update to new version 2.28.0
- depend on polkit-agent

* Tue Aug 25 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.27.0-1mdv2010.0
+ Revision: 421071
- new version
- use new polkit

* Tue Jun 30 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.26.2-2mdv2010.0
+ Revision: 390831
- update devel deps

* Fri May 15 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.26.2-1mdv2010.0
+ Revision: 375884
- update to new version 2.26.2

* Wed May 06 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.26.1-1mdv2010.0
+ Revision: 372385
- update to new version 2.26.1

* Tue Mar 17 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.26.0-1mdv2009.1
+ Revision: 356488
- update to new version 2.26.0

* Tue Feb 17 2009 Frederic Crozat <fcrozat@mandriva.com> 2.25.2-2mdv2009.1
+ Revision: 341433
- Package /etc/gconf/gconf.xml.system (Mdv bug #47867)

* Tue Feb 17 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.25.2-1mdv2009.1
+ Revision: 341231
- update to new version 2.25.2

* Sun Feb 15 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.25.1-1mdv2009.1
+ Revision: 340501
- update to new version 2.25.1

* Sat Jan 10 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.25.0-1mdv2009.1
+ Revision: 327959
- update to new version 2.25.0

* Mon Sep 22 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.24.0-1mdv2009.0
+ Revision: 286841
- new version

* Thu Aug 28 2008 Frederic Crozat <fcrozat@mandriva.com> 2.23.2-2mdv2009.0
+ Revision: 276868
- Reinstall all schemas if upgrading from 2008.1 or older, filetriggers might have been installed too late during the upgrade

* Tue Aug 19 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.23.2-1mdv2009.0
+ Revision: 273776
- new version
- update file list
- update build deps

* Tue Jul 08 2008 Olivier Blin <blino@mandriva.org> 2.23.1-2mdv2009.0
+ Revision: 232738
- explicitely require sed for filetrigger script (so that it is available when used by installer)

* Thu Jul 03 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.23.1-1mdv2009.0
+ Revision: 230996
- fix license
- new version
- drop patch 0
- update buildrequires
- update file list

* Wed Jun 11 2008 Pixel <pixel@mandriva.com> 2.22.0-4mdv2009.0
+ Revision: 217906
- add rpm filetrigger running "gconftool-2 --makefile-install-rule" when rpm install gconf schemas
- do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Mon Mar 31 2008 Anssi Hannula <anssi@mandriva.org> 2.22.0-3mdv2008.1
+ Revision: 191330
- post script requires update-alternatives

* Tue Mar 25 2008 Emmanuel Andry <eandry@mandriva.org> 2.22.0-2mdv2008.1
+ Revision: 189891
- Fix lib group

* Mon Mar 10 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.22.0-1mdv2008.1
+ Revision: 183578
- new version

* Wed Feb 27 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.21.90-4mdv2008.1
+ Revision: 175697
- add conflict to the sanity check package for upgrades

* Wed Feb 27 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.21.90-3mdv2008.1
+ Revision: 175666
- make the devel package depend on the sanity check package

* Mon Feb 25 2008 Olivier Blin <blino@mandriva.org> 2.21.90-2mdv2008.1
+ Revision: 174924
- split gconf-sanity-check in a GConf2-sanity-check package not to require gtk in GConf2

* Mon Jan 28 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.21.90-1mdv2008.1
+ Revision: 159229
- new version

* Tue Jan 22 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.21.2-1mdv2008.1
+ Revision: 156128
- new version
- drop patch 2

* Thu Jan 10 2008 Marcelo Ricardo Leitner <mrl@mandriva.com> 2.21.1-2mdv2008.1
+ Revision: 147575
- Disable regenerating the docs for now, as texpdf is looping itself.
- Added patch pkgconfig, to make it not require glib1 but glib2 instead.
  Same fix as in http://svn.gnome.org/viewvc/gconf/trunk/gconf-2.0.pc.in?r1=2505&r2=2506

* Tue Jan 08 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.21.1-1mdv2008.1
+ Revision: 146812
- new version

* Wed Dec 26 2007 Oden Eriksson <oeriksson@mandriva.com> 2.20.1-3mdv2008.1
+ Revision: 137942
- rebuilt against openldap-2.4.7 libs

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Thu Nov 15 2007 Frederic Crozat <fcrozat@mandriva.com> 2.20.1-2mdv2008.1
+ Revision: 108932
- Enable parallel build
- Add bug numbers for upstream merge request

* Mon Oct 15 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.20.1-1mdv2008.1
+ Revision: 98393
- new version

* Wed Sep 19 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.20.0-1mdv2008.0
+ Revision: 90874
- new version
- new devel name

* Sat Jun 23 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.19.1-1mdv2008.0
+ Revision: 43464
- new version


* Mon Mar 05 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.18.0.1-1mdv2007.0
+ Revision: 133279
- new version
- drop merged patch 2

* Mon Mar 05 2007 Frederic Crozat <fcrozat@mandriva.com> 2.18.0-2mdv2007.1
+ Revision: 133183
-bunzip patches and relevant sources
-Patch2: always rename markup tree files (Mdv bug #29139, GNOME bug #414916)

* Sun Mar 04 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.18.0-1mdv2007.1
+ Revision: 132016
- new version

* Mon Feb 26 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.16.1-1mdv2007.1
+ Revision: 126054
- new version
- Import GConf2

  + Christiaan Welvaart <cjw@daneel.dyndns.org>
    - rebuild to fix source rpm distro tag

* Tue Oct 10 2006 Götz Waschk <waschk@mandriva.org> 2.16.0-1mdv2007.1
- fix buildrequires
- New version 2.16.0

* Sat Sep 09 2006 Frederic Crozat <fcrozat@mandriva.com> 2.14.0-3mdv2007.0
- Fix bad dependencies caused by profile scripts

* Fri Aug 11 2006 Frederic Crozat <fcrozat@mandriva.com> 2.14.0-2mdv2007.0
- Add local.defaults/mandatory files

* Tue Apr 11 2006 Frederic Crozat <fcrozat@mandriva.com> 2.14.0-1mdk
- Release 2.14.0

* Mon Feb 27 2006 Götz Waschk <waschk@mandriva.org> 2.12.1-4mdk
- fix rpmlint warnings

* Mon Feb 27 2006 Frederic Crozat <fcrozat@mandriva.com> 2.12.1-3mdk
- Regenerate patch1, it wasn't applying correctly

* Thu Feb 23 2006 Frederic Crozat <fcrozat@mandriva.com> 2.12.1-2mdk
- Use mkrel

* Thu Nov 03 2005 GÃ¶tz Waschk <waschk@mandriva.org> 2.12.1-1mdk
- New release 2.12.1

* Mon Oct 10 2005 Christiaan Welvaart <cjw@daneel.dyndns.org> 2.12.0-2mdk
- add BuildRequires: libldap-devel

* Wed Oct 05 2005 Frederic Crozat <fcrozat@mandriva.com> 2.12.0-1mdk
- Release 2.10.0

* Thu Jul 28 2005 Götz Waschk <waschk@mandriva.org> 2.10.1-2mdk
- readd dropped dep on GConf2 to the library package

* Thu Jul 07 2005 Götz Waschk <waschk@mandriva.org> 2.10.1-1mdk
- remove prereq
- New release 2.10.1

* Thu Apr 21 2005 Frederic Crozat <fcrozat@mandriva.com> 2.10.0-1mdk 
- Release 2.10.0 (based on Götz Waschk package)
- Remove patch2 (merged upstream)

* Mon Feb 07 2005 Frederic Crozat <fcrozat@mandrakesoft.com> 2.8.1-3mdk 
- Patch2 (CVS): various bug fixes from CVS

* Fri Jan 07 2005 Frederic Crozat <fcrozat@mandrakesoft.com> 2.8.1-2mdk 
- Patch1: force reload database when schemas are installed/uninstalled

* Tue Nov 09 2004 Götz Waschk <waschk@linux-mandrake.com> 2.8.1-1mdk
- disable parallel build
- drop merged patch 1
- New release 2.8.1

* Wed Nov 03 2004 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 2.6.4-2.1mdk
- Provide /usr/lib/gconfd-2 symlink on lib64 platforms

* Thu Sep 09 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 2.6.4-2mdk 
- Update patch1 with CVS bugfix

* Fri Aug 27 2004 Goetz Waschk <waschk@linux-mandrake.com> 2.6.4-1mdk
- New release 2.6.4

* Tue Jul 27 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 2.6.3-2mdk
- Patch1 (CVS): backport handling of SIGHUP to force reloading all databases

* Sat Jul 03 2004 Goetz Waschk <waschk@linux-mandrake.com> 2.6.3-1mdk
- New release 2.6.3

* Wed Jun 16 2004 Götz Waschk <waschk@linux-mandrake.com> 2.6.2-1mdk
- reenable libtoolize
- New release 2.6.2

* Wed Apr 21 2004 Goetz Waschk <goetz@mandrakesoft.com> 2.6.1-1mdk
- New release 2.6.1

* Tue Apr 06 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 2.6.0-1mdk
- Release 2.6.0 (with Götz Waschk help)
- update doc life list
- add new files

