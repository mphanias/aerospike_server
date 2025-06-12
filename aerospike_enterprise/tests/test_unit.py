# (C) Datadog, Inc. 2020-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

import copy

import mock
import pytest

from datadog_checks.aerospike_enterprise import AerospikeCheck

from . import common

pytestmark = pytest.mark.unit


def test_connection_uses_tls():
    instance = copy.deepcopy(common.INSTANCE)
    tls_config = {'cafile': 'my-ca-file', 'certfile': 'my-certfile', 'keyfile': 'my-keyfile'}
    instance['tls_config'] = copy.deepcopy(tls_config)

    check = AerospikeCheck('aerospike_enterprise', {}, [instance])
    tls_config['enable'] = True

    assert check._tls_config == tls_config

    with mock.patch('aerospike.client') as client:
        check.get_client()
        client.assert_called_with({'hosts': [check._host], 'tls': tls_config})

