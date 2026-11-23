"""Administrator-run dependency supplier. Never run against the worker's denied route.

No application, acceptance suite, deployment or host package installation is run.
The non-secret operator receipt and independent review are mandatory prerequisites.
"""
import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import stat
import zipfile
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request
import venv
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEX = re.compile(r"[0-9a-f]{64}")
SHA = re.compile(r"[0-9a-f]{40}")
PIP_VERSION = "26.2.2"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(args, log, env=None, cwd=None):
    # Preserve complete command output and real status without flooding CI console.
    with Path(log).open("wb") as stream:
        result = subprocess.run(args, stdout=stream, stderr=subprocess.STDOUT, env=env, cwd=cwd)
    require(result.returncode == 0, "command failed; inspect " + Path(log).name)


class Downloads:
    def __init__(self, receipt, ledger):
        self.receipt, self.ledger = receipt, Path(ledger)
        self.records = []
        self.redirects = []
        outer = self

        class Redirects(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                outer.allowed(newurl)
                outer.redirects.append({"status": code,
                    "from": urllib.parse.urlsplit(req.full_url)._replace(query="", fragment="").geturl(),
                    "to": urllib.parse.urlsplit(newurl)._replace(query="", fragment="").geturl()})
                # Anonymous registry bearer tokens must not reach a CDN redirect.
                request = super().redirect_request(req, fp, code, msg, headers, newurl)
                if request is not None and urllib.parse.urlsplit(newurl).netloc != urllib.parse.urlsplit(req.full_url).netloc:
                    request.remove_header("Authorization")
                return request

        self.opener = urllib.request.build_opener(Redirects())

    def allowed(self, url):
        parsed = urllib.parse.urlsplit(url)
        require(parsed.scheme == "https" and not parsed.username and not parsed.password and parsed.port in (None, 443), "non-HTTPS or credential-bearing URL refused")
        require(parsed.hostname in self.receipt["allowed_https_hosts"], "unapproved endpoint host")
        require(any(row.get("permitted") is True and row.get("evidence_reference")
                    and url.startswith(row["url_prefix"]) for row in self.receipt["verified_endpoints"]),
                "endpoint path/redirect lacks operator permission evidence")

    def get(self, url, destination, expected=None, headers=None, max_bytes=400_000_000):
        self.allowed(url)
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        size = 0
        h = hashlib.sha256()
        self.redirects = []
        with self.opener.open(urllib.request.Request(url, headers=headers or {}), timeout=60) as response, destination.open("wb") as output:
            self.allowed(response.url)
            effective = urllib.parse.urlsplit(response.url)
            for chunk in iter(lambda: response.read(1024 * 1024), b""):
                size += len(chunk)
                require(size <= max_bytes, "download size limit exceeded")
                output.write(chunk)
                h.update(chunk)
            record = {"source": urllib.parse.urlsplit(url)._replace(query="", fragment="").geturl(),
                      "effective": effective._replace(query="", fragment="").geturl(),
                      "bytes": size, "sha256": h.hexdigest(), "file": destination.name, "redirect_chain": list(self.redirects)}
        require(expected is None or h.hexdigest() == expected.removeprefix("sha256:"), "download checksum mismatch")
        self.records.append(record)
        write(self.ledger, self.records)
        return h.hexdigest()

    def json(self, url, destination, headers=None):
        self.get(url, destination, headers=headers, max_bytes=20_000_000)
        return read(destination)


def preflight(args, output):
    receipt = json.loads(os.environ["OPERATOR_PREFLIGHT_JSON"])
    require(receipt.get("schema") == "delivery-lab.operator-dependency-preflight.v1" and receipt.get("verified") is True, "verified operator receipt required")
    for key in ("operator_identity", "operator_evidence_reference", "assurance_review_reference", "permitted_retrieval_method", "persistent_copy_destination"):
        require(isinstance(receipt.get(key), str) and bool(receipt[key].strip()), "missing operator evidence: " + key)
    require(receipt.get("source_commit") == args.source and SHA.fullmatch(args.source), "source SHA mismatch")
    require(digest(HERE / "workflow.yml.in") == receipt.get("workflow_sha256"), "inert workflow checksum mismatch")
    require(digest(args.published_workflow) == receipt["workflow_sha256"], "published workflow differs from reviewed bytes")
    runner = receipt["runner"]
    require(runner["label"] == "ubuntu-24.04" and os.environ.get("RUNNER_OS") == "Linux", "runner label/OS mismatch")
    release = dict(line.split("=", 1) for line in Path("/etc/os-release").read_text().splitlines() if "=" in line)
    require(release.get("ID", "").strip('"') == "ubuntu" and release.get("VERSION_ID", "").strip('"') == "24.04", "runner OS release mismatch")
    require(platform.machine() == runner["architecture"] == "x86_64", "runner architecture mismatch")
    require(platform.libc_ver() == ("glibc", runner["glibc"]) and runner["glibc"] == "2.39", "glibc mismatch")
    require(platform.python_version() == runner["python_driver"] == "3.12.3", "driver CPython mismatch")
    require(os.environ.get("ImageVersion") == runner["image_version"] and runner["image_version"], "runner image version differs from operator verification")
    docker_version = subprocess.check_output(["docker", "version", "--format", "{{.Server.Version}}"], text=True).strip()
    require(docker_version == runner.get("docker_version") and docker_version, "Docker version differs from operator verification")
    require(receipt.get("retention_days") == 14, "retention policy mismatch")
    require(receipt["allowed_https_hosts"] and receipt["verified_endpoints"], "permitted endpoint inventory missing")
    for host in receipt["allowed_https_hosts"]:
        require(isinstance(host, str) and re.fullmatch(r"[a-z0-9.-]+", host) and "*" not in host, "exact host names required")
    for row in receipt["verified_endpoints"]:
        require(row.get("permitted") is True and row.get("evidence_reference"), "endpoint permission unverified")
        parsed = urllib.parse.urlsplit(row["url_prefix"])
        require(parsed.scheme == "https" and parsed.hostname in receipt["allowed_https_hosts"] and not parsed.username and not parsed.password and not parsed.query and not parsed.fragment, "invalid endpoint inventory")
    write(output / "operator-preflight.json", receipt)
    write(output / "provenance.json", {"source_commit": args.source, "workflow_commit": os.environ.get("GITHUB_WORKFLOW_SHA"),
          "repository": os.environ.get("GITHUB_REPOSITORY"), "run_id": os.environ.get("GITHUB_RUN_ID"),
          "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"), "runner_name": os.environ.get("RUNNER_NAME"),
          "runner_image": runner["image_version"], "runtime": platform.platform(), "python": sys.version,
          "python_executable": sys.executable, "python_executable_sha256": digest(sys.executable),
          "os_release": release,
          "workflow_sha256": receipt["workflow_sha256"], "helper_sha256": digest(HERE / "supply.py"), "kind": args.kind,
          "operator": receipt["operator_identity"], "artifact_identity": "External upload receipt and operator retention record required; not self-referenced"})
    write(output / "retrieval.json", {"permitted_method": receipt["permitted_retrieval_method"],
          "persistent_destination": receipt["persistent_copy_destination"], "retention_days": 14,
          "persistent_copy_verified": False, "release_gate": "Operator must save and independently checksum copied bytes before CI expiry"})
    return receipt


