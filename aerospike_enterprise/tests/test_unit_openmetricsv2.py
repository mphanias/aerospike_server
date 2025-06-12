# (C) Datadog, Inc. 2022-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

import os

import pytest

from datadog_checks.aerospike_enterprise import AerospikeCheck, AerospikeEnterpriseCheckV2
from datadog_checks.dev.utils import get_metadata_metrics

from .common import (
    EXPECTED_PROMETHEUS_METRICS_7,
    HERE,
)

pytestmark = [pytest.mark.unit]


def get_fixture_path(filename):
    return os.path.join(HERE, 'fixtures', filename)


def test_openmetricsv2_check(aggregator, dd_run_check, instance_openmetrics_v2, mock_http_response):

    check = AerospikeEnterpriseCheckV2('aerospike_enterprise', {}, [instance_openmetrics_v2])
    dd_run_check(check)

    metrics_to_check = EXPECTED_PROMETHEUS_METRICS_7
    # print("\n\n\t **** aggregator.metric_names \n\n\t", aggregator.metric_names,"\n\n\t")
    _test_check_from_v7(aggregator, dd_run_check, instance_openmetrics_v2, mock_http_response, EXPECTED_PROMETHEUS_METRICS_7)



def _test_check_from_v7(aggregator, dd_run_check, instance_openmetrics_v2, mock_http_response, metrics_to_check):
    """
    run checks if aerospike server version is 7 or above, validates, mock prom metrics, labels and metadata.csv
    """

    mock_http_response(file_path=get_fixture_path('prometheus.txt'))
    
    # print("\n\n\t **** _test_check_from_v7 \n\n\t","\n\n\t")

    # print("\n\n\t **** metrics_to_check \n\n\t", metrics_to_check,"\n\n\t")

    for metric_name in metrics_to_check:
        aggregator.assert_metric(metric_name)
        # print("\n\n\t **** metric_name \n\n\t", metric_name,"\n\n\t")

        # no need to validate node-ticks for labels, as its a counter to check how many times exporter url is called
        #    node-ticks wiill not have any labels associated
        if metric_name not in ("aerospike.node.ticks", "aerospike.node.up"):
            aggregator.assert_metric_has_tag(
                metric_name, 'endpoint:{}'.format(instance_openmetrics_v2.get('openmetrics_endpoint'))
            )            

            aggregator.assert_metric_has_tag_prefix(metric_name, 'aerospike_cluster')
            aggregator.assert_metric_has_tag_prefix(metric_name, 'aerospike_service')

            # latency metric should have le tag representing bucket
            # 1,2,4,8,16,32..., 65k
            if "aerospike.latencies" in metric_name and "_bucket" in metric_name:
                aggregator.assert_metric_has_tag_prefix(metric_name, 'le')

    aggregator.assert_all_metrics_covered()
    aggregator.assert_metrics_using_metadata(get_metadata_metrics(), check_submission_type=True)
