%define modname eaccelerator
%define dirname %{modname}
%define soname %{modname}.so
%define inifile Z99_%{modname}.ini

Summary:	PHP accelerator optimizer
Name:		php-eaccelerator
Version:	0.9.6.1git20120725
Release:	12
Group:		Development/PHP
License:	GPL
URL:		http://eaccelerator.net/
# svn --username anonymous --password anonymous co http://dev.eaccelerator.net/eaccelerator/trunk eaccelerator
Source0:	http://prdownloads.sourceforge.net/eaccelerator/eaccelerator-%{version}.tar.gz
Source1:	eaccelerator.ini
Source2:	php-eaccelerator.rpmlintrc
Patch0:		eaccelerator-cache_file_location.diff
Requires(post): rpm-helper
Requires(postun): rpm-helper
BuildRequires:	php-devel >= 3:5.2.2
BuildRequires:	apache-devel >= 2.2.4
Conflicts:	php-afterburner php-apc %{name}-eloader
Epoch:		2
ExcludeArch:	%mips %arm

%description
eAccelerator is a further development of the mmcache PHP accelerator and
encoder. It increases the performance of PHP scripts by caching them in a
compiled state, so that the overhead of compiling is almost completely
eliminated. 

%package	admin
Summary:	Web interface for controlling eaccelerator and encode php files
Group:		System/Servers
Requires:	%{name} >= %{epoch}:%{version}
Conflicts:	%{name}-eloader
Epoch:		%{epoch}

%description	admin
This packages install the eAccelerator admin webinterface and a
script for encoding php files.

%prep

%setup -q -n eaccelerator-%{version}
%patch0 -p1 -b .cache_file_location

cp %{SOURCE1} eaccelerator.ini

# lib64 fixes
perl -pi -e "s|/usr/lib|%{_libdir}|g" eaccelerator.ini

# fixi strange attribs
find . -type d -exec chmod 755 {} \;
find . -type f -exec chmod 644 {} \;

%build
%serverbuild

phpize

# wtf?
chmod 755 configure

%configure2_5x \
    --with-libdir=%{_lib} \
    --cache-file=config.cache \
    --with-eaccelerator-info \
    --with-eaccelerator-disassembler \
    --with-%{modname}=shared,%{_prefix}

