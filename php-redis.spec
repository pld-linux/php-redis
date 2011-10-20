#
# Conditional build:
%bcond_without	tests		# build without tests

%define		modname	redis
Summary:	%{modname} A PHP extension for Redis
Name:		php-%{modname}
Version:	2.1.3
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	https://github.com/nicolasff/phpredis/tarball/%{version}#/%{name}-%{version}.tgz
# Source0-md5:	eb2bee7e42f7a32a38c2a45377f21086
URL:		https://github.com/nicolasff/phpredis
%{?with_tests:BuildRequires:	/usr/bin/php}
BuildRequires:	php-devel >= 4:5.0.4
%{?with_tests:BuildRequires:	php-session}
%{?with_tests:BuildRequires:	php-simplexml}
BuildRequires:	rpmbuild(macros) >= 1.519
%{?requires_php_extension}
Requires:	php-session
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The phpredis extension provides an API for communicating with the
Redis key-value store.

This extension also provides session support.

%prep
%setup -qc
mv *-php%{modname}-*/* .

%build
phpize
%configure
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n \
	-dextension_dir=modules \
	-dextension=%{php_extensiondir}/simplexml.so \
	-dextension=%{php_extensiondir}/spl.so \
	-dextension=%{php_extensiondir}/session.so \
	-dextension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc CREDITS README.markdown
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
