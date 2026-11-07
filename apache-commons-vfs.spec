Name:		apache-commons-vfs
Version:	2.10.0
Release:	1
Summary:	Virtual filesystem for local and remote files
Group:		Development/Java
License:	ASL 2.0
URL:		https://commons.apache.org/proper/commons-vfs/
Source0:	https://github.com/apache/commons-vfs/archive/refs/tags/rel/commons-vfs-%{version}.tar.gz#/commons-vfs-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(commons-logging:commons-logging)
BuildRequires:	mvn(org.apache.commons:commons-lang3)
BuildRequires:	mvn(commons-io:commons-io)
BuildRequires:	mvn(org.apache.commons:commons-collections4)
# Optional at runtime. builddep skips optional dependencies, and the kept providers import them.
BuildRequires:	mvn(commons-net:commons-net)
BuildRequires:	mvn(org.apache.commons:commons-compress)
BuildRequires:	mvn(org.apache.httpcomponents:httpclient)
BuildSystem:	maven
BuildOption(install):	--file-name commons-vfs2 --link %{name} --link %{name}2 --alias org.apache.commons:commons-vfs --alias commons-vfs:commons-vfs

Provides:	%{name}2 = %{version}-%{release}
Obsoletes:	%{name}-javadoc < %{version}-%{release}
Obsoletes:	%{name}-examples < %{version}-%{release}
Obsoletes:	%{name}-ant < %{version}-%{release}

%description
Apache Commons VFS presents local files, archives, and remote
servers through one API. 2.10.0 requires Java 8. Upstream binds the
http and https schemes to HttpClient 5, and splits the Ant tasks and
the HDFS provider into their own modules.

This package ships the core jar. The providers that compile against
system jars stay: local, zip, jar, gzip, tar, bzip2, ftp, ftps, http4,
http4s, ram, res, and temporary. SFTP needs JSch, and the HttpClient 3
and HttpClient 5 providers need libraries that are not packaged, so
those sources are left out. providers.xml still skips them when the
classes are absent. The default URL provider encodes paths with VFS
URIUtils instead of commons-httpclient. Ant tasks, examples,
Jackrabbit WebDAV, and HDFS are not built. Tests are skipped. The
automatic module name is org.apache.commons.vfs2.

%prep
%autosetup -n commons-vfs-rel-commons-vfs-%{version}
python - <<'PY'
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

for gradle in Path(".").rglob("*.gradle"):
    gradle.unlink()
for extra in (Path("gradlew"), Path("gradlew.bat")):
    if extra.is_file():
        extra.unlink()
if Path("gradle").is_dir():
    shutil.rmtree(Path("gradle"))

provider = Path("commons-vfs2/src/main/java/org/apache/commons/vfs2/provider")
for name in ("sftp", "http", "https", "http5", "http5s"):
    path = provider / name
    if not path.is_dir():
        raise SystemExit("missing provider " + name)
    shutil.rmtree(path)

url_name = provider / "URLFileName.java"
text = url_name.read_text(encoding="utf-8")
text = text.replace("import org.apache.commons.httpclient.URIException;\n", "")
text = text.replace(
    "import org.apache.commons.httpclient.util.URIUtil;\n",
    "import org.apache.commons.vfs2.util.URIUtils;\n",
)
text = text.replace("URIUtil.encodePath", "URIUtils.encodePath")
text = text.replace("throws URIException, FileSystemException", "throws FileSystemException")
text = text.replace("throws FileSystemException, URIException", "throws FileSystemException")
text = "\n".join(line for line in text.splitlines() if "URIException" not in line) + "\n"
if "org.apache.commons.httpclient" in text or "URIUtil.encodePath" in text:
    raise SystemExit("URLFileName still imports httpclient")
if "import org.apache.commons.vfs2.util.URIUtils;" not in text:
    raise SystemExit("URIUtils import missing")
url_name.write_text(text, encoding="utf-8")

tasks = Path("commons-vfs2/src/main/resources/org/apache/commons/vfs2/tasks")
if tasks.is_dir():
    shutil.rmtree(tasks)

java_root = Path("commons-vfs2/src/main/java")
files = list(java_root.rglob("*.java"))
if len(files) != 271:
    raise SystemExit("unexpected java file count " + str(len(files)))
