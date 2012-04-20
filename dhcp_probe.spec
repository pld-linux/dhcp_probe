Summary:	Tool for discovering DHCP and BootP servers
Name:		dhcp_probe
Version:	1.3.0
Release:	0.1
License:	GPLv2+ and MIT
Group:		Applications
Source0:	http://www.net.princeton.edu/software/dhcp_probe/%{name}-%{version}.tar.gz
# Source0-md5:	8067e696fbd88120bdcc2ffef4b64da2
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	dhcp_probe@.service
Patch0:		dhcp_probe-guignard-03_implicit_point_conv_bootp.c.patch
Patch1:		dhcp_probe-guignard-04_linux_32_or_64bits.patch
Patch2:		dhcp_probe-virta-01-pcap-loop.patch
Patch3:		dhcp_probe-virta-02-keep-pcap.patch
Patch4:		dhcp_probe-virta-03-drop-privs.patch
URL:		http://www.net.princeton.edu/software/dhcp_probe/
BuildRequires:	rpmbuild(macros) >= 1.647
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
BuildRequires:	libnet-devel >= 1:1.1.6
BuildRequires:	libpcap-devel
Requires:	rc-scripts
Requires:	systemd-units >= 0.38
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
dchp_probe attempts to discover DHCP and BootP servers on
a directly-attached Ethernet network. A network administrator can use
this tool to locate unauthorized DHCP and BootP servers. 

%prep
%setup -q
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p0
%patch4 -p0
cp -a extras/README README.extras

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{sysconfig,rc.d/init.d},%{systemdunitdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -p extras/dhcp_probe.cf.sample $RPM_BUILD_ROOT%{_sysconfdir}/dhcp_probe.cf
install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/dhcp_probe
install -p %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/dhcp_probe
install -p %{SOURCE3} $RPM_BUILD_ROOT%{systemdunitdir}/dhcp_probe@.service

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}
%service %{name} restart
%systemd_reload

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi
%systemd_reload

%postun
%systemd_reload

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog INSTALL.dhcp_probe NEWS README* TODO
%doc extras/dhcp_probe_notify* extras/mail-throttled
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/dhcp_probe.cf
%attr(755,root,root) %{_sbindir}/dhcp_probe
%attr(754,root,root) /etc/rc.d/init.d/dhcp_probe
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/dhcp_probe
%{systemdunitdir}/%{name}@.service
%{_mandir}/man5/dhcp_probe.cf.5*
%{_mandir}/man8/dhcp_probe.8*
