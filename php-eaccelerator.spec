%define modname eaccelerator
%define dirname %{modname}
%define soname %{modname}.so
%define inifile Z99_%{modname}.ini

Summary:	PHP accelerator optimizer
Name:		php-eaccelerator
Version:	0.9.5.2
Release:	%mkrel 4
Group:		Development/PHP
License:	GPL
URL:		http://eaccelerator.net/
Source0:	http://prdownloads.sourceforge.net/eaccelerator/eaccelerator-%{version}.tar.bz2
Source1:	eaccelerator.ini
Patch0:		eaccelerator-cache_file_location.diff
Requires(post): rpm-helper
Requires(postun): rpm-helper
BuildRequires:	php-devel >= 3:5.2.2
BuildRequires:	apache-devel >= 2.2.4
BuildRequires:	dos2unix
Conflicts:	php-afterburner php-apc %{name}-eloader
Epoch:		2
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

%description
eAccelerator is a further development of the mmcache PHP accelerator and
encoder. It increases the performance of PHP scripts by caching them in a
compiled state, so that the overhead of compiling is almost completely
eliminated. 

%package	admin
Summary:	Web interface for controlling eaccelerator and encode php files
Group:		System/Servers
Requires(post): rpm-helper
Requires(postun): rpm-helper
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

# strip away annoying ^M
find -type f -exec dos2unix -U {} \;

%build
%serverbuild

phpize
%configure2_5x \
    --with-libdir=%{_lib} \
    --cache-file=config.cache \
    --without-eaccelerator-shared-memory \
    --with-eaccelerator-info \
    --with-eaccelerator-disassembler \
    --with-%{modname}=shared,%{_prefix}

%make
mv modules/*.so .

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/php/extensions
install -d %{buildroot}%{_sysconfdir}/php.d
install -d %{buildroot}/var/www/php-eaccelerator
install -d %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d

install -m0755 %{soname} %{buildroot}%{_libdir}/php/extensions/

install -m0644 eaccelerator.ini %{buildroot}%{_sysconfdir}/php.d/%{inifile}

install -m0644 bugreport.php %{buildroot}/var/www/php-eaccelerator/
install -m0644 control.php %{buildroot}/var/www/php-eaccelerator/index.php
install -m0644 dasm.php %{buildroot}/var/www/php-eaccelerator/
install -m0644 PHP_Highlight.php %{buildroot}/var/www/php-eaccelerator/

# fix access config files
cat > %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/php-eaccelerator.conf << EOF
Alias /php-eaccelerator /var/www/php-eaccelerator

<Directory /var/www/php-eaccelerator>
    Order deny,allow
    Deny from all
    Allow from 127.0.0.1
    ErrorDocument 403 "Access denied per %{_sysconfdir}/httpd/conf/webapps.d/php-eaccelerator.conf"
</Directory>
EOF

# pre-populate the balanced tree, grep "^static char num2hex" eaccelerator.c + grep "^#define EACCELERATOR_HASH_LEVEL" eaccelerator.h
install -d %{buildroot}/var/cache/httpd/php-eaccelerator/{0,1,2,3,4,5,6,7,8,9,a,b,c,d,e,f}/{0,1,2,3,4,5,6,7,8,9,a,b,c,d,e,f}
find %{buildroot}/var/cache/httpd/php-eaccelerator -type d | sed -e "s|%{buildroot}||" | sed -e 's/^/%attr(0711,apache,root) %dir /' > %{name}.filelist

%post
%_post_webapp

%postun
%_postun_webapp

%post admin
%_post_webapp

%postun admin
%_postun_webapp

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files -f %{name}.filelist
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog NEWS README doc/*
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/php.d/%{inifile}
%attr(0755,root,root) %{_libdir}/php/extensions/%{soname}

%files admin
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/php-eaccelerator.conf
%dir /var/www/php-eaccelerator
/var/www/php-eaccelerator/*
