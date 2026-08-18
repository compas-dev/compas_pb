import gzip
import os
import platform
import stat
import tarfile
import urllib.request
import zipfile
from pathlib import Path

from invoke.tasks import task

PROTOC_VERSION = "31.1"
PROTOC_GEN_DOCS_VERSION = "1.5.1"
PROTOC_GEN_ES_VERSION = "2.14.0"

# Languages protoc emits natively, with no extra plugin.
PROTO_TARGET_LANGUAGES = ["cpp", "csharp", "java", "objc", "php", "ruby"]

# Languages that need a third-party protoc plugin. Maps the language name used in asset
# names to the protoc flag prefix the plugin registers (``--es_out`` for protobuf-es), so
# javascript and go can be added here the same way.
PROTO_PLUGIN_LANGUAGES = {"typescript": "es"}

ALL_PROTO_TARGET_LANGUAGES = PROTO_TARGET_LANGUAGES + list(PROTO_PLUGIN_LANGUAGES)

_PROTOC_ARCH_MAPPING = {
    "x86_64": "x86_64",
    "aarch64": "aarch_64",
    "arm64": "aarch_64",
    "amd64": "x86_64",
}

_DOCSPLUGIN_ARCH_MAPPING = {
    "x86_64": "amd64",
    "aarch64": "arm64",
    "arm64": "arm64",
    "amd64": "amd64",
}


def _get_platform_info():
    system = platform.system().lower()
    arch = platform.machine().lower()

    if system not in ("linux", "darwin", "windows"):
        raise RuntimeError(f"Unsupported platform: {system} {arch}")

    return system, arch


def _get_protoc_download_url(version=PROTOC_VERSION):
    base_url = f"https://github.com/protocolbuffers/protobuf/releases/download/v{version}/"
    system, arch = _get_platform_info()

    protoc_arch = _PROTOC_ARCH_MAPPING.get(arch)
    if not protoc_arch:
        raise RuntimeError(f"Unsupported architecture for protoc: {arch}")

    if system == "linux":
        return base_url + f"protoc-{version}-linux-{protoc_arch}.zip"
    elif system == "darwin":
        return base_url + f"protoc-{version}-osx-universal_binary.zip"
    elif system == "windows":
        return base_url + f"protoc-{version}-win64.zip"


def _get_docsplugin_download_url(version=PROTOC_GEN_DOCS_VERSION):
    base_url = f"https://github.com/pseudomuto/protoc-gen-doc/releases/download/v{version}/"
    system, arch = _get_platform_info()

    docs_arch = _DOCSPLUGIN_ARCH_MAPPING.get(arch)
    if not docs_arch:
        raise RuntimeError(f"Unsupported architecture for protoc-gen-doc: {arch}")

    return base_url + f"protoc-gen-doc_{version}_{system}_{docs_arch}.tar.gz"


def _get_cached_protoc_path():
    cache_dir = Path.home() / ".cache" / "protoc" / PROTOC_VERSION
    protoc_bin = cache_dir / "bin" / "protoc"
    if platform.system() == "Windows":
        protoc_bin = protoc_bin.with_suffix(".exe")

    return protoc_bin, cache_dir


def _download_and_extract_docsplugin(url, extract_path):
    archive_path = extract_path / "protoc-gen-doc.tar.gz"
    urllib.request.urlretrieve(url, archive_path)

    with gzip.open(archive_path, "rb") as gz_ref:
        with tarfile.TarFile(fileobj=gz_ref, mode="r") as tar_ref:
            tar_ref.extractall(extract_path)

    archive_path.unlink()


