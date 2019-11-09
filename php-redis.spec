# TODO
# - use external igbinary and make it's dependency optional
#
# Conditional build:
%bcond_without	phpdoc		# build phpdoc package
%bcond_with	tests		# build without tests

# build "phpdoc" only for 7.3 version on pld builders
%if 0%{?_pld_builder:1} && "%{?php_suffix}" != "73"
%undefine	with_phpdoc
%endif

%define		php_name	php%{?php_suffix}
%define		modname	redis
Summary:	%{modname} A PHP extension for Redis
Name:		%{php_name}-%{modname}
Version:	4.3.0
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	https://github.com/phpredis/phpredis/tarball/%{version}/%{modname}-%{version}.tar.gz
# Source0-md5:	a038194807474611cf76dd727098b986
Source1:	https://github.com/ukko/phpredis-phpdoc/archive/9ec1795bcd45ec83a19b46cf9a8b78b4e4d7ac80/%{modname}-phpdoc.tar.gz
# Source1-md5:	eaba2e5fad040e2f4526374c073ae5f7
URL:		https://github.com/phpredis/phpredis
BuildRequires:	%{php_name}-cli
BuildRequires:	%{php_name}-devel >= 4:5.0.4
BuildRequires:	%{php_name}-pcre
BuildRequires:	%{php_name}-session
BuildRequires:	%{php_name}-simplexml
%if %{with tests}
BuildRequires:	%{php_name}-pecl-igbinary
BuildRequires:	%{php_name}-zlib
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

%package -n php-redis-phpdoc
Summary:	@phpdoc extension PHP for IDE autocomplete
Group:		Documentation
URL:		https://github.com/ukko/phpredis-phpdoc
Requires:	php-dirs
BuildArch:	noarch

%description -n php-redis-phpdoc
@phpdoc extension PHP for IDE autocomplete.

%prep
%setup -qc -a1
mv phpredis-phpredis-*/* .
mv phpredis-phpdoc-* phpdoc

%build
phpize
%configure
%{__make}

export TEST_PHP_EXECUTABLE="%{__php}"
export TEST_PHP_ARGS=" -n \
	-dextension_dir=modules \
	-dextension=%{php_extensiondir}/pcre.so \
	-dextension=%{php_extensiondir}/spl.so \
	-dextension=%{php_extensiondir}/simplexml.so \
	-dextension=%{php_extensiondir}/session.so \
	-dextension=%{modname}.so \
"

# simple module load test
$TEST_PHP_EXECUTABLE $TEST_PHP_ARGS -m > modules.log
grep %{modname} modules.log

%if %{with tests}
TEST_PHP_ARGS="
	$TEST_PHP_ARGS
	-dextension=%{php_extensiondir}/zlib.so \
"

# Run tests for Redis class (note this is the default)
$TEST_PHP_EXECUTABLE $TEST_PHP_ARGS tests/TestRedis.php --class Redis

# Run tests for RedisArray class
tests/mkring.sh start
$TEST_PHP_EXECUTABLE $TEST_PHP_ARGS tests/TestRedis.php --class RedisArray
tests/mkring.sh stop

# Run tests for the RedisCluster class
tests/make-cluster.sh start
$TEST_PHP_EXECUTABLE $TEST_PHP_ARGS tests/TestRedis.php --class RedisCluster
tests/make-cluster.sh stop
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

install -d $RPM_BUILD_ROOT%{_examplesdir}/php-%{modname}-%{version}
cp -a phpdoc/src/*.php $RPM_BUILD_ROOT%{_examplesdir}/php-%{modname}-%{version}

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

%if %{with phpdoc}
%files -n php-redis-phpdoc
%defattr(644,root,root,755)
%{_examplesdir}/php-%{modname}-%{version}
%endif
