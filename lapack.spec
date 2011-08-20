Summary: Numerical linear algebra package libraries
Name: lapack
Version: 3.2.1
Release: 4%{?dist}
License: BSD
Group: Development/Libraries
URL: http://www.netlib.org/lapack/
Source0: http://www.netlib.org/lapack/lapack-%{version}.tgz
Source1: http://www.netlib.org/lapack/manpages.tgz
Source2: Makefile.blas
Source3: Makefile.lapack
Source4: http://www.netlib.org/lapack/lapackqref.ps
Source5: http://www.netlib.org/blas/blasqr.ps
Patch3: lapack-3.1.1-make.inc.patch
BuildRequires: gcc-gfortran
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
LAPACK (Linear Algebra PACKage) is a standard library for numerical
linear algebra. LAPACK provides routines for solving systems of
simultaneous linear equations, least-squares solutions of linear
systems of equations, eigenvalue problems, and singular value
problems. Associated matrix factorizations (LU, Cholesky, QR, SVD,
Schur, and generalized Schur) and related computations (i.e.,
reordering of Schur factorizations and estimating condition numbers)
are also included. LAPACK can handle dense and banded matrices, but
not general sparse matrices. Similar functionality is provided for
real and complex matrices in both single and double precision. LAPACK
is coded in Fortran77 and built with gcc.

%package devel
Summary: LAPACK development libraries
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: blas-devel = %{version}-%{release}
Provides: lapack-static = %{version}-%{release}

%description devel
LAPACK development libraries for applications that link statically.

%package -n blas
Summary: The Basic Linear Algebra Subprograms library
Group: Development/Libraries

%description -n blas
BLAS (Basic Linear Algebra Subprograms) is a standard library which
provides a number of basic algorithms for numerical algebra. 

%package -n blas-devel
Summary: BLAS development libraries
Group: Development/Libraries
Requires: blas = %{version}-%{release}
Requires: gcc-gfortran
Provides: blas-static = %{version}-%{release}

%description -n blas-devel
BLAS development libraries for applications that link statically.

%prep
%setup -q 
%setup -q -D -T -a1
%patch3 -p1
cp -f INSTALL/make.inc.gfortran make.inc
cp -f %{SOURCE2} BLAS/SRC/Makefile
cp -f %{SOURCE3} SRC/Makefile

mv lapack-3.2.0/manpages/ manpages/

#Empty
rm -f manpages/man/manl/zbcon.l

%build
# use RPM_OPT_O_FLAGS (-O0) everywhere necessary
# drop RPM_OPT_SIZE_FLAGS (-Os) (bz 520518)
RPM_OPT_O_FLAGS=$(echo $RPM_OPT_FLAGS | sed 's|-O2|-O0|')
export FC=gfortran

# Build BLAS
pushd BLAS/SRC
FFLAGS="$RPM_OPT_O_FLAGS" make dcabs1.o
FFLAGS="$RPM_OPT_FLAGS" CFLAGS="$RPM_OPT_FLAGS" make static
cp libblas.a ${RPM_BUILD_DIR}/%{name}-%{version}/
make clean
FFLAGS="$RPM_OPT_O_FLAGS -fPIC" make dcabs1.o
FFLAGS="$RPM_OPT_FLAGS -fPIC" CFLAGS="$RPM_OPT_FLAGS -fPIC" make shared
cp libblas.so.%{version} ${RPM_BUILD_DIR}/%{name}-%{version}/
popd

ln -s libblas.so.%{version} libblas.so

# Build the static dlamch, dsecnd, lsame, second, slamch bits
pushd INSTALL
make NOOPT="$RPM_OPT_O_FLAGS" OPTS="$RPM_OPT_FLAGS"
popd

# Build the static lapack library
pushd SRC
make FFLAGS="$RPM_OPT_FLAGS" CFLAGS="$RPM_OPT_FLAGS" static
cp liblapack.a ${RPM_BUILD_DIR}/%{name}-%{version}/
popd