def wheels(output, requirements, receipt):
    """Resolve on the actual target interpreter, capture report, then install offline."""
    downloads = Downloads(receipt, output / "wheel-downloads.json")
    wheel_dir = output / "wheelhouse"
    wheel_dir.mkdir()
    meta = downloads.json(f"https://pypi.org/pypi/pip/{PIP_VERSION}/json", output / "pip-metadata.json")
    choices = [x for x in meta["urls"] if x["filename"] == f"pip-{PIP_VERSION}-py3-none-any.whl"]
    require(len(choices) == 1, "exact pip wheel unavailable")
    pip_info = choices[0]
    pip_wheel = wheel_dir / pip_info["filename"]
    downloads.get(pip_info["url"], pip_wheel, pip_info["digests"]["sha256"])
    (output / "toolchain.lock").write_text(f"pip=={PIP_VERSION} --hash=sha256:{digest(pip_wheel)}\n")
    # The operator must verify pip's upstream/redirect egress before dispatch.
    # This invocation is a resolver, not a network-policy enforcement mechanism.
    bootstrap = "import sys; sys.path.insert(0,sys.argv.pop(1)); from pip._internal.cli.main import main; raise SystemExit(main())"
    report = output / "resolution.json"
    run([sys.executable, "-c", bootstrap, str(pip_wheel), "--isolated", "--disable-pip-version-check",
         "install", "--dry-run", "--ignore-installed", "--only-binary=:all:", "--index-url", "https://pypi.org/simple",
         "--report", str(report), *requirements], output / "resolver.log")
    resolved = read(report)
    pins, inventory = [], []
    for row in resolved["install"]:
        info = row["download_info"]
        url = info["url"]
        filename = urllib.parse.unquote(urllib.parse.urlsplit(url).path.rsplit("/", 1)[-1])
        require(filename.endswith(".whl") and filename == Path(filename).name, "non-wheel result rejected")
        expected = info["archive_info"]["hashes"]["sha256"]
        require(HEX.fullmatch(expected), "resolver supplied no valid hash")
        downloads.get(url, wheel_dir / filename, expected)
        name, version = row["metadata"]["name"], row["metadata"]["version"]
        require(re.fullmatch(r"[A-Za-z0-9_.-]+", name) and re.fullmatch(r"[A-Za-z0-9_.+!-]+", version), "invalid package identity")
        pins.append(f"{name}=={version} --hash=sha256:{expected}")
        inventory.append({"name": name, "version": version, "filename": filename, "bytes": (wheel_dir / filename).stat().st_size,
                          "sha256": expected, "source": url, "final_url": downloads.records[-1]["effective"],
                          "redirect_chain": downloads.records[-1]["redirect_chain"], "wheel_tags": filename[:-4].rsplit("-", 3)[-3:]})
    (output / "requirements.lock").write_text("\n".join(sorted(pins)) + "\n")
    write(output / "wheel-inventory.json", inventory)
    write(output / "resolver-runtime.json", {"python": sys.version, "machine": platform.machine(), "libc": platform.libc_ver(), "pip": PIP_VERSION})
    write(output / "resolver.json", {"python": sys.version, "implementation": platform.python_implementation(),
          "machine": platform.machine(), "libc": platform.libc_ver(), "resolver": "pip==" + PIP_VERSION,
          "toolchain_wheel_sha256": digest(pip_wheel), "index": "https://pypi.org/simple",
          "flags": ["--isolated", "--disable-pip-version-check", "install", "--dry-run", "--ignore-installed", "--only-binary=:all:"],
          "direct_requirements": requirements, "graph_and_metadata": "resolution.json", "raw_log": "resolver.log",
          "compatible_tags": "offline-compatible-tags.txt", "installer_provenance": "toolchain-inventory.json"})
    write(output / "toolchain-inventory.json", [{"name": "pip", "version": PIP_VERSION,
          "filename": pip_wheel.name, "bytes": pip_wheel.stat().st_size, "sha256": digest(pip_wheel),
          "source": pip_info["url"], "purpose": "separately pinned resolver/installer"}])
    return output