%make
mv modules/*.so .

%install
install -d %{buildroot}%{_libdir}/php/extensions
install -d %{buildroot}%{_sysconfdir}/php.d
install -d %{buildroot}/var/www/php-eaccelerator

install -m0755 %{soname} %{buildroot}%{_libdir}/php/extensions/

install -m0644 eaccelerator.ini %{buildroot}%{_sysconfdir}/php.d/%{inifile}

install -m0644 bugreport.php %{buildroot}/var/www/php-eaccelerator/
install -m0644 control.php %{buildroot}/var/www/php-eaccelerator/index.php
install -m0644 dasm.php %{buildroot}/var/www/php-eaccelerator/
install -m0644 PHP_Highlight.php %{buildroot}/var/www/php-eaccelerator/

# fix access config files
install -d -m 755 %{buildroot}%{_webappconfdir}
cat > %{buildroot}%{_webappconfdir}/php-eaccelerator.conf << EOF
Alias /php-eaccelerator /var/www/php-eaccelerator

<Directory /var/www/php-eaccelerator>
    Require host 127.0.0.1
    ErrorDocument 403 "Access denied per %{_webappconfdir}/php-eaccelerator.conf"
</Directory>
EOF

# pre-populate the balanced tree, grep "^static char num2hex" eaccelerator.c + grep "^#define EACCELERATOR_HASH_LEVEL" eaccelerator.h
install -d %{buildroot}/var/cache/httpd/php-eaccelerator/{0,1,2,3,4,5,6,7,8,9,a,b,c,d,e,f}/{0,1,2,3,4,5,6,7,8,9,a,b,c,d,e,f}
find %{buildroot}/var/cache/httpd/php-eaccelerator -type d | sed -e "s|%{buildroot}||" | sed -e 's/^/%attr(0711,apache,root) %dir /' > %{name}.filelist


%files -f %{name}.filelist
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog NEWS README doc/*
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/php.d/%{inifile}
%attr(0755,root,root) %{_libdir}/php/extensions/%{soname}

%files admin
%defattr(-,root,root)
%config(noreplace) %{_webappconfdir}/php-eaccelerator.conf
%dir /var/www/php-eaccelerator
/var/www/php-eaccelerator/*


%changelog
* Wed Aug 24 2011 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6.1-9mdv2011.0
+ Revision: 696368
- rebuilt for php-5.3.8

* Fri Aug 19 2011 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6.1-8
+ Revision: 695312
- rebuilt for php-5.3.7

* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6.1-7
+ Revision: 667478
- mass rebuild

* Sat Mar 19 2011 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6.1-6
+ Revision: 646552
- rebuilt for php-5.3.6

* Sat Jan 08 2011 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6.1-5mdv2011.0
+ Revision: 629737
- rebuilt for php-5.3.5

* Mon Jan 03 2011 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6.1-4mdv2011.0
+ Revision: 628043
- ensure it's built without automake1.7

* Tue Nov 23 2010 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6.1-3mdv2011.0
+ Revision: 600175
- rebuild

* Sun Oct 24 2010 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6.1-2mdv2011.0
+ Revision: 588712
- rebuild

* Tue Jun 15 2010 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6.1-1mdv2010.1
+ Revision: 548060
- 0.9.6.1

* Fri Mar 05 2010 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6-1mdv2010.1
+ Revision: 514497
- 0.9.6

* Mon Feb 22 2010 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6-0.358.10mdv2010.1
+ Revision: 509465
- rebuild
- rebuild

* Mon Feb 08 2010 Guillaume Rousse <guillomovitch@mandriva.org> 2:0.9.6-0.358.8mdv2010.1
+ Revision: 502376
- affect post-installation dependencies to admin supackage only
- rely on filetrigger for reloading apache configuration begining with 2010.1, rpm-helper macros otherwise

* Sat Jan 02 2010 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6-0.358.6mdv2010.1
+ Revision: 485256
- rebuilt for php-5.3.2RC1

* Sat Nov 21 2009 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6-0.358.5mdv2010.1
+ Revision: 468083
- rebuilt against php-5.3.1

* Wed Sep 30 2009 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6-0.358.4mdv2010.0
+ Revision: 451213
- rebuild

* Sun Sep 27 2009 Olivier Blin <blino@mandriva.org> 2:0.9.6-0.358.3mdv2010.0
+ Revision: 450271
- do not build on mips & arm (from Arnaud Patard)

* Tue Sep 01 2009 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6-0.358.2mdv2010.0
+ Revision: 423567
- fix #53263 (If installed, php-eaccelerator broke httpd.)

* Sun Aug 30 2009 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6-0.358.1mdv2010.0
+ Revision: 422382
- new svn snap (r358)
- update eaccelerator.ini slightly

* Sun Jul 19 2009 Raphaël Gertz <rapsys@mandriva.org> 2:0.9.6-0.356.2mdv2010.0
+ Revision: 397511
- Rebuild

* Fri Jul 10 2009 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6-0.356.1mdv2010.0
+ Revision: 394232
- new svn snap (r356)

* Wed May 13 2009 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.6-0.355.1mdv2010.0
+ Revision: 375429
- use a more recent svn snapshot
- rebuilt against php-5.3.0RC2

* Sun Mar 01 2009 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.3-8mdv2009.1
+ Revision: 346417
- rebuilt for php-5.2.9

* Wed Feb 25 2009 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.3-7mdv2009.1
+ Revision: 344656
- rebuild (fixes #48187)

* Tue Feb 17 2009 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.3-6mdv2009.1
+ Revision: 341504
- rebuilt against php-5.2.9RC2

* Mon Feb 16 2009 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.3-5mdv2009.1
+ Revision: 340734
- rebuild (fixes #47862)

* Wed Dec 31 2008 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.3-4mdv2009.1
+ Revision: 321730
- rebuild

* Fri Dec 05 2008 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.3-3mdv2009.1
+ Revision: 310214
- rebuilt against php-5.2.7

* Tue Dec 02 2008 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.3-2mdv2009.1
+ Revision: 309247
- rebuild

* Sat Aug 16 2008 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.3-1mdv2009.0
+ Revision: 272604
- fix build
- 0.9.5.3

* Tue Jul 15 2008 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.2-6mdv2009.0
+ Revision: 235815
- rebuild

* Fri May 02 2008 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.2-5mdv2009.0
+ Revision: 200105
- rebuilt against php-5.2.6

* Tue Feb 12 2008 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.2-4mdv2008.1
+ Revision: 166098
- provide the balanced tree structure

* Mon Feb 04 2008 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.2-3mdv2008.1
+ Revision: 161958
- rebuild

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sun Nov 11 2007 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.2-2mdv2008.1
+ Revision: 107560
- restart apache if needed

* Tue Oct 30 2007 Funda Wang <fwang@mandriva.org> 2:0.9.5.2-1mdv2008.1
+ Revision: 103705
- update to new version 0.9.5.2

* Mon Sep 17 2007 Olivier Blin <blino@mandriva.org> 2:0.9.5.1-7mdv2008.0
+ Revision: 89135
- rebuild because of package loss

* Sat Sep 01 2007 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.1-6mdv2008.0
+ Revision: 77453
- rebuilt against php-5.2.4

* Thu Aug 16 2007 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.1-5mdv2008.0
+ Revision: 64297
- use the new %%serverbuild macro

* Thu Jun 21 2007 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.1-4mdv2008.0
+ Revision: 42289
- fix #31403

* Thu Jun 14 2007 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.1-3mdv2008.0
+ Revision: 39378
- use distro conditional -fstack-protector

* Fri Jun 01 2007 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.1-2mdv2008.0
+ Revision: 33773
- rebuilt against new upstream version (5.2.3)

* Tue May 08 2007 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.1-1mdv2008.0
+ Revision: 25045
- Import php-eaccelerator



* Tue May 08 2007 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5.1-1mdv2008.0
- 0.9.5.1
- drop upstream patches; P1

* Thu Feb 08 2007 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5-6mdv2007.0
- rebuilt against new upstream version (5.2.1)

* Fri Jan 12 2007 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5-5mdv2007.1
- rediffed P1
- sync with fc extras (P1)

* Sun Dec 10 2006 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5-4mdv2007.1
- add one missing file (PHP_Highlight.php)

* Wed Nov 08 2006 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5-3mdv2007.0
- fix deps
- fix a better error 404 message

* Tue Nov 07 2006 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5-2mdv2007.1
- rebuilt for php-5.2.0

* Thu Nov 02 2006 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5-1mdv2007.1
- 0.9.5
- drop the eloader and encoder stuff
- rediffed P0
- bunzip sources

* Thu Oct 12 2006 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5-0.rc1.1mdv2007.1
- Import php-eaccelerator

* Mon Aug 28 2006 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5-0.rc1.1
- rebuilt for php-5.1.6

* Fri Aug 11 2006 Oden Eriksson <oeriksson@mandriva.com> 1:0.9.5-4.rc1.3mdk
- really use the right cache dir in S1
- added bugreport.php in S2

* Fri Aug 11 2006 Oden Eriksson <oeriksson@mandriva.com> 1:0.9.5-4.rc1.2mdk
- add some missing files

* Mon Aug 07 2006 Oden Eriksson <oeriksson@mandriva.com> 1:0.9.5-4.rc1.1mdk
- 0.9.5-rc1

* Thu Jul 27 2006 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5-2.beta2.2mdk
- rebuild

* Sat May 06 2006 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5-1.beta2.2mdk
- rebuilt for php-5.1.4

* Fri May 05 2006 Oden Eriksson <oeriksson@mandriva.com> 2:0.9.5-0.beta2.2mdk
- rebuilt for php-5.1.3

* Tue Apr 25 2006 Oden Eriksson <oeriksson@mandriva.com> 1:0.9.5-0.beta2.1mdk
- 0.9.5-beta2

* Wed Mar 22 2006 Oden Eriksson <oeriksson@mandriva.com> 1:0.9.5-0.beta1.2mdk
- fix the webapps dir location, oops!

* Thu Sep 08 2005 Oden Eriksson <oeriksson@mandriva.com> 1:0.9.5-0.beta1.1mdk
- 0.9.5-beta1
- phpcoder-1.5
- rediffed P1
- deactivate the hardened patch as it won't apply
- fix versioning
- drop the /admin/ location and use the webapps policy

* Thu Sep 08 2005 Oden Eriksson <oeriksson@mandriva.com> 5.0.4_0.9.3-3mdk
- rebuild

* Wed Sep 07 2005 Oden Eriksson <oeriksson@mandriva.com> 5.0.4_0.9.3-2mdk
- added one hash fix patch from the hardened-php project (P11)

* Fri May 27 2005 Oden Eriksson <oeriksson@mandriva.com> 5.0.4_0.9.3-1mdk
- 0.9.3 final

* Fri May 27 2005 Oden Eriksson <oeriksson@mandriva.com> 5.0.4_0.9.3-0.rc2.1mdk
- rename the package
- 0.9.3-rc2
- rediff and reorder patches
- use better anti ^M stripper

* Sun Apr 17 2005 Oden Eriksson <oeriksson@mandriva.com> 5.0.4_0.9.2a-1mdk
- 5.0.4

* Tue Apr 05 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 5.0.3_0.9.2a-6mdk
- fixed a small bug when building the eloader stuff

* Sun Mar 20 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 5.0.3_0.9.2a-5mdk
- use the %%mkrel macro

* Thu Feb 24 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 5.0.3_0.9.2a-4mdk
- reintroduced phpcoder-1.4 + patch
- nuke the .htaccess files
- restart apache

* Sat Feb 12 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 5.0.3_0.9.2a-3mdk
- rebuilt against a non hardened-php aware php lib
- disable sysvipc shared memory support as it does not work...

* Fri Feb 11 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 5.0.3_0.9.2a-2mdk
- added fixes from cvs (P1) so that it actually works...
- fix the patch to the extensions dir

* Sun Jan 16 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 5.0.3_0.9.2a-1mdk
- 0.9.2a
- rebuild due to hardened-php-0.2.6

* Tue Jan 11 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 5.0.3_0.9.2-1mdk
- initial mandrake package

* Tue Jan 11 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.10_0.9.2-2mdk
- reset admin name and password in the 99_eaccelerator.ini file
- obsolete php-mmcache-*

* Tue Jan 11 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.10_0.9.2-1mdk
- php-mmcache is dead, long live php-eaccelerator!
- used parts from the package by Bart Vanbrabant

* Thu Dec 16 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.10_2.4.7-0.20040822.1mdk
- rebuild for php 4.3.10

* Tue Aug 24 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.8_2.4.7-0.20040822.1mdk
- use a recent snap (20040822)
- phpcoder-1.4

* Thu Jul 15 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.8_2.4.7-0.1mdk
- rebuilt for php-4.3.8

* Tue Jul 13 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.7_2.4.7-0.2mdk
- remove redundant provides

* Tue Jun 15 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.7_2.4.7-0.1mdk
- rebuilt for php-4.3.7

* Tue May 25 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.6_2.4.7-0.2mdk
- new snap
- use the %%configure2_5x macro
- move scandir to /etc/php.d

* Tue May 11 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.6_2.4.7-0.1mdk
- use a snap from 20040510
- updated S1

* Thu May 06 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 4.3.6_2.4.6-1mdk
- built for php 4.3.6