# Build the static with pic dlamch, dsecnd, lsame, second, slamch bits
pushd INSTALL
make clean
make NOOPT="$RPM_OPT_O_FLAGS -fPIC" OPTS="$RPM_OPT_FLAGS -fPIC"
popd

# Build the static with pic lapack library
pushd SRC
make clean
make FFLAGS="$RPM_OPT_FLAGS -fPIC" CFLAGS="$RPM_OPT_FLAGS -fPIC" static
cp liblapack.a ${RPM_BUILD_DIR}/%{name}-%{version}/liblapack_pic.a
popd

# Build the shared dlamch, dsecnd, lsame, second, slamch bits
pushd INSTALL
make clean
make NOOPT="$RPM_OPT_O_FLAGS -fPIC" OPTS="$RPM_OPT_FLAGS -fPIC"
popd

# Build the shared lapack library
pushd SRC
make clean
make FFLAGS="$RPM_OPT_FLAGS -fPIC" CFLAGS="$RPM_OPT_FLAGS -fPIC" shared
cp liblapack.so.%{version} ${RPM_BUILD_DIR}/%{name}-%{version}/
popd

cp -p %{SOURCE4} lapackqref.ps
cp -p %{SOURCE5} blasqr.ps

%install
rm -fr ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/manl

for f in liblapack.so.%{version} libblas.so.%{version} libblas.a liblapack.a liblapack_pic.a; do
  cp -f $f ${RPM_BUILD_ROOT}%{_libdir}/$f
done

find manpages/blas/man/manl -type f -printf "%{_mandir}/manl/%f*\n" > blasmans

# These are also in the BLAS package
rm -f manpages/man/manl/lsame.l*
rm -f manpages/man/manl/xerbla.l*
find manpages/man/manl -type f -printf "%{_mandir}/manl/%f*\n" > lapackmans