forbidden = (
    "org.apache.commons.httpclient",
    "org.apache.hc.",
    "com.jcraft.jsch",
    "org.apache.hadoop",
    "org.apache.jackrabbit",
)
for source in files:
    for line in source.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("import "):
            continue
        for needle in forbidden:
            if needle in stripped:
                raise SystemExit(needle + " remains in " + str(source))

Path("src/main").mkdir(parents=True)
shutil.move(str(java_root), "src/main/java")
shutil.move("commons-vfs2/src/main/resources", "src/main/resources")
for name in (
    "commons-vfs2",
    "commons-vfs2-ant",
    "commons-vfs2-bom",
    "commons-vfs2-distribution",
    "commons-vfs2-examples",
    "commons-vfs2-hdfs",
    "commons-vfs2-jackrabbit1",
    "commons-vfs2-jackrabbit2",
    "commons-vfs2-sandbox",
):
    shutil.rmtree(name)

providers = Path("src/main/resources/org/apache/commons/vfs2/impl/providers.xml").read_text(encoding="utf-8")
for needle in (
    "com.jcraft.jsch.JSch",
    "org.apache.hc.client5.http.classic.HttpClient",
    "org.apache.commons.httpclient.HttpClient",
    "org.apache.http.client.HttpClient",
):
    if needle not in providers:
        raise SystemExit("providers.xml missing " + needle)

NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)

def tag(name):
    return "{" + NS + "}" + name

def add(parent, name, value):
    node = ET.SubElement(parent, tag(name))
    node.text = value
    return node

def dep(parent, group, artifact, version, optional=False):
    node = ET.SubElement(parent, tag("dependency"))
    add(node, "groupId", group)
    add(node, "artifactId", artifact)
    add(node, "version", version)
    if optional:
        add(node, "optional", "true")
    return node

root = ET.Element(tag("project"))
add(root, "modelVersion", "4.0.0")
add(root, "groupId", "org.apache.commons")
add(root, "artifactId", "commons-vfs2")
add(root, "version", "%{version}")
add(root, "name", "Apache Commons VFS")
props = ET.SubElement(root, tag("properties"))
add(props, "maven.compiler.release", "8")
deps = ET.SubElement(root, tag("dependencies"))
dep(deps, "commons-logging", "commons-logging", "1.4.0")
dep(deps, "org.apache.commons", "commons-lang3", "3.21.0")
dep(deps, "commons-io", "commons-io", "2.22.0")
dep(deps, "org.apache.commons", "commons-collections4", "4.6.0")
dep(deps, "commons-net", "commons-net", "3.13.0", optional=True)
dep(deps, "org.apache.commons", "commons-compress", "1.28.0", optional=True)
dep(deps, "org.apache.httpcomponents", "httpclient", "4.5.14", optional=True)
ET.ElementTree(root).write("pom.xml", encoding="utf-8", xml_declaration=True)

pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>commons-vfs2</artifactId>",
    "<maven.compiler.release>8</maven.compiler.release>",
    "<artifactId>commons-collections4</artifactId>",
    "<artifactId>commons-net</artifactId>",
    "<artifactId>commons-compress</artifactId>",
    "<artifactId>httpclient</artifactId>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("commons-httpclient", "httpclient5", "httpcore5", "jsch", "<modules>"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
poms = [item for item in Path(".").rglob("pom.xml")]
if len(poms) != 1:
    raise SystemExit("expected one pom, found " + str(len(poms)))
if list(Path("src/main/java").rglob("*.java")) != files and len(list(Path("src/main/java").rglob("*.java"))) != 271:
    raise SystemExit("moved java tree has the wrong count")
PY

%build -a
cat > manifest-addition <<'EOF'
Automatic-Module-Name: org.apache.commons.vfs2
EOF
jar ufm target/commons-vfs2-%{version}.jar manifest-addition
java --module-path target/commons-vfs2-%{version}.jar --describe-module org.apache.commons.vfs2 > module-describe.txt
# A versioned jar prints "name@version ... automatic", not "name automatic".
grep -q '^org.apache.commons.vfs2' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }

%files -f .mfiles
%doc LICENSE.txt NOTICE.txt README.md RELEASE-NOTES.txt
