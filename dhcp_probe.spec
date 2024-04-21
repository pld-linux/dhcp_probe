Summary:	Tool for discovering DHCP and BootP servers
Summary(pl.UTF-8):	Narzędzie do znajdowania serwerów DHCP i BootP
Name:		dhcp_probe
Version:	1.3.1
Release:	1
License:	GPL v2+ and MIT
Group:		Applications/Networking
Source0:	https://www.net.princeton.edu/software/dhcp_probe/%{name}-%{version}.tar.gz
# Source0-md5:	0fecf69bd0439603b5e3b3f0a652b822
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	dhcp_probe.target
Source4:	dhcp_probe@.service
Source5:	dhcp_probe-service-generator
Patch3:		dhcp_probe-virta-02-keep-pcap.patch
Patch4:		dhcp_probe-virta-03-drop-privs.patch
URL:		https://www.net.princeton.edu/software/dhcp_probe/
BuildRequires:	libnet-devel >= 1:1.2
BuildRequires:	libpcap-devel
BuildRequires:	rpmbuild(macros) >= 1.647
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	libnet >= 1:1.2
Requires:	rc-scripts
Requires:	systemd-units >= 38
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
dchp_probe attempts to discover DHCP and BootP servers on
a directly-attached Ethernet network. A network administrator can use
this tool to locate unauthorized DHCP and BootP servers. 

%description -l pl.UTF-8
dhcp_probe próbuje wykryć serwery DHCP i BootP w bezpośrednio
podłączonej sieci Ethernet. Narzędzie jest przydatne dla
administratorów sieci do lokalizowania nieautoryzowanych serwerów DHCP
oraz BootP.

%prep
%setup -q
%patch3 -p0
%patch4 -p0
cp -a extras/README README.extras

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{sysconfig,rc.d/init.d},%{systemdunitdir}} \
	$RPM_BUILD_ROOT/lib/systemd/system-generators

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -p extras/dhcp_probe.cf.sample $RPM_BUILD_ROOT%{_sysconfdir}/dhcp_probe.cf
install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/dhcp_probe
install -p %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/dhcp_probe
install -p %{SOURCE3} $RPM_BUILD_ROOT%{systemdunitdir}/dhcp_probe.target
install -p %{SOURCE4} $RPM_BUILD_ROOT%{systemdunitdir}/dhcp_probe@.service
ln -s /dev/null $RPM_BUILD_ROOT%{systemdunitdir}/dhcp_probe.service
install -p %{SOURCE5} $RPM_BUILD_ROOT/lib/systemd/system-generators/dhcp_probe-service-generator

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}
%service %{name} restart
%systemd_post %{name}.target

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi
%systemd_preun %{name}.target

%postun
%systemd_reload

%files
%defattr(644,root,root,755)
%doc AUTHORS COPYING ChangeLog INSTALL.dhcp_probe NEWS README* TODO extras/{dhcp_probe_notify*,mail-throttled}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/dhcp_probe.cf
%attr(755,root,root) %{_sbindir}/dhcp_probe
%attr(754,root,root) /etc/rc.d/init.d/dhcp_probe
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/dhcp_probe
%attr(755,root,root) /lib/systemd/system-generators/dhcp_probe-service-generator
%{systemdunitdir}/dhcp_probe.service
%{systemdunitdir}/dhcp_probe.target
%{systemdunitdir}/dhcp_probe@.service
%{_mandir}/man5/dhcp_probe.cf.5*
%{_mandir}/man8/dhcp_probe.8*