def install_offline(output, log_prefix):
    temp = Path(tempfile.mkdtemp(prefix="delivery-lab-offline-"))
    venv.EnvBuilder(with_pip=True).create(temp)
    python = temp / "bin/python"
    for lock in ("toolchain.lock", "requirements.lock"):
        run([str(python), "-m", "pip", "--isolated", "--disable-pip-version-check", "install", "--no-index", "--no-cache-dir",
             "--only-binary=:all:", "--require-hashes", "--find-links", str(output / "wheelhouse"), "-r", str(output / lock)], output / (log_prefix + lock + ".install.log"))
    run([str(python), "-m", "pip", "--isolated", "--disable-pip-version-check", "check"], output / (log_prefix + "pip-check.log"))
    run([str(python), "-m", "pip", "--isolated", "--disable-pip-version-check", "list", "--format=json"], output / (log_prefix + "installed.json"))
    run([str(python), "-c", "from pip._vendor.packaging.tags import sys_tags; print('\\n'.join(map(str,sys_tags())))"], output / (log_prefix + "compatible-tags.txt"))
    return python, temp


def app(args, output, receipt):
    spec = read(HERE / "app-input.json")
    downloads = Downloads(receipt, output / "image-downloads.json")
    # Anonymous Docker Hub bearer token, kept in memory and never archived/logged.
    auth_url = "https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/python:pull"
    downloads.allowed(auth_url)
    with downloads.opener.open(auth_url, timeout=30) as response:
        token = json.load(response)["token"]
    headers = {"Authorization": "Bearer " + token, "Accept": "application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json"}
    root = "https://registry-1.docker.io/v2/library/python/"
    index = downloads.json(root + "manifests/" + spec["target"]["base_tag"], output / "registry-index.json", headers)
    choices = [x for x in index.get("manifests", []) if x.get("platform", {}).get("os") == "linux" and x.get("platform", {}).get("architecture") == "amd64" and not x.get("platform", {}).get("variant")]
    require(len(choices) == 1, "exact linux/amd64 base manifest unavailable")
    descriptor = choices[0]
    oci = output / "base-oci"
    blob_dir = oci / "blobs/sha256"
    child = blob_dir / descriptor["digest"].removeprefix("sha256:")
    downloads.get(root + "manifests/" + descriptor["digest"], child, descriptor["digest"], headers)
    manifest = read(child)
    for entry in [manifest["config"], *manifest["layers"]]:
        require(re.fullmatch(r"sha256:[0-9a-f]{64}", entry["digest"]), "unsupported blob digest")
        path = blob_dir / entry["digest"].split(":")[1]
        downloads.get(root + "blobs/" + entry["digest"], path, entry["digest"], headers)
        require(path.stat().st_size == entry["size"], "blob size mismatch")
    write(oci / "oci-layout", {"imageLayoutVersion": "1.0.0"})
    write(oci / "index.json", {"schemaVersion": 2, "manifests": [descriptor]})
    image = "python@" + descriptor["digest"]
    write(output / "base-image.json", {"tag": spec["target"]["base_tag"], "platform": "linux/amd64",
          "registry_index_digest": "sha256:" + digest(output / "registry-index.json"), "platform_manifest_digest": descriptor["digest"],
          "config_digest": manifest["config"]["digest"], "pull_reference": image, "selection": spec["selection_provenance"]})
    # This is the operator-approved CI runner, not a worker-side Docker proxy bypass.
    run(["docker", "pull", "--platform", "linux/amd64", image], output / "docker-pull.log")
    loaded_config = subprocess.check_output(["docker", "image", "inspect", "--format", "{{.Id}}", image], text=True).strip()
    require(loaded_config == manifest["config"]["digest"], "Docker config digest mismatch")
    run(["docker", "image", "save", "--output", str(output / "base.docker.tar"), loaded_config], output / "docker-save.log")
    container_env = {"DELIVERY_LAB_DEPENDENCY_RECEIPT": json.dumps(receipt)}
    env = dict(os.environ, **container_env)
    run(["docker", "run", "--rm", "--platform", "linux/amd64", "--label", "com.logsoftgrup.pilot=delivery-lab",
         "--label", "com.logsoftgrup.environment=dependency-supply", "--mount", f"type=bind,src={HERE},dst=/supplier,readonly",
         "--mount", f"type=bind,src={output},dst=/bundle", "--env", "DELIVERY_LAB_DEPENDENCY_RECEIPT", image,
         "python", "/supplier/supply.py", "app-wheels", "--output", "/bundle"], output / "app-resolve.log", env=env)
    run(["docker", "run", "--rm", "--pull", "never", "--network", "none", "--platform", "linux/amd64",
         "--label", "com.logsoftgrup.pilot=delivery-lab", "--label", "com.logsoftgrup.environment=dependency-supply",
         "--mount", f"type=bind,src={HERE},dst=/supplier,readonly", "--mount", f"type=bind,src={output},dst=/bundle",
         loaded_config, "python", "/supplier/supply.py", "app-offline", "--output", "/bundle"], output / "app-offline.log")
    run(["docker", "version", "--format", "{{json .}}"], output / "docker-version.json")


