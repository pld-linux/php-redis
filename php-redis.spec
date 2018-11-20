# TODO
# - use external igbinary and make it's dependency optional
#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	redis
Summary:	%{modname} A PHP extension for Redis
Name:		%{php_name}-%{modname}
Version:	4.2.0
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	https://github.com/nicolasff/phpredis/tarball/%{version}/%{modname}-%{version}.tar.gz
# Source0-md5:	e2664b39d94f5f72f2e6ac27db92bc70
Source1:	https://github.com/ukko/phpredis-phpdoc/tarball/master/%{modname}-phpdoc.tar.gz
# Source1-md5:	52160e53904c1072ae98345de4127de2
URL:		https://github.com/nicolasff/phpredis
BuildRequires:	%{php_name}-devel >= 4:5.0.4
%if %{with tests}
BuildRequires:	%{php_name}-pcre
BuildRequires:	%{php_name}-session
BuildRequires:	%{php_name}-simplexml
BuildRequires:	%{php_name}-cli
%endif
BuildRequires:	rpmbuild(macros) >= 1.519
%{?requires_php_extension}
Requires:	%{php_name}-session
Provides:	php(%{modname}) = %{version}
Obsoletes:	php-redis < 2.2.5-1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The phpredis extension provides an API for communicating with the
Redis key-value store.

This extension also provides session support.

%prep
%setup -qc -a1
mv phpredis-phpredis-*/* .
mv ukko-phpredis-phpdoc-* phpdoc

%build
phpize
%configure
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n \
	-dextension_dir=modules \
	-dextension=%{php_extensiondir}/pcre.so \
	-dextension=%{php_extensiondir}/spl.so \
	-dextension=%{php_extensiondir}/simplexml.so \
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
%doc CREDITS README.markdown phpdoc
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
