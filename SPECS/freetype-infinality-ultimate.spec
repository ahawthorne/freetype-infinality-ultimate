%define _patchrel 2014.12.07

Name: freetype-infinality-ultimate
Version: 2.5.4
Release: 1%{?dist}
Summary: TrueType font rendering library with Infinality patches and custom settings.

Group: System Environment/Libraries
License: (FTL or GPLv2+) and BSD and MIT and Public Domain and zlib with acknowledgement
URL: http://www.freetype.org
Source:  http://download.savannah.gnu.org/releases/freetype/freetype-%{version}.tar.bz2
Source1: http://download.savannah.gnu.org/releases/freetype/freetype-doc-%{version}.tar.bz2
Source3: ftconfig.h
Source2: infinality-settings.sh

# Fix multilib conflicts
Patch88:  freetype-multilib.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1079302
Patch91:  freetype-2.5.3-freetype-config-libs.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1161963
Patch92:  freetype-2.5.3-freetype-config-prefix.patch

# bohoomil infinality
Patch1: 01-freetype-2.5.4-enable-valid.patch
Patch2: 02-ftsmooth-2.5.4.patch
Patch3: 03-upstream-%{_patchrel}.patch
Patch4: 04-infinality-2.5.4-%{_patchrel}.patch

Buildroot: %{_tmppath}/%{name}-%{version}-root-%(%{__id_u} -n)

BuildRequires: libX11-devel
BuildRequires: libpng-devel
BuildRequires: zlib-devel
BuildRequires: bzip2-devel
BuildRequires: harfbuzz-devel

Provides: %{name}-bytecode
Provides: %{name}
Provides: %{name}-subpixel
Obsoletes: freetype-subpixel
Conflicts: freetype-freeworld


%description
TrueType font rendering library with Infinality patches and custom settings.

%package devel
Summary: FreeType development libraries and header files
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
The freetype-infinality-ultimate-devel package includes the static libraries and header files
for the FreeType font rendering engine.

Install freetype-infinality-ultimate-devel if you want to develop programs which will use
FreeType.


%prep
%setup -q -n freetype-%{version}

%patch88 -p1 -b .multilib
%patch92 -p1 -b .freetype-config-prefix

%patch1 -p1 -b .enable-valid
%patch2 -p1 -b .ft-smooth
%patch3 -p1 -b .upstream-%{_patchrel}
%patch4 -p1 -b .infinality-2.5.4-%{_patchrel}


%build
%configure --disable-static \
           --with-zlib=yes \
           --with-bzip2=yes \
           --with-png=yes \
           --with-harfbuzz=yes
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' builds/unix/libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' builds/unix/libtool
make %{?_smp_mflags}

# Convert FTL.txt to UTF-8
pushd docs
iconv -f latin1 -t utf-8 < FTL.TXT > FTL.TXT.tmp && \
touch -r FTL.TXT FTL.TXT.tmp && \
mv FTL.TXT.tmp FTL.TXT
popd


%install
rm -rf $RPM_BUILD_ROOT


%makeinstall gnulocaledir=$RPM_BUILD_ROOT%{_datadir}/locale

# fix multilib issues
%define wordsize %{__isa_bits}

mv $RPM_BUILD_ROOT%{_includedir}/freetype2/config/ftconfig.h \
   $RPM_BUILD_ROOT%{_includedir}/freetype2/config/ftconfig-%{wordsize}.h
install -p -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_includedir}/freetype2/config/ftconfig.h

install -D -T $RPM_SOURCE_DIR/infinality-settings.sh \
 $RPM_BUILD_ROOT%{_sysconfdir}/X11/xinit/xinitrc.d/infinality-settings

sed -i "1i #!/bin/bash\n" \
 ${RPM_BUILD_ROOT}%{_sysconfdir}/X11/xinit/xinitrc.d/infinality-settings

# Don't package static a or .la files
rm -f $RPM_BUILD_ROOT%{_libdir}/*.{a,la}

%clean
rm -rf $RPM_BUILD_ROOT

%triggerpostun -- freetype < 2.0.5-3
{
  # ttmkfdir updated - as of 2.0.5-3, on upgrades we need xfs to regenerate
  # things to get the iso10646-1 encoding listed.
  for I in %{_datadir}/fonts/*/TrueType /usr/share/X11/fonts/TTF; do
      [ -d $I ] && [ -f $I/fonts.scale ] && [ -f $I/fonts.dir ] && touch $I/fonts.scale
  done
  exit 0
}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%{_libdir}/libfreetype.so.*
%doc README
%doc docs/LICENSE.TXT docs/FTL.TXT docs/GPLv2.TXT
%doc docs/CHANGES docs/VERSION.DLL docs/formats.txt
%doc
%{_sysconfdir}/X11/xinit/xinitrc.d/infinality-settings

%files devel
%defattr(-,root,root)
%dir %{_includedir}/freetype2
%{_datadir}/aclocal/freetype2.m4
%{_includedir}/freetype2/*
%{_libdir}/libfreetype.so
%{_bindir}/freetype-config
%{_libdir}/pkgconfig/freetype2.pc
%doc docs/reference
%{_mandir}/man1/*


%changelog
* Thu Dec 11 2014 Andrew Hawthorne <andrew.hawthorne@gmail.com> - 2.5.4-1
- Ininital build