def app_wheels(output):
    spec = read(HERE / "app-input.json")
    require(platform.python_version() == spec["target"]["python"] and platform.machine() == "x86_64", "APP target Python/architecture mismatch")
    receipt = json.loads(os.environ["DELIVERY_LAB_DEPENDENCY_RECEIPT"])
    wheels(output, spec["direct_requirements"], receipt)


def app_offline(output):
    python, temp = install_offline(output, "offline-")
    try:
        run([str(python), "-c", "import fastapi,uvicorn,sqlite3; print(fastapi.__version__,uvicorn.__version__,sqlite3.sqlite_version)"], output / "app-imports.log")
        write(output / "offline-isolation.json", {"method": "Docker --network none --pull never; exact loaded config digest", "routes": Path("/proc/net/route").read_text()})
    finally:
        shutil.rmtree(temp)


def browser_acquire(python, output, receipt):
    env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=str(output / "browser"))
    package = Path(subprocess.check_output([str(python), "-c", "import pathlib,playwright;print(pathlib.Path(playwright.__file__).parent)"], text=True).strip())
    driver = package / "driver"
    script = r"""const path=require('path'); const root=process.argv[1];
const {registry}=require(path.join(root,'lib/server/registry/index.js'));
const {hostPlatform}=require(path.join(root,'lib/server/utils/hostPlatform.js'));
const names=['chromium','chromium-headless-shell','ffmpeg'];
console.log(JSON.stringify({platform:hostPlatform,executables:names.map(name=>{const e=registry.findExecutable(name);if(!e)throw Error('missing component');return {name,directory:e.directory,executable:e.executablePath(),version:e.browserVersion,urls:e.downloadURLs};})}));"""
    plan = json.loads(subprocess.check_output([str(driver / "node"), "-e", script, str(driver / "package")], env=env, text=True))
    descriptor = driver / "package/browsers.json"
    shutil.copyfile(descriptor, output / "playwright-browsers.json")
    write(output / "browser-selection.json", plan)
    downloads = Downloads(receipt, output / "browser-downloads.json")
    archives = []
    for component in plan["executables"]:
        directory = Path(component["directory"]).resolve()
        require(directory.is_relative_to((output / "browser").resolve()), "browser cache path escaped bundle")
        require(component["urls"], "package supplied no browser URL")
        # One selected URL, no mirror retry. Unexpected redirects fail closed.
        archive = output / "browser-archives" / (component["name"] + ".zip")
        downloads.get(component["urls"][0], archive)
        with zipfile.ZipFile(archive) as zipped:
            members = zipped.infolist()
            require(len(members) <= 50_000 and sum(x.file_size for x in members) <= 3 * 1024**3, "browser archive bounds exceeded")
            paths = set()
            for member in members:
                target = (directory / member.filename).resolve()
                mode = member.external_attr >> 16
                require(target.is_relative_to(directory) and not stat.S_ISLNK(mode) and target not in paths, "unsafe browser archive member")
                paths.add(target)
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    target.chmod(0o755)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with zipped.open(member) as source, target.open("wb") as destination:
                        shutil.copyfileobj(source, destination)
                    target.chmod(0o755 if mode & 0o111 else 0o644)
        executable = Path(component["executable"])
        require(executable.is_relative_to(directory) and executable.is_file(), "selected executable missing")
        executable.chmod(0o755)
        (directory / "INSTALLATION_COMPLETE").touch()
        archives.append({"component": component["name"], "version": component.get("version"),
                         "archive": archive.relative_to(output).as_posix(), "archive_sha256": digest(archive),
                         "selected_url": component["urls"][0], "executable": executable.relative_to(output).as_posix(),
                         "executable_sha256": digest(executable), "mode": oct(executable.stat().st_mode & 0o777)})
    write(output / "browser-inventory.json", {"playwright": "1.56.0", "descriptor_sha256": digest(descriptor),
          "platform": plan["platform"], "components": archives, "browser_tree": [
              {"path": x.relative_to(output).as_posix(), "sha256": digest(x), "bytes": x.stat().st_size, "mode": oct(x.stat().st_mode & 0o777)}
              for x in sorted((output / "browser").rglob("*")) if x.is_file()]})


