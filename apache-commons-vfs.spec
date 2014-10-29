%{?_javapackages_macros:%_javapackages_macros}
%global base_name vfs
%global short_name commons-%{base_name}
Name:          apache-commons-vfs
Version:       2.0
Release:       12
Summary:       Commons Virtual File System
License:       ASL 2.0
Url:           http://commons.apache.org/%{base_name}/
Source0:       http://www.apache.org/dist/commons/%{base_name}/source/%{short_name}-%{version}-src.tar.gz

BuildRequires: maven-local
BuildRequires: mvn(com.jcraft:jsch)
BuildRequires: mvn(commons-collections:commons-collections)
BuildRequires: mvn(commons-httpclient:commons-httpclient)
BuildRequires: mvn(commons-logging:commons-logging)
BuildRequires: mvn(commons-net:commons-net)
BuildRequires: mvn(org.apache.ant:ant)
BuildRequires: mvn(org.apache.commons:commons-compress)
BuildRequires: mvn(org.apache.commons:commons-parent)
BuildRequires: mvn(org.apache.maven.plugins:maven-antrun-plugin)
BuildRequires: mvn(org.jdom:jdom)

# test deps
BuildRequires: mvn(junit:junit)

BuildArch:     noarch
Provides:      %{name}2 = %{version}-%{release}

%description
Commons VFS provides a single API for accessing various
different file systems. It presents a uniform view of the
files from various different sources, such as the files on
local disk, on an HTTP server, or inside a Zip archive.
Some of the features of Commons VFS are:
* A single consistent API for accessing files of different
 types.
* Support for numerous file system types.
* Caching of file information. Caches information in-JVM,
 and optionally can cache remote file information on the
 local file system.
* Event delivery.
* Support for logical file systems made up of files from
 various different file systems.
* Utilities for integrating Commons VFS into applications,
 such as a VFS-aware ClassLoader and URLStreamHandlerFactory.
* A set of VFS-enabled Ant tasks.

%package ant
Summary:       Development files for Commons VFS
Requires:      %{name} = %{version}-%{release}

%description ant
This package enables support for the Commons VFS ant tasks.

%package examples
Summary:       Commons VFS Examples
Requires:      %{name} = %{version}-%{release}

%description examples
VFS is a Virtual File System library - Examples.

%package javadoc
Summary:       Javadoc for %{name}

%description javadoc
This package contains javadoc for %{name}.

%prep
%setup -q -n %{short_name}-%{version}
perl -pi -e 's/\r$//g;' *.txt

# Remove unused dependencies
%pom_remove_dep :maven-scm-api
%pom_remove_dep :maven-scm-provider-svnexe
# Remove not available module
%pom_remove_dep :commons-vfs-sandbox
# Disable unwanted module
%pom_disable_module dist

# Fix plugin configuration
%pom_xpath_inject "pom:project/pom:reporting/pom:plugins/pom:plugin[pom:artifactId='maven-javadoc-plugin']/pom:configuration" "
<excludePackageNames>*.webdav.*</excludePackageNames>"
# Fix ant gId
%pom_xpath_set "pom:project/pom:dependencyManagement/pom:dependencies/pom:dependency[pom:artifactId='ant']/pom:groupId" "
org.apache.ant"

%pom_xpath_set "pom:project/pom:dependencies/pom:dependency[pom:artifactId='ant']/pom:groupId" "
org.apache.ant" core

# Remove unwanted dependency
%pom_remove_dep :jackrabbit-webdav core

# Disable jackrabbit-webdav support
%pom_add_plugin org.apache.maven.plugins:maven-compiler-plugin core "
<executions>
  <execution>
    <id>default-compile</id>
    <phase>compile</phase>
    <configuration>
      <excludes>
       <exclude>**/webdav/*</exclude>
      </excludes>
    </configuration>
    <goals>
      <goal>compile</goal>
    </goals>
  </execution>
  <execution>
    <id>default-testCompile</id>
    <phase>test-compile</phase>
    <configuration>
      <testExcludes>
       <exclude>**/webdav/test/*</exclude>
      </testExcludes>
    </configuration>
    <goals>
      <goal>testCompile</goal>
    </goals>
  </execution>
</executions>"

rm -rf core/src/main/java/org/apache/commons/vfs2/provider/webdav
rm -rf core/src/test/java/org/apache/commons/vfs2/provider/webdav
sed -i 's|"webdav",||' core/src/test/java/org/apache/commons/vfs2/util/DelegatingFileSystemOptionsBuilderTest.java

rm -r core/src/test/java/org/apache/commons/vfs2/provider/ram/test/CustomRamProviderTest.java

# not really needed
%pom_remove_plugin :maven-checkstyle-plugin
%pom_remove_plugin :commons-build-plugin
%pom_remove_plugin :findbugs-maven-plugin

# Fix installation directory and symlink
%mvn_file :%{short_name}2 %{name}
%mvn_file :%{short_name}2 %{name}2
%mvn_file :%{short_name}2 %{short_name}
%mvn_file :%{short_name}2 %{short_name}2
%mvn_file :%{short_name}2-examples %{name}-examples
%mvn_file :%{short_name}2-examples %{name}2-examples
%mvn_file :%{short_name}2-examples %{short_name}-examples
%mvn_file :%{short_name}2-examples %{short_name}2-examples

%mvn_alias :commons-vfs2 "org.apache.commons:%{short_name}" "%{short_name}:%{short_name}"
%mvn_alias :commons-vfs2-examples "org.apache.commons:%{short_name}-examples" "%{short_name}:%{short_name}-examples"

# main package wins parent POM
%mvn_package ":commons-vfs2-project" commons-vfs2

%build
%mvn_build -s

%install
%mvn_install

mkdir -p %{buildroot}%{_sysconfdir}/ant.d
echo "ant commons-logging %{short_name}" > %{short_name}
install -p -m 644 %{short_name} %{buildroot}%{_sysconfdir}/ant.d/%{short_name}

%files -f .mfiles-commons-vfs2
%doc LICENSE.txt NOTICE.txt README.txt RELEASE-NOTES.txt

%files examples -f .mfiles-commons-vfs2-examples

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt NOTICE.txt

%files ant
%config %{_sysconfdir}/ant.d/%{short_name}

%changelog
* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Jun 28 2013 gil cattaneo <puntogil@libero.it> 2.0-10
- used pom_xpath_set macro

* Fri Jun 28 2013 gil cattaneo <puntogil@libero.it> 2.0-9
- swith to pom macros
- packaged in /usr/share/java instead of /usr/share/java/apache-commons-vfs

* Fri Jun 28 2013 Michal Srb <msrb@redhat.com> - 2.0-8
- Fix directory ownership

* Thu Jun 27 2013 Michal Srb <msrb@redhat.com> - 2.0-7
- Build with XMvn
- Do not ignore test failures
- Fix BR

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 2.0-5
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Wed Aug  1 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.0-4
- Rebuild against javamail

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jun 18 2012 gil cattaneo <puntogil@libero.it> 2.0-2
- add subpackage ant
- install NOTICE.txt in javadocs subpackage

* Mon May 14 2012 gil cattaneo <puntogil@libero.it> 2.0-1
- initial rpm