cp -f manpages/blas/man/manl/* ${RPM_BUILD_ROOT}%{_mandir}/manl
cp -f manpages/man/manl/* ${RPM_BUILD_ROOT}%{_mandir}/manl

cd ${RPM_BUILD_ROOT}%{_libdir}
ln -sf liblapack.so.%{version} liblapack.so
ln -sf liblapack.so.%{version} liblapack.so.3
ln -sf liblapack.so.%{version} liblapack.so.3.2
ln -sf libblas.so.%{version} libblas.so
ln -sf libblas.so.%{version} libblas.so.3
ln -sf libblas.so.%{version} libblas.so.3.2

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post -n blas -p /sbin/ldconfig

%postun -n blas -p /sbin/ldconfig

%clean
rm -fr ${RPM_BUILD_ROOT}

%files -f lapackmans
%defattr(-,root,root)
%doc README lapackqref.ps LICENSE
%{_libdir}/liblapack.so.*

%files devel
%defattr(-,root,root,-)
%{_libdir}/liblapack.so
%{_libdir}/liblapack*.a

%files -n blas -f blasmans
%defattr(-,root,root)
%doc blasqr.ps
%{_libdir}/libblas.so.*

%files -n blas-devel
%defattr(-,root,root,-)
%{_libdir}/libblas.so
%{_libdir}/libblas*.a

%changelog
* Wed Feb 17 2010 Ivana Hutarova Varekova <varekova@redhat.com> - 3.2.1-4
- Resolves: #543948 
  add license file

* Fri Sep  4 2009 Tom "spot" Callaway <tcallawa@redhat.com> - 3.2.1-3
- use RPM_OPT_O_FLAGS (-O0) everywhere necessary, drop RPM_OPT_SIZE_FLAGS (-Os) (bz 520518)

* Thu Aug 20 2009 Tom "spot" Callaway <tcallawa@redhat.com> - 3.2.1-2
- don't enable xblas yet

* Fri Aug 14 2009 Tom "spot" Callaway <tcallawa@redhat.com> - 3.2.1-1
- update to 3.2.1, spec file cleanups

* Mon Aug 10 2009 Ville Skyttä <ville.skytta@iki.fi> - 3.1.1-7
- Convert specfile to UTF-8.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.1.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Jul  8 2008 Tom "spot" Callaway <tcallawa@redhat.com> 3.1.1-4
- fix missing dependencies (bz 442915)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 3.1.1-3
- Autorebuild for GCC 4.3

* Thu Aug 23 2007 Tom "spot" Callaway <tcallawa@redhat.com> 3.1.1-2
- fix license (BSD)
- rebuild for BuildID

* Fri May 25 2007 Tom "spot" Callaway <tcallawa@redhat.com> 3.1.1-1
- bump to 3.1.1

* Fri Jan  5 2007 Tom "spot" Callaway <tcallawa@redhat.com> 3.1.0-4
- fix bugzillas 219740,219741

* Wed Dec 20 2006 Tom "spot" Callaway <tcallawa@redhat.com> 3.1.0-3
- make clean everywhere

* Wed Dec 20 2006 Tom "spot" Callaway <tcallawa@redhat.com> 3.1.0-2
- fix the Makefiles

* Tue Nov 14 2006 Tom "spot" Callaway <tcallawa@redhat.com> 3.1.0-1
- bump to 3.1.0

* Thu Sep 14 2006 Tom "spot" Callaway <tcallawa@redhat.com> 3.0-38
- bump for fc-6

* Tue Feb 28 2006 Tom "spot" Callaway <tcallawa@redhat.com> 3.0-37
- bump for FC5

* Mon Dec 19 2005 Tom "spot" Callaway <tcallawa@redhat.com> 3.0-36
- bump for gcc4.1

* Tue Nov 15 2005 Tom "spot" Callaway <tcallawa@redhat.com> 3.0-35
- try not to patch files that do not exist

* Tue Nov 15 2005 Tom "spot" Callaway <tcallawa@redhat.com> 3.0-34
- finish fixing bz 143340

* Thu Oct  6 2005 Tom "spot" Callaway <tcallawa@redhat.com> 3.0-33
- fix bz 169558

* Wed Sep 28 2005 Tom "spot" Callaway <tcallawa@redhat.com> 3.0-32
- move to latest upstream 3.0 tarballs
- add 8 missing BLAS functions from upstream blas tarball (bz 143340)

* Thu Sep 22 2005 Tom "spot" Callaway <tcallawa@redhat.com> 3.0-31
- actually install liblapack_pic.a

* Wed Sep 14 2005 Tom "spot" Callaway <tcallawa@redhat.com> 3.0-30
- make -devel packages
- make liblapack_pic.a package
- use dist tag

* Thu Apr 14 2005 Tom "spot" Callaway <tcallawa@redhat.com> 3.0-29
- package moves to Fedora Extras, gcc4

* Tue Dec 21 2004 Ivana Varekova <varekova@redhat.com>
- fix bug #143420 problem with compiler optimalizations

* Tue Nov 30 2004 Ivana Varekova <varekova@redhat.com>
- fix bug #138683 problem with compilation

* Thu Nov 11 2004 Ivana Varekova <varekova@redhat.com>
- fix build problem bug #138447

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Dec 31 2003 Jeff Johnson <jbj@jbj.org> 3.0-23
- link -lg2c explicitly into liblapack and libblas (#109079).

* Wed Aug 20 2003 Jeremy Katz <katzj@redhat.com> 3.0-22
- nuke -man subpackages (#97506)

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Sun Nov 10 2002 Jeff Johnson <jbj@redhat.com> 3.0-19
- rebuild with x86_64.

* Thu Jul 18 2002 Trond Eivind Glomsrod <teg@redhat.com> 3.0-18
- Remove an empty man page (#63569)

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Wed May  1 2002 Trond Eivind Glomsrod <teg@redhat.com> 3.0-15
- Rebuild

* Thu Feb 21 2002 Trond Eivind Glomsrod <teg@redhat.com> 3.0-14
- Rebuild

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Mon Aug 13 2001 Trond Eivind Glomsrod <teg@redhat.com> 3.0-12
- The man-pages for xerbla and lsame were in blas-man and lapack-man (#51605)

* Fri Jun  8 2001 Trond Eivind Glomsrod <teg@redhat.com>
- Reenable optimization for IA64

* Fri May 25 2001 Trond Eivind Glomsrod <teg@redhat.com>
- Add all patches from the LAPACK site as of 2001-05-25
- Use this workaround for IA64 instead
- Remove SPARC workaround
- Don't exclude IA64

* Thu Dec 07 2000 Trond Eivind Glomsrod <teg@redhat.com>
- rebuild for main distribution

* Mon Nov 20 2000 Trond Eivind Glomsrod <teg@redhat.com>
- add the LAPACK Quick Reference Guide to the docs
- add the BLAS Quick Reference Guide to the docs

* Tue Aug 01 2000 Trond Eivind Glomsrod <teg@redhat.com>
- fix lack of ldconfig in postuninstall script

* Mon Jul 24 2000 Prospector <prospector@redhat.com>
- rebuilt

* Mon Jul 10 2000 Trond Eivind Glomsrod <teg@redhat.com>
- updated with the latest updates (new tarfile..) from netlib 

* Thu Jun 15 2000 Trond Eivind Glomsrod <teg@redhat.com>
- use %%{_mandir}
- added some flags to work around SPARC compiler bug

* Wed Jan 19 2000 Tim Powers <timp@redhat.com>
- bzipped sources to conserve space

* Tue Jan  4 2000 Jeff Johnson <jbj@redhat.com>
- build for PowerTools 6.2.

* Sat Dec 25 1999 Joachim Frieben <jfrieben@hotmail.com>
- updated to version v3.0 + update as of Tue Nov 30 1999

* Sat Oct 23 1999 Joachim Frieben <jfrieben@hotmail.com>
- updated Red Hat makefiles to v3.0

* Mon Aug 2 1999 Tim Powers <timp@redhat.com>
- updated to v3.0
- built for 6.1

* Mon Apr 12 1999 Michael Maher <mike@redhat.com>
- built package for 6.0

* Sat Oct 24 1998 Jeff Johnson <jbj@redhat.com>
- new description/summary text.

* Fri Jul 17 1998 Jeff Johnson <jbj@redhat.com>
- repackage for powertools.

* Sun Feb 15 1998 Trond Eivind Glomsrod <teg@pvv.ntnu.no>
 [lapack-2.0-9]
 - No code updates, just built with a customized rpm -
   this should make dependencies right.

* Sat Feb 07 1998 Trond Eivind Glomsrod <teg@pvv.ntnu.no>
 [lapack-2.0-8]
 - Total rewrite of the spec file
 - Added my own makefiles - libs should build better,
   static libs should work (and be faster than they
	would be if they had worked earlier ;)
 - No patch necessary anymore.
 - Renamed lapack-blas and lapack-blas-man to
   blas and blas-man. "Obsoletes:" tag added.
   (oh - and as always: Dedicated to the girl I
   love, Eline Skirnisdottir)

* Sat Dec 06 1997 Trond Eivind Glomsrod <teg@pvv.ntnu.no>
 [lapack-2.0-7]
  - added a dependency to glibc, so people don't try with libc5

* Thu Nov 20 1997 Trond Eivind Glomsrod <teg@pvv.ntnu.no>
  [lapack-2.0-6]
  - removed etime.c
  - compiled with egcs, and for glibc 2.0

* Sun Oct 12 1997 Trond Eivind Glomsrod <teg@pvv.ntnu.no>
  [lapack-2.0-5]
  - added a changelog
  - cleaned up building of shared libs
  - now uses a BuildRoot
  - cleaned up the specfile
