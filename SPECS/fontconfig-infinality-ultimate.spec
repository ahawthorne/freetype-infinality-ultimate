%define _basename fontconfig
%define _master_name fontconfig-ultimate-master
%global freetype_version 2.1.4

Name: 		fontconfig-infinality-ultimate		
Version: 	2.11.1
Release:	1%{?dist}
Summary:	A library for configuring and customizing font access, optimized for freetype-infinality-ultimate

Group:		System Environment/Libraries	
License:	MIT and Public Domain and UCD
URL:		http://www.freetype.org	
Source:		http://fontconfig.org/release/%{_basename}-%{version}.tar.bz2
Source1:	25-no-bitmap-fedora.conf
Source2:	https://github.com/bohoomil/fontconfig-ultimate/archive/master.tar.gz

# https://bugzilla.redhat.com/show_bug.cgi?id=140335
Patch0:		%{_basename}-sleep-less.patch
# https://bugs.freedesktop.org/show_bug.cgi?id=77252
Patch1:		%{_basename}-fix-fccache-fail.patch
Patch2:		%{_basename}-fix-broken-cache.patch
#Patch3:		fontconfig-upstream-2014-11-06.patch

BuildRequires: expat-devel
BuildRequires: freetype-infinality-ultimate-devel >= %{freetype_version}
BuildRequires: fontpackages-devel
Requires:      /etc/ld.so.conf.d

Requires:	fontpackages-filesystem
Requires(pre):	freetype-infinality-ultimate
Requires(post):	grep coreutils
Requires:	font(:lang=en)

Provides: fontconfig-infinality
Provides: %{name}
obsoletes: fonts-config

%description
Fontconfig is designed to locate fonts within the
system and select them according to requirements specified by 
applications, optimized for freetype-infinality-ultimate.

%package	devel
Summary:	Font configuration and customization library
Group:		Development/Libraries
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	freetype-infinality-ultimate-devel >= %{freetype_version}
Requires:	pkgconfig

%description	devel
The fontconfig-devel package includes the header files,
and developer docs for the fontconfig package, optimized for
freetype-infinalty-ultimate

Install fontconfig-infinality-ultimate-devel if you want to develop programs which 
will use fontconfig.

%package	devel-doc
Summary:	Development Documentation files for fontconfig-infinality-ultimate library
Group:		Documentation
BuildArch:	noarch
Requires:	%{name}-devel = %{version}-%{release}

%description	devel-doc
The fontconfig-devel-doc package contains the documentation files
which is useful for developing applications that uses fontconfig.



%prep
%setup -q -n %{_basename}-%{version}

# copy fontconfig-ib patches & stuff
tar xzf $RPM_SOURCE_DIR/master.tar.gz 
cd %{_master_name}

