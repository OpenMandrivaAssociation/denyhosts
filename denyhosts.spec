Name:       denyhosts
Version:    2.6
Release:    %mkrel 2
Summary:    A script to help thwart ssh server attacks

Group:      Networking/Other
License:    GPLv2
URL:        http://denyhosts.sourceforge.net/
Source0:    http://dl.sourceforge.net/denyhosts/DenyHosts-%{version}.tar.gz
Source1:    denyhosts.cron
Source2:    denyhosts.init
Source3:    denyhosts-allowed-hosts
Source4:    denyhosts.sysconfig
Source5:    denyhosts.logrotate
Source6:    README.fedora
Patch0:     denyhosts-2.6-config.patch
Patch1:     denyhosts-2.4-setup.patch
Patch2:     denyhosts-2.6-daemon-control.patch
# Patch10 is a security fix
Patch10:    denyhosts-2.6-regex.patch
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch:  noarch
BuildRequires:  python-devel
Requires:       openssh-server
Requires(post): rpm-helper
Requires(preun): rpm-helper

%description
DenyHosts is a Python script that analyzes the sshd server log
messages to determine which hosts are attempting to hack into your
system. It also determines what user accounts are being targeted. It
keeps track of the frequency of attempts from each host and, upon
discovering a repeated attack host, updates the /etc/hosts.deny file
to prevent future break-in attempts from that host.  Email reports can
be sent to a system admin.


%prep
%setup -q -n DenyHosts-%{version}
%patch0 -p0 -b .config
%patch1 -p0 -b .setup
%patch2 -p0 -b .daemon-control
%patch10 -p1 -b .regex

cp %{SOURCE6} .

# Fix up non-utf8-ness
for i in CHANGELOG.txt; do
  iconv -f iso-8859-1 -t utf-8 < $i > $i. && touch -r $i $i. && mv -f $i. $i
done

# This must be moved before the Python build process runs so that we
# can include it as documentation.
mv plugins/README.contrib .

# And the permissions are off as well
chmod +x plugins/*


%build
python setup.py build


%install
rm -rf %{buildroot}

python setup.py install -O1 --skip-build --root=%{buildroot}

install -d %{buildroot}/%{_bindir}
install -d %{buildroot}/%{_initrddir}
install -d %{buildroot}/%{_sysconfdir}/cron.d
install -d %{buildroot}/%{_sysconfdir}/logrotate.d
install -d %{buildroot}/%{_sysconfdir}/sysconfig

install -d -m 700 %{buildroot}/%{_localstatedir}/lib/denyhosts
install -d %{buildroot}/%{_localstatedir}/log

install -p -m 600 denyhosts.cfg-dist %{buildroot}/%{_sysconfdir}/denyhosts.conf
install -p -m 755 daemon-control-dist %{buildroot}/%{_bindir}/denyhosts-control
install -p -m 644 %{SOURCE1} %{buildroot}/%{_sysconfdir}/cron.d/denyhosts
install -p -m 755 %{SOURCE2} %{buildroot}/%{_initrddir}/denyhosts
install -p -m 644 %{SOURCE3} %{buildroot}/%{_localstatedir}/lib/denyhosts/allowed-hosts
install -p -m 644 %{SOURCE4} %{buildroot}/%{_sysconfdir}/sysconfig/denyhosts
install -p -m 644 %{SOURCE5} %{buildroot}/%{_sysconfdir}/logrotate.d/denyhosts

touch %{buildroot}/%{_localstatedir}/log/denyhosts

for i in allowed-warned-hosts hosts hosts-restricted hosts-root \
         hosts-valid offset suspicious-logins sync-hosts \
         users-hosts users-invalid users-valid; do
  touch %{buildroot}/%{_localstatedir}/lib/denyhosts/$i
done

# FC-4 and earlier won't create these automatically; create them here
# so that the %exclude below doesn't fail
touch %{buildroot}/%{_bindir}/denyhosts.pyc
touch %{buildroot}/%{_bindir}/denyhosts.pyo


%clean
rm -rf %{buildroot}


%preun
%_preun_service %name

%post
# Note that we do not automaticaly run --migrate, because we can't be
# sure that all of the hosts.deny entries were created by denyhosts
%_post_service %name

touch %{_localstatedir}/log/denyhosts
touch %{_localstatedir}/lib/denyhosts/allowed-warned-hosts
touch %{_localstatedir}/lib/denyhosts/hosts
touch %{_localstatedir}/lib/denyhosts/hosts-restricted
touch %{_localstatedir}/lib/denyhosts/hosts-root
touch %{_localstatedir}/lib/denyhosts/hosts-valid
touch %{_localstatedir}/lib/denyhosts/offset
touch %{_localstatedir}/lib/denyhosts/suspicious-logins
touch %{_localstatedir}/lib/denyhosts/sync-hosts
touch %{_localstatedir}/lib/denyhosts/users-hosts
touch %{_localstatedir}/lib/denyhosts/users-invalid
touch %{_localstatedir}/lib/denyhosts/users-valid

%postun
if [ $1 -ge 1 ] ; then
  service %name condrestart >/dev/null 2>&1
fi


%files
%defattr(-,root,root,-)
%doc CHANGELOG.txt denyhosts.cfg-dist LICENSE.txt
%doc README.fedora README.txt setup.py README.contrib

%{_bindir}/denyhosts.py
%exclude %{_bindir}/denyhosts.py[co]

%{_bindir}/denyhosts-control
%{_datadir}/denyhosts
%{py_puresitedir}/*

%config(noreplace) %{_sysconfdir}/denyhosts.conf
%config(noreplace) %{_sysconfdir}/cron.d/denyhosts
%config(noreplace) %{_sysconfdir}/logrotate.d/denyhosts
%config(noreplace) %{_sysconfdir}/sysconfig/denyhosts
%config(noreplace) %{_localstatedir}/lib/denyhosts/allowed-hosts

%ghost %{_localstatedir}/log/denyhosts
%ghost %{_localstatedir}/lib/denyhosts/allowed-warned-hosts
%ghost %{_localstatedir}/lib/denyhosts/hosts
%ghost %{_localstatedir}/lib/denyhosts/hosts-restricted
%ghost %{_localstatedir}/lib/denyhosts/hosts-root
%ghost %{_localstatedir}/lib/denyhosts/hosts-valid
%ghost %{_localstatedir}/lib/denyhosts/offset
%ghost %{_localstatedir}/lib/denyhosts/suspicious-logins
%ghost %{_localstatedir}/lib/denyhosts/sync-hosts
%ghost %{_localstatedir}/lib/denyhosts/users-hosts
%ghost %{_localstatedir}/lib/denyhosts/users-invalid
%ghost %{_localstatedir}/lib/denyhosts/users-valid

%dir %{_localstatedir}/lib/denyhosts

%{_initrddir}/denyhosts


