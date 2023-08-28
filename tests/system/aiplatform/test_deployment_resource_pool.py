# -*- coding: utf-8 -*-

# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import pytest

from google.cloud import aiplatform
from google.cloud.aiplatform.preview import models

from tests.system.aiplatform import e2e_base

# permanent_custom_mnist_model
_MODEL_ID = "6430031960164270080"


@pytest.mark.usefixtures("tear_down_resources")
class TestDeploymentResourcePool(e2e_base.TestEndToEnd):
    """End-to-end tests for DeploymentResourcePool."""

    _temp_prefix = "temp_vertex_sdk_e2e"

    def test_create_deploy_delete_with_deployment_resource_pool(self, shared_state):
        # Collection of resources generated by this test, to be deleted during teardown
        shared_state["resources"] = []

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )
        drp = models.DeploymentResourcePool.create(
            deployment_resource_pool_id="drp_test"
        )
        shared_state["resources"].append(drp)

        endpoint = aiplatform.Endpoint.create(
            display_name=self._make_display_name("drp_endpoint_test")
        ).preview
        shared_state["resources"].append(endpoint)

        # Retrieve permanent model, deploy to Endpoint, then undeploy
        model = aiplatform.Model(model_name=_MODEL_ID).preview
        endpoint.deploy(model=model, deployment_resource_pool=drp)

        assert endpoint._gca_resource.deployed_models
        assert drp.query_deployed_models()

        deployed_model_id = endpoint.list_models()[0].id
        endpoint.undeploy(deployed_model_id=deployed_model_id)
        assert not endpoint._gca_resource.deployed_models
        assert not drp.query_deployed_models()