def test(args, output, receipt):
    root = Path(args.test_source).resolve()
    expected_source = "a94938bfcb37745c93843816a66d990cc46d888e"
    require(receipt.get("test_source_commit") == expected_source, "TEST-SUPPLY-1 exact source required")
    git_sha = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    require(git_sha == expected_source, "Assurance source mismatch")
    contract_path = root / "pilot/delivery-lab/assurance/supply/test-runtime-contract.v1.json"
    require(digest(contract_path) == "c8265cd20750d54677fba4944d4307a07820cdcebde408b6621b159b7093523d", "Assurance contract mismatch")
    contract = read(contract_path)
    require(contract["schema"] == "delivery-lab.test-supply-contract.v1", "TEST contract schema mismatch")
    require(receipt.get("offline_isolation") == "sudo-netns-loopback-v1" and receipt.get("isolation_evidence_reference"), "operator-verified offline isolation required")
    # The immutable TC-D1 tree remains present in TEST-SUPPLY-1; read, never edit.
    input_path = root / "pilot/delivery-lab/assurance/tests/requirements.in"
    require(input_path.is_file(), "TC-D1 requirements input missing")
    require(digest(input_path) == read(HERE / "test-input-interface.json")["requirements_in_sha256"], "TC-D1 requirements bytes changed")
    shutil.copyfile(input_path, output / "requirements.in")
    write(output / "assurance-contract.json", contract)
    wheels(output, ["pytest==8.4.2", "playwright==1.56.0"], receipt)
    python, temp = install_offline(output, "selection-")
    try:
        browser_acquire(python, output, receipt)
    finally:
        shutil.rmtree(temp)
    # Process-scoped network namespace; no host policy/firewall/package change.
    run(["sudo", "-n", "unshare", "--net", "--", "/bin/sh", "-c", 'ip link set lo up && exec "$@"',
         "delivery-lab-netns", sys.executable, str(HERE / "supply.py"), "test-offline", "--output", str(output)], output / "test-offline.log")
    require(read(output / "offline-verification.json")["result"] == "PASS", "TEST runtime smoke failed")


