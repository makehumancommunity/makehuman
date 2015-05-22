%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

Name:           PACKAGE_NAME
Summary:        MakeHuman
Version:        VER
Release:        1
URL:            http://www.makehuman.org
License:        AGPLv3
Group:          Applications/Graphics
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  mercurial
BuildRequires:  python
Vendor:         MakeHuman.org
Packager:       Joel Palmius <joepal1976@hotmail.com>
Provides:       makehuman
Requires:       python >= 2.7, numpy, PyOpenGL, PyQt4
Source:         PACKAGE_NAME-VER-1.tar.gz
BuildArch:      noarch
Summary:        Free, open source tool for creating realistic 3D human characters.

%description
 MakeHuman is a free, open source software which allows the creation of 
realistic 3D human characters fast and in a simplified manner, through the 
manipulation of controls for different human attributes.
 Users are able to model human characters by manipulating the controls to modify 
various human characteristics such as gender, age, height, weight and ethnicity 
as well as low level details of things such as the eye's shape, mouth's shape 
or finger's length. Via a 'point and click' approach, users can preview and 
load poses, animation cycles, facial expressions, hair, shoes and clothes onto 
characters from the MakeHuman™ Library. The human characters created can be 
saved in the custom MakeHuman format (.mhm), rendered and exported in various 
formats such as Collada (.dae), Filbox (.fbx), MD5, Blender exchange (.mhx), 
Wavefront .obj, Stereolithography (.stl).
 The output characters are licensed under the CC0 license, one of the most 
liberal license for output content. This means that artists are given the 
freedom to use their creations for both commercial and non-commercial 
purposes. The copyright © 2001-2015 is retained by the MakeHuman™ Team 
(makehuman.org) which grants you permission to use released code under the GNU 
Affero General Public License 3.0 (AGPL).

%prep
cd $RPM_BUILD_DIR
rm -rf makehuman
rm -rf usr
gzip -dc $RPM_SOURCE_DIR/PACKAGE_NAME-VER-1.tar.gz | tar -xvvf -
if [ $? -ne 0 ]; then
  exit $?
fi

%build
mkdir -p usr/share
mkdir -p usr/share/applications
mkdir -p usr/bin

mv makehuman/MakeHuman.desktop usr/share/applications/MakeHuman.desktop
mv makehuman/makehuman usr/bin/makehuman
mv makehuman usr/share/

%install
rm -rf $RPM_BUILD_ROOT
rm -rf doesnotexist
mkdir -p $RPM_BUILD_ROOT
mv $RPM_BUILD_DIR/usr $RPM_BUILD_ROOT/usr

%files
/usr/share/makehuman
/usr/share/applications
/usr/bin/makehuman

