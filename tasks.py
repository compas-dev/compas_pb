from pathlib import Path

from compas_invocations2 import build
from compas_invocations2 import style
from compas_invocations2 import tests
from invoke.collection import Collection
from invoke.tasks import task

from compas_pb.invocations import create_class_assets
from compas_pb.invocations import create_proto_bundle
from compas_pb.invocations import generate_proto_classes
from compas_pb.invocations import proto_docs


@task
def pre_build(ctx):
    """Create generated protobuf archives before building a release."""
    create_class_assets(ctx)


ns = Collection(
    style.check,
    style.lint,
    style.format,
    tests.test,
    tests.testdocs,
    tests.testcodeblocks,
    build.clean,
    pre_build,
    generate_proto_classes,
    create_class_assets,
    create_proto_bundle,
    proto_docs,
)

ns.configure(
    {
        "base_folder": Path(__file__).parent,
        "proto_folder": Path("./src") / "compas_pb" / "protobuf_defs" / "compas_pb" / "generated",
        "proto_include_paths": [Path("./src") / "compas_pb" / "protobuf_defs"],
        "proto_out_folder": Path("./src"),
    }
)
