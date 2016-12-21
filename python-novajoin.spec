%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global service novajoin

Name:           python-%{service}
Version:        XXX
Release:        XXX
Summary:        Nova integration to enroll IPA clients

License:        ASL 2.0
URL:            https://launchpad.net/novajoin
Source0:        https://tarballs.openstack.org/%{service}/%{service}-%{version}.tar.gz
Source1:        novajoin-notify.service
Source2:        novajoin-server.service
Source3:        novajoin.logrotate

BuildArch:      noarch

Requires:       python-webob
Requires:       python-paste
Requires:       python-routes
Requires:       python-six
Requires:       python-keystoneclient
Requires:       python-keystoneauth1
Requires:       python-oslo-concurrency
Requires:       python-oslo-messaging
Requires:       python-oslo-policy
Requires:       python-oslo-serialization
Requires:       python-oslo-service
Requires:       python-oslo-utils
Requires:       python-neutronclient
Requires:       python-novaclient
Requires:       python-cinderclient
Requires:       python-glanceclient

# this is the package that creates the nova user
Requires:       openstack-nova-common
Requires:       ipa-admintools
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

BuildRequires:  python-webob
BuildRequires:  python-paste
BuildRequires:  python-routes
BuildRequires:  python-six
BuildRequires:  python-keystoneclient
BuildRequires:  python-keystoneauth1
BuildRequires:  python-oslo-concurrency
BuildRequires:  python-oslo-messaging
BuildRequires:  python-oslo-policy
BuildRequires:  python-oslo-serialization
BuildRequires:  python-oslo-service
BuildRequires:  python-oslo-utils
BuildRequires:  python-neutronclient
BuildRequires:  python-novaclient
BuildRequires:  python-cinderclient
BuildRequires:  python-glanceclient
BuildRequires:  openstack-nova-common
BuildRequires:  python2-devel
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  python-sphinx
BuildRequires:  python-oslo-sphinx
BuildRequires:  python-sphinx_rtd_theme
BuildRequires:  git
BuildRequires:  systemd
BuildRequires:  systemd-units
BuildRequires:  python-hacking
BuildRequires:  python-anyjson
BuildRequires:  python-coverage
BuildRequires:  python-fixtures
BuildRequires:  python-mock
BuildRequires:  python-subunit
BuildRequires:  python-testtools
BuildRequires:  python-testrepository
BuildRequires:  python-testresources
BuildRequires:  python-testscenarios
BuildRequires:  python-os-testr

%description
A nova vendordata plugin for the OpenStack nova metadata
service to manage host instantiation in an IPA server.

%package -n python-%{service}-tests-unit
Summary:        Unit tests for novajoin
Requires:       python-%{service} = %{version}-%{release}

Requires:       python-anyjson
Requires:       python-coverage
Requires:       python-fixtures
Requires:       python-mock
Requires:       python-subunit
Requires:       python-testtools
Requires:       python-testrepository
Requires:       python-testresources
Requires:       python-testscenarios
Requires:       python-os-testr

%description -n python-%{service}-tests-unit
Unit test files for the novajoin service.

%prep
%autosetup -n %{service}-%{upstream_version} -S git

rm -f *requirements.txt

%build

%py2_build

# generate html docs
sphinx-build doc/source html
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}

%install
%py2_install

# Setup directories
install -d -m 755 %{buildroot}%{_mandir}/man1
install -d -m 755 %{buildroot}%{_datadir}/%{service}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{service}
install -d -m 755 %{buildroot}%{_localstatedir}/log/novajoin

# Install systemd service files
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/novajoin-notify.service
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/novajoin-server.service

# Install config files
install -p -D -m 640 files/join.conf.template %{buildroot}%{_sysconfdir}/nova/join.conf

# install log rotation configuration
install -p -D -m 644 -p %{SOURCE3} \
  %{buildroot}%{_sysconfdir}/logrotate.d/novajoin

%check
%{__python2} setup.py test

%files -n python-%{service}
%license LICENSE
%doc README.md
%doc html
%{python2_sitelib}/%{service}
%{python2_sitelib}/%{service}-*.egg-info
%config(noreplace) %attr(-, root, nova) %{_sysconfdir}/nova/join-api-paste.ini
%config(noreplace) %attr(-, root, nova) %{_sysconfdir}/nova/join.conf
%{_libexecdir}/novajoin-ipa-setup
%{_sbindir}/novajoin-install
%{_sbindir}/novajoin-notify
%{_sbindir}/novajoin-server
%dir %{_datarootdir}/novajoin
%{_datarootdir}/novajoin/cloud-config.json
%{_datarootdir}/novajoin/freeipa.json
%{_datarootdir}/novajoin/join.conf.template
%{_mandir}/man1/novajoin-install.1.gz
%{_mandir}/man1/novajoin-notify.1.gz
%{_mandir}/man1/novajoin-server.1.gz
%{_unitdir}/*.service
%attr(0700,nova,nova) %dir %{_localstatedir}/log/novajoin
%config(noreplace) %{_sysconfdir}/logrotate.d/novajoin
%exclude %{python2_sitelib}/%{service}/test.*
%exclude %{python2_sitelib}/%{service}/tests

%files -n python-%{service}-tests-unit
%license LICENSE
%{python2_sitelib}/%{service}/test.*
%{python2_sitelib}/%{service}/tests


%post
%systemd_post novajoin-server.service novajoin-notify.service

%preun
%systemd_preun novajoin-server.service novajoin-notify.service

%postun
%systemd_postun_with_restart novajoin-server.service novajoin-notify.service

%changelog
