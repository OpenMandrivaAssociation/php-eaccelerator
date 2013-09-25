%define modname eaccelerator
%define soname %{modname}.so
%define inifile Z99_%{modname}.ini

Summary:	PHP accelerator optimizer
Name:		php-eaccelerator
Epoch:		2
Version:	0.9.6.1git20120725
Release:	12
Group:		Development/PHP
License:	GPLv2
Url:		http://eaccelerator.net/
# svn --username anonymous --password anonymous co http://dev.eaccelerator.net/eaccelerator/trunk eaccelerator
Source0:	http://prdownloads.sourceforge.net/eaccelerator/eaccelerator-%{version}.tar.gz
Source1:	eaccelerator.ini
Source2:	php-eaccelerator.rpmlintrc
Patch0:		eaccelerator-cache_file_location.diff
ExcludeArch:	%mips %arm
BuildRequires:	apache-devel >= 2.2.4
BuildRequires:	php-devel >= 3:5.2.2
Requires(post,postun): rpm-helper
Conflicts:	php-afterburner
Conflicts:	php-apc
Conflicts:	%{name}-eloader

%description
eAccelerator is a further development of the mmcache PHP accelerator and
encoder. It increases the performance of PHP scripts by caching them in a
compiled state, so that the overhead of compiling is almost completely
eliminated. 

%package	admin
Summary:	Web interface for controlling eaccelerator and encode php files
Group:		System/Servers
Requires:	%{name} >= %{EVRD}
Conflicts:	%{name}-eloader

%description	admin
This packages install the eAccelerator admin webinterface and a
script for encoding php files.

%prep

%setup -qn eaccelerator-%{version}
%apply_patches

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
%doc AUTHORS COPYING ChangeLog NEWS README doc/*
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/php.d/%{inifile}
%attr(0755,root,root) %{_libdir}/php/extensions/%{soname}

%files admin
%config(noreplace) %{_webappconfdir}/php-eaccelerator.conf
%dir /var/www/php-eaccelerator
/var/www/php-eaccelerator/*