def test_offline(output):
    require(platform.python_version() == "3.12.3" and platform.libc_ver() == ("glibc", "2.39"), "offline TEST target mismatch")
    interfaces = [name for _, name in socket.if_nameindex()]
    require(set(interfaces) == {"lo"}, "offline namespace has a non-loopback interface")
    write(output / "offline-isolation.json", {"method": "sudo-netns-loopback-v1", "interfaces": interfaces, "routes": Path("/proc/net/route").read_text()})
    python, temp = install_offline(output, "offline-")
    try:
        run([str(python), str(HERE / "supply.py"), "browser-smoke", "--output", str(output)], output / "browser-smoke.log",
            env=dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=str(output / "browser")))
    finally:
        shutil.rmtree(temp)


def browser_smoke(output):
    # Producer dependency smoke only; no application or accepted test suite is run.
    from playwright.sync_api import sync_playwright
    inventory = read(output / "browser-inventory.json")
    libraries = []
    import playwright
    elf_files = [Path(playwright.__file__).parent / "driver/node"]
    for candidate in (output / "browser").rglob("*"):
        if candidate.is_file():
            with candidate.open("rb") as stream:
                if stream.read(4) == b"\x7fELF":
                    elf_files.append(candidate)
    for index, executable in enumerate(elf_files):
        result = subprocess.run(["ldd", str(executable)], capture_output=True, text=True)
        text = result.stdout + result.stderr
        (output / ("runtime-" + str(index) + "-ldd.log")).write_text(text)
        static = "not a dynamic executable" in text or "statically linked" in text
        require((result.returncode == 0 or static) and "not found" not in text, "browser runtime library missing")
        for path in re.findall(r"(/[^\s()]+)", result.stdout):
            library = Path(path)
            if library.is_file():
                libraries.append({"path": str(library), "sha256": digest(library), "disposition": "already-present-on-CI; consumer must verify", "required_by": str(executable)})
    run(["dpkg-query", "-W", "-f=${binary:Package}\t${Version}\n"], output / "os-package-versions.txt")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content("<title>Dependency supply smoke</title><p>Synthetic dependency check</p>")
        require(page.title() == "Dependency supply smoke", "synthetic browser smoke failed")
        descendants = {os.getpid()}
        parents = {}
        for entry in Path("/proc").iterdir():
            if entry.name.isdecimal():
                try:
                    parents[int(entry.name)] = int((entry / "stat").read_text().rsplit(")", 1)[1].split()[1])
                except (OSError, ValueError):
                    pass
        changed = True
        while changed:
            new = {pid for pid, parent in parents.items() if parent in descendants}
            changed = bool(new - descendants)
            descendants |= new
        actual = set()
        for pid in descendants:
            try:
                path = Path(os.readlink(f"/proc/{pid}/exe"))
                if path.is_relative_to(output / "browser"):
                    actual.add(str(path))
            except OSError:
                pass
        selected = next(x for x in inventory["components"] if x["component"] == "chromium-headless-shell")
        require(str(output / selected["executable"]) in actual, "default launch executable not established")
        require(browser.version == selected["version"], "actual browser version differs from package descriptor")
        write(output / "offline-verification.json", {"result": "PASS", "scope": "producer dependency smoke, not TC.V or acceptance",
              "browser_version": browser.version, "actual_executables": [{"path": x, "sha256": digest(x)} for x in sorted(actual)],
              "page_title": page.title()})
        browser.close()
    write(output / "runtime-libraries.json", {"os_release": Path("/etc/os-release").read_text(), "glibc": platform.libc_ver(),
          "library_inventory": libraries, "package_versions_file": "os-package-versions.txt", "missing": [], "consumer_compatibility": "UNVERIFIED"})


