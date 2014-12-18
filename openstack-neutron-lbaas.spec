%global modulename neutron_lbaas
%global servicename neutron-lbaas

Name:           openstack-%{servicename}
Version:        XXX
Release:        XXX%{?dist}
Summary:        Openstack Networking Load Balancer as a Service (LBaaS) plugin

License:        ASL 2.0
URL:            http://launchpad.net/neutron/
Source0:        http://tarballs.openstack.org/%{servicename}/%{servicename}-master.tar.gz
Source1:        neutron-lbaas-agent.service

BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  systemd

Requires:       openstack-neutron >= 2015.1
Requires:       python-alembic
Requires:       python-eventlet
Requires:       python-netaddr >= 0.7.12
Requires:       python-oslo-config >= 2:1.4.0
Requires:       python-oslo-db >= 1.1.0
Requires:       python-oslo-messaging >= 1.4.0.0
Requires:       python-oslo-serialization >= 1.0.0
Requires:       python-oslo-utils >= 1.0.0
Requires:       python-pbr
Requires:       python-requests
Requires:       python-six
Requires:       python-sqlalchemy

%description
This is a service plugin for Openstack Neutron (Networking) service that
implements Load Balancer as a Service (LBaas) inside Neutron L3 agent.


%prep
%setup -q -n neutron-lbaas-%{upstream_version}
# Remove bundled egg-info
rm -rf %{modulename}.egg-info


%build
%{__python2} setup.py build


%install
export OSLO_PACKAGE_VERSION=%{version}
%{__python2} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

# Move config files to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron
mv %{buildroot}/usr/etc/neutron/*.ini %{buildroot}%{_sysconfdir}/neutron
 
# Install systemd units
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/neutron-lbaas-agent.service


%post
%systemd_post neutron-lbaas-agent.service


%preun
%systemd_preun neutron-lbaas-agent.service


%postun
%systemd_postun_with_restart neutron-lbaas-agent.service


%files
%doc AUTHORS CONTRIBUTING.rst LICENSE README.rst
%{_bindir}/neutron-lbaas-agent
%{_unitdir}/neutron-lbaas-agent.service
%{python2_sitelib}/%{modulename}
%{python2_sitelib}/%{modulename}-%{version}-py%{python2_version}.egg-info
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/neutron/lbaas_agent.ini


%changelog
* Wed Dec 17 2014 Ihar Hrachyshka <ihrachys@redhat.com> - 2015.1.0.0.1
- Initial attempt to package LBaaS plugin.