cp -r conf.d.infinality $RPM_BUILD_DIR/%{_basename}-%{version}/conf.d.infinality
cp -r fontconfig_patches/*.patch $RPM_BUILD_DIR/%{_basename}-%{version}


# prepare src
cd $RPM_BUILD_DIR/%{_basename}-%{version}

%patch0 -p1 -b .sleep-less
%patch1 -p1 -b .cache-fail
%patch2 -p1 -b .broken-cache
#%patch3 -p1 -b .upstream-fixes





%build
# We don't want to rebuild the docs, but we want to install the included ones.
export HASDOCBOOK=no

%configure	--with-add-fonts=/usr/share/X11/fonts/Type1,/usr/share/X11/fonts/TTF,/usr/local/share/fonts \
		--disable-static \
		

make %{?_smp_mflags}




%install
make install DESTDIR=$RPM_BUILD_ROOT INSTALL="install -p"

find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

install -p -m 0644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.d
ln -s %{_fontconfig_templatedir}/25-unhint-nonlatin.conf $RPM_BUILD_ROOT%{_fontconfig_confdir}/

# move installed doc files back to build directory to package themm
# in the right place
mv $RPM_BUILD_ROOT%{_docdir}/fontconfig/* .
rmdir $RPM_BUILD_ROOT%{_docdir}/fontconfig/

#install infinality stuff
cd $RPM_BUILD_DIR/%{_basename}-%{version}/%{_master_name}

# copy presets
#cp -r fontconfig_patches/{combi,free,ms} \
#$RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.avail.infinality
install -d -p fontconfig_patches/{combi,free,ms} \
$RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.avail.infinality

install -d $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.avail.infinality
cp -pr conf.d.infinality/* $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.avail.infinality

# install fc-presets
install -m755 fontconfig_patches/fc-presets $RPM_BUILD_ROOT%{_bindir}/fc-presets

# copy font settings
install -m755 -d $RPM_BUILD_ROOT%{_docdir}/%{name}/fonts-settings
cp fontconfig_patches/fonts-settings/*.conf \
$RPM_BUILD_ROOT%{_docdir}/%{name}/fonts-settings

# copy documentation
install -m755 -d $RPM_BUILD_ROOT%{_docdir}/%{name}
cp -r doc $RPM_BUILD_ROOT%{_datadir}

 # install infinality-settings
install -m755 -d $RPM_BUILD_ROOT%{_docdir}/%{name}/freetype
install -m755 freetype/infinality-settings.sh \
$RPM_BUILD_ROOT%{_docdir}/%{name}/freetype/infinality-settings.sh
find $RPM_BUILD_ROOT -type d -name .git -exec rm -r '{}' +

%check
#make check

%post
cat << _EOF
Thank you for checking out fontconfig-infinality-ultimate.
By default, fontconfig will use presets for the free font collection
from [infinality-bundle-fonts] repository.
If you are going to use either a custom font collection or core
Microsoft families, set the appropriate presets using
fc-presets command.
_EOF

pushd etc/fonts/conf.d > /dev/null

redundant=(20-unhint-small-dejavu-sans-mono.conf
	20-unhint-small-dejavu-sans.conf
	20-unhint-small-dejavu-serif.conf
	57-dejavu-sans-mono.conf
	57-dejavu-sans.conf
	57-dejavu-serif.conf)
echo -e "Removing redundant symlinks ..."
for bit in "${redundant[@]}"; do
	if [ -f ${bit} ]; then
		rm -f ${bit}
	fi
done
echo -e "Done."

echo -e "Creating symlinks for free font collection ..."
ln -sf ../conf.avail.infinality/free/30-metric-aliases-free.conf .
ln -sf ../conf.avail.infinality/free/37-repl-global-free.conf .
ln -sf ../conf.avail.infinality/free/60-latin-free.conf .
ln -sf ../conf.avail.infinality/free/65-non-latin-free.conf .
ln -sf ../conf.avail.infinality/free/66-aliases-wine-free.conf .
echo -e "Done."
popd > /dev/null


/sbin/ldconfig

umask 0022

mkdir -p %{_localstatedir}/cache/fontconfig

# Force regeneration of all fontconfig cache files
# The check for existance is needed on dual-arch installs (the second
#  copy of fontconfig might install the binary instead of the first)
# The HOME setting is to avoid problems if HOME hasn't been reset
if [ -x /usr/bin/fc-cache ] && /usr/bin/fc-cache --version 2>&1 | grep -q %{version} ; then
  HOME=/root /usr/bin/fc-cache -f
fi

%postun 
pushd etc/fonts/conf.d > /dev/null
echo -e "Restoring old symlinks ..."
for bit in "${redundant[@]}"; do
	if [[ ! -f ${bit} ]] && [[ -f ../conf.avail/${bit} ]]; then
		ln -sf ../conf.avail/${bit} .
	fi
done
echo -e "Done."
cat << _EOF
fontconfig-infinality-ultimate-git has been removed.
Check for dead symlinks and leftover files
in /etc/fonts/conf.d/
_EOF
/sbin/ldconfig

%files
%doc README AUTHORS COPYING
%doc fontconfig-user.txt fontconfig-user.html
%doc %{_fontconfig_confdir}/README
%{_libdir}/libfontconfig.so.*
%{_bindir}/fc-cache
%{_bindir}/fc-cat
%{_bindir}/fc-list
%{_bindir}/fc-match
%{_bindir}/fc-pattern
%{_bindir}/fc-query
%{_bindir}/fc-scan
%{_bindir}/fc-validate
%{_bindir}/fc-presets
%{_fontconfig_templatedir}/*.conf
%{_datadir}/xml/fontconfig
# fonts.conf is not supposed to be modified.
# If you want to do so, you should use local.conf instead.
%config %{_fontconfig_masterdir}/fonts.conf
%config(noreplace) %{_fontconfig_confdir}/*.conf
%config(noreplace) %{_fontconfig_masterdir}/conf.avail.infinality/*.conf
%{_fontconfig_masterdir}/conf.avail.infinality/README
%{_fontconfig_masterdir}/conf.avail.infinality/README.in
%{_fontconfig_masterdir}/conf.avail.infinality/Makefile.am
%dir %{_localstatedir}/cache/fontconfig
%{_mandir}/man1/*
%{_mandir}/man5/*

%files devel
%{_libdir}/libfontconfig.so
%{_libdir}/pkgconfig/*
%{_includedir}/fontconfig
%{_mandir}/man3/*

%files devel-doc
%doc fontconfig-devel.txt fontconfig-devel


%changelog
* Fri Dec 12 2014 Andrew Hawthorne <andrew.hawthorne@gmail.com> - 2.11.1-1
- Ininital build

