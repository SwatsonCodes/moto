from os import environ

import boto3
import pytest

from moto import mock_efs


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    environ["AWS_ACCESS_KEY_ID"] = "testing"
    environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    environ["AWS_SECURITY_TOKEN"] = "testing"
    environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(scope="function")
def efs(aws_credentials):  # pylint: disable=unused-argument
    with mock_efs():
        yield boto3.client("efs", region_name="us-east-1")


@pytest.fixture(scope="function")
def file_system(efs):
    create_fs_resp = efs.create_file_system(CreationToken="foobarbaz")
    create_fs_resp.pop("ResponseMetadata")
    yield create_fs_resp


def test_list_tags_for_resource__without_tags(efs, file_system):
    file_system_id = file_system["FileSystemId"]

    ap_id = efs.create_access_point(ClientToken="ct", FileSystemId=file_system_id)[
        "AccessPointId"
    ]

    resp = efs.list_tags_for_resource(ResourceId=ap_id)
    resp.should.have.key("Tags").equals([])


def test_list_tags_for_resource__with_tags(efs, file_system):
    file_system_id = file_system["FileSystemId"]

    ap_id = efs.create_access_point(
        ClientToken="ct",
        Tags=[{"Key": "key", "Value": "value"}, {"Key": "Name", "Value": "myname"}],
        FileSystemId=file_system_id,
    )["AccessPointId"]

    resp = efs.list_tags_for_resource(ResourceId=ap_id)
    resp.should.have.key("Tags").equals(
        [{"Key": "key", "Value": "value"}, {"Key": "Name", "Value": "myname"}]
    )


def test_tag_resource(efs, file_system):
    file_system_id = file_system["FileSystemId"]

    ap_id = efs.create_access_point(ClientToken="ct", FileSystemId=file_system_id)[
        "AccessPointId"
    ]

    efs.tag_resource(
        ResourceId=ap_id,
        Tags=[{"Key": "key", "Value": "value"}, {"Key": "Name", "Value": "myname"}],
    )

    resp = efs.list_tags_for_resource(ResourceId=ap_id)
    resp.should.have.key("Tags").equals(
        [{"Key": "key", "Value": "value"}, {"Key": "Name", "Value": "myname"}]
    )


def test_untag_resource(efs, file_system):
    file_system_id = file_system["FileSystemId"]

    ap_id = efs.create_access_point(
        ClientToken="ct",
        Tags=[{"Key": "key1", "Value": "val1"}],
        FileSystemId=file_system_id,
    )["AccessPointId"]

    efs.tag_resource(
        ResourceId=ap_id,
        Tags=[{"Key": "key2", "Value": "val2"}, {"Key": "key3", "Value": "val3"}],
    )

    efs.untag_resource(ResourceId=ap_id, TagKeys=["key2"])

    resp = efs.list_tags_for_resource(ResourceId=ap_id)
    resp.should.have.key("Tags").equals(
        [{"Key": "key1", "Value": "val1"}, {"Key": "key3", "Value": "val3"}]
    )