def _download_and_extract_protoc(url, extract_path):
    archive_path = extract_path / "protoc.zip"
    print(f"Downloading protoc from {url} to {archive_path}")
    urllib.request.urlretrieve(url, archive_path)

    with zipfile.ZipFile(archive_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    archive_path.unlink()


def _get_cached_protoc_gen_es_path():
    cache_dir = Path.home() / ".cache" / "protoc-gen-es" / PROTOC_GEN_ES_VERSION
    plugin_bin = cache_dir / "node_modules" / ".bin" / "protoc-gen-es"
    if platform.system() == "Windows":
        plugin_bin = plugin_bin.with_suffix(".cmd")

    return plugin_bin, cache_dir


def setup_protoc_gen_es(ctx):
    """Install the protobuf-es code generator, and return the path to its executable.

    protoc has no native TypeScript output, so TypeScript bindings come from
    ``@bufbuild/protoc-gen-es``. It is an npm package, so this needs node on PATH. The
    install is cached per version alongside the protoc cache.
    """
    plugin_bin, cache_dir = _get_cached_protoc_gen_es_path()

    if plugin_bin.exists():
        print(f"Using cached protoc-gen-es at: {plugin_bin}")
        return plugin_bin

    print(f"protoc-gen-es not found in cache. Installing to: {cache_dir}")
    cache_dir.mkdir(parents=True, exist_ok=True)
    ctx.run(
        f'npm install --silent --no-package-lock --prefix "{cache_dir}" '
        f"@bufbuild/protoc-gen-es@{PROTOC_GEN_ES_VERSION}"
    )

    if not plugin_bin.exists():
        raise FileNotFoundError(f"Failed to find protoc-gen-es after install: {plugin_bin}")

    print("Install complete.")
    return plugin_bin


def setup_protoc():
    protoc_bin, cache_dir = _get_cached_protoc_path()
    plugin_executable = protoc_bin.parent / "protoc-gen-doc"

    if platform.system() == "Windows":
        plugin_executable = plugin_executable.with_suffix(".exe")
        protoc_bin = protoc_bin.with_suffix(".exe")

    if not protoc_bin.exists() or not plugin_executable.exists():
        print(f"protoc not found in cache. Downloading to: {cache_dir}")
        cache_dir.mkdir(parents=True, exist_ok=True)

        url = _get_protoc_download_url()
        _download_and_extract_protoc(url, cache_dir)

        docsplugin_url = _get_docsplugin_download_url()
        _download_and_extract_docsplugin(docsplugin_url, protoc_bin.parent)

        if platform.system() in ["Linux", "Darwin"]:
            mode = os.stat(protoc_bin)
            os.chmod(protoc_bin, mode.st_mode | stat.S_IEXEC)

            mode = os.stat(plugin_executable)
            os.chmod(plugin_executable, mode.st_mode | stat.S_IEXEC)

        if not protoc_bin.exists():
            raise FileNotFoundError("Failed to find protoc binary after extraction.")
        print("Download complete.")
    else:
        print(f"Using cached protoc at: {protoc_bin}")

    return protoc_bin, plugin_executable


@task(help={"target_language": "Output language for generated classes (e.g., 'python')"})
def generate_proto_classes(ctx, target_language: str = "python"):
    protoc_path, _ = setup_protoc()

    if target_language == "python":
        proto_out_folder = Path(ctx.proto_out_folder)
    elif target_language in ALL_PROTO_TARGET_LANGUAGES:
        proto_out_folder = _generated_root(ctx) / target_language
        proto_out_folder.mkdir(parents=True, exist_ok=True)
    else:
        supported = ", ".join(["python"] + ALL_PROTO_TARGET_LANGUAGES)
        raise ValueError(f"Target language '{target_language}' not supported. Choose one of: {supported}")

    # Plugin-backed languages replace the --<lang>_out flag with the plugin's own flag,
    # and need the plugin binary passed explicitly since it is not on PATH.
    plugin_flag = PROTO_PLUGIN_LANGUAGES.get(target_language)
    plugin_path = setup_protoc_gen_es(ctx) if plugin_flag == "es" else None

    for idl_file in Path(ctx.proto_folder).glob("*.proto"):
        cmd = f"{protoc_path} "
        cmd += " ".join(f"--proto_path={p}" for p in ctx.proto_include_paths)

        if plugin_flag:
            cmd += f' --plugin=protoc-gen-{plugin_flag}="{plugin_path}"'
            cmd += f" --{plugin_flag}_out={proto_out_folder}"
            if plugin_flag == "es":
                # Emit TypeScript rather than JavaScript + .d.ts.
                cmd += f" --{plugin_flag}_opt=target=ts"
            cmd += f" {idl_file}"
        else:
            cmd += f" --{target_language}_out={proto_out_folder} {idl_file}"

        if target_language == "python":
            cmd += f" --pyi_out={proto_out_folder}"

        print(f"Running: {cmd}")
        ctx.run(cmd)


def _package_name(ctx) -> str:
    """Distribution name used to label release assets.

    Defaults to compas_pb, so any package that owns .proto files can reuse these tasks by
    setting ``package_name`` in its invoke configuration.
    """
    return ctx.config.get("package_name", "compas_pb")


def _generated_root(ctx) -> Path:
    """Folder the per-language bindings are generated into before being zipped."""
    configured = ctx.config.get("generated_folder", None)
    if configured:
        return Path(configured)
    return Path(ctx.proto_out_folder) / _package_name(ctx) / "generated"


def _asset_version(language: str) -> str:
    """Version marker for a generated-bindings asset.

    Natively-emitted languages are pinned by the protoc that produced them. Plugin-backed
    languages are pinned by the plugin version instead, since that is what shapes the
    generated API — protoc only feeds it a descriptor.
    """
    if language in PROTO_PLUGIN_LANGUAGES:
        return PROTOC_GEN_ES_VERSION if PROTO_PLUGIN_LANGUAGES[language] == "es" else PROTOC_VERSION
    return PROTOC_VERSION


@task()
def create_proto_bundle(ctx):
    """Zip the .proto schemas themselves for release upload.

    Every downstream generator needs the schemas, not just the bindings compas_pb happens
    to generate. Publishing them is what lets a consumer pin a schema version instead of
    scraping this repository at some ref.
    """
    dist_dir = Path(ctx.base_folder) / "dist" / "proto"
    dist_dir.mkdir(parents=True, exist_ok=True)

    zip_path = dist_dir / f"{_package_name(ctx)}-proto.zip"
    zip_path.unlink(missing_ok=True)

    proto_root = Path(ctx.proto_include_paths[0])
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for item in sorted(proto_root.rglob("*.proto")):
            arcname = str(item.relative_to(proto_root))
            zipf.write(item, arcname)
            print(f"Added {arcname}")

    print(f"Proto bundle ready: {zip_path}")
    return zip_path


@task()
def create_class_assets(ctx):
    base_dir = Path(ctx.base_folder)
    dist_dir = base_dir / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    # Assets are written to dist/proto/, so clean there — globbing dist/ itself never
    # matched anything and left stale zips behind for the release upload to pick up.
    for existing_file in (dist_dir / "proto").glob(f"{_package_name(ctx)}-generated-*.zip"):
        existing_file.unlink()
        print(f"Removed existing asset: {existing_file}")

    class_assests = [create_proto_bundle(ctx)]

    for language in ALL_PROTO_TARGET_LANGUAGES:
        generate_proto_classes(ctx, target_language=language)

        generated_dir = _generated_root(ctx) / language
        zip_path = dist_dir / "proto" / f"{_package_name(ctx)}-generated-{language}-{_asset_version(language)}.zip"
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for item in generated_dir.rglob("*"):
                if item.is_file():
                    arcname = f"{item.relative_to(generated_dir)}"
                    zipf.write(item, arcname)
                    print(f"Added {arcname}")
        class_assests.append(zip_path)
        # clean up
        if generated_dir.exists():
            import shutil

            shutil.rmtree(generated_dir)
            print(f"Removed temporary generated files in: {generated_dir}")
    if class_assests:
        print("protobuf class assets are ready for GitHub release upload! find them in: {dist_dir}")


@task()
def proto_docs(ctx):
    """Generate documentation for protobuf definitions using protoc-gen-doc."""
    protoc_path, plugin_path = setup_protoc()
    proto_files = ctx.proto_folder / "*.proto"
    target_dir = Path(ctx.base_folder) / "docs"
    target_dir.mkdir(parents=True, exist_ok=True)

    cmd = f"{protoc_path} "
    cmd += f"--plugin=protoc-gen-doc={plugin_path} "
    cmd += " ".join(f"--proto_path={p}" for p in ctx.proto_include_paths)
    cmd += f" --doc_out={target_dir}"
    cmd += f" --doc_opt=markdown,protobuf.md {proto_files}"

    print(f"Generating protobuf docs with command: {cmd}")

    ctx.run(cmd)