def finish(output, kind):
    files = []
    for path in sorted(output.rglob("*")):
        require(not path.is_symlink(), "bundle symlink rejected")
        if path.is_file():
            files.append({"path": path.relative_to(output).as_posix(), "bytes": path.stat().st_size, "sha256": digest(path), "mode": oct(path.stat().st_mode & 0o777)})
    write(output / "bundle-manifest.json", {"schema": "delivery-lab.dependency-bundle.v1", "kind": kind,
          "status": "SUPPLIER_COMPLETE_REQUIRES_INDEPENDENT_CONSUMER_VERIFICATION", "files": files})
    archive = output.parent / (kind + "-bundle.tar.gz")
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(output, arcname=kind.upper())
    (output.parent / (archive.name + ".sha256")).write_text(digest(archive) + "  " + archive.name + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("app", "test", "app-wheels", "app-offline", "test-offline", "browser-smoke"))
    parser.add_argument("--output", required=True)
    parser.add_argument("--source")
    parser.add_argument("--published-workflow")
    parser.add_argument("--test-source")
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    helpers = {"app-wheels": app_wheels, "app-offline": app_offline, "test-offline": test_offline, "browser-smoke": browser_smoke}
    if args.kind in helpers:
        helpers[args.kind](output)
        return
    receipt = preflight(args, output)
    (app if args.kind == "app" else test)(args, output, receipt)
    finish(output, args.kind)
    print(json.dumps({"kind": args.kind, "archive": args.kind + "-bundle.tar.gz", "result": "supplier-complete; independent verification pending"}))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Never echo request headers, anonymous bearer tokens or signed redirect queries.
        print(json.dumps({"result": "failed", "error_type": type(error).__name__, "detail": str(error) if isinstance(error, ValueError) else "See preserved stage evidence; no automatic retry."}), file=sys.stderr)
        raise SystemExit(1)
