%global modulename neutron_lbaas
%global servicename neutron-lbaas
%global type LBaaS

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           openstack-%{servicename}
Version:        2015.1.0
Release:        1%{?dist}
Summary:        Openstack Networking %{type} plugin

License:        ASL 2.0
URL:            http://launchpad.net/neutron/
Source0:        http://launchpad.net/neutron/%{release_name}/%{version}/+download/%{servicename}-%{upstream_version}.tar.gz

Source1:        %{servicename}-agent.service
Source2:        %{servicename}-dist.conf

BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  systemd-units

Requires:       python-%{servicename} = %{version}-%{release}
Requires:       openstack-neutron >= %{version}

%description
This is a %{type} service plugin for Openstack Neutron (Networking) service.


%package -n python-%{servicename}
Summary:        Neutron %{type} Python libraries
Group:          Applications/System

Requires:       python-neutron >= %{version}
Requires:       python-alembic >= 0.7.2
Requires:       python-barbicanclient >= 3.0.1
Requires:       python-eventlet
Requires:       python-netaddr >= 0.7.12
Requires:       python-oslo-config >= 2:1.9.3
Requires:       python-oslo-db >= 1.7.0
Requires:       python-oslo-log >= 1.0.0
Requires:       python-oslo-messaging >= 1.8.0
Requires:       python-oslo-serialization >= 1.4.0
Requires:       python-oslo-utils >= 1.4.0
Requires:       python-pbr
Requires:       python-pyasn1
Requires:       python-pyasn1-modules
Requires:       python-requests
Requires:       python-six
Requires:       python-sqlalchemy >= 0.9.7
Requires:       pyOpenSSL


%description -n python-%{servicename}
This is a %{type} service plugin for Openstack Neutron (Networking) service.

This package contains the Neutron %{type} Python library.


%package -n python-%{servicename}-tests
Summary:        Neutron %{type} tests
Group:          Applications/System

Requires:       python-%{servicename} = %{version}-%{release}


%description -n python-%{servicename}-tests
This is a %{type} service plugin for Openstack Neutron (Networking) service.

This package contains Neutron %{type} test files.


%prep
%setup -q -n %{servicename}-%{upstream_version}

# Let's handle dependencies ourselves
rm -f requirements.txt


%build
export PBR_VERSION=%{version}
export SKIP_PIP_INSTALL=1
%{__python2} setup.py build

# Loop through values in neutron-lbaas-dist.conf and make sure that the values
# are substituted into the lbaas_agent.ini as comments.
while read name eq value; do
  if [ -n "$name" -a -n "$value" ]; then
    sed -ri "0,/^(#)? *$name *=/{s!\(^(#)? *$name *=\).*!\1 $value!}" etc/lbaas_agent.ini
  fi
done < %{SOURCE2}


%install
export PBR_VERSION=%{version}
export SKIP_PIP_INSTALL=1
%{__python2} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

# Move rootwrap files to proper location
install -d -m 755 %{buildroot}%{_datarootdir}/neutron/rootwrap
mv %{buildroot}/usr/etc/neutron/rootwrap.d/*.filters %{buildroot}%{_datarootdir}/neutron/rootwrap

# Move config files to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron
mv %{buildroot}/usr/etc/neutron/*.ini %{buildroot}%{_sysconfdir}/neutron
mv %{buildroot}/usr/etc/neutron/*.conf %{buildroot}%{_sysconfdir}/neutron

# Install systemd units
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{servicename}-agent.service

# Install dist conf
install -p -D -m 640 %{SOURCE2} %{buildroot}%{_datadir}/neutron/%{servicename}-dist.conf

# Create configuration directory that can be populated by users with custom *.conf files
mkdir -p %{buildroot}/%{_sysconfdir}/neutron/conf.d/%{servicename}-agent

# Make sure neutron-server loads new configuration file
mkdir -p %{buildroot}/%{_datadir}/neutron/server
ln -s %{_sysconfdir}/neutron/%{modulename}.conf %{buildroot}%{_datadir}/neutron/server/%{modulename}.conf


%post
%systemd_post %{servicename}-agent.service


%preun
%systemd_preun %{servicename}-agent.service


%postun
%systemd_postun_with_restart %{servicename}-agent.service


%files
%license LICENSE
%doc AUTHORS CONTRIBUTING.rst README.rst
%{_bindir}/%{servicename}-agent
%{_bindir}/%{servicename}v2-agent
%{_unitdir}/%{servicename}-agent.service
%{_datarootdir}/neutron/rootwrap/lbaas-haproxy.filters
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/lbaas_agent.ini
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/neutron_lbaas.conf
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/services_lbaas.conf
%dir %{_sysconfdir}/neutron/conf.d
%dir %{_sysconfdir}/neutron/conf.d/%{servicename}-agent
%attr(-, root, neutron) %{_datadir}/neutron/%{servicename}-dist.conf
%{_datadir}/neutron/server/%{modulename}.conf


%files -n python-%{servicename}
%{python2_sitelib}/%{modulename}
%{python2_sitelib}/%{modulename}-%{version}-py%{python2_version}.egg-info
%exclude %{python2_sitelib}/%{modulename}/tests


%files -n python-%{servicename}-tests
%{python2_sitelib}/%{modulename}/tests


%changelog