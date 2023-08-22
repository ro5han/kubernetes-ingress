import pytest
import requests
from urllib3.exceptions import MaxRetryError

from settings import TEST_DATA
from suite.utils.custom_resources_utils import create_gc_from_yaml, delete_gc
from suite.utils.resources_utils import create_secret_from_yaml, delete_secret, wait_before_test
from suite.utils.vs_vsr_resources_utils import patch_virtual_server_from_yaml, read_vs


@pytest.mark.vs
@pytest.mark.parametrize(
    "crd_ingress_controller, virtual_server_setup",
    [
        (
            {
                "type": "complete",
                "extra_args": [
                    f"-global-configuration=nginx-ingress/nginx-configuration",
                    f"-enable-leader-election=false",
                ],
            },
            {
                "example": "virtual-server-custom-listeners",
                "app_type": "simple",
            },
        )
    ],
    indirect=True,
)
class TestVirtualServerCustomListeners:
    def restore_default_vs(self, kube_apis, virtual_server_setup) -> None:
        """
        Function to revert vs deployment to valid state
        """
        patch_src = f"{TEST_DATA}/virtual-server-status/standard/virtual-server.yaml"
        patch_virtual_server_from_yaml(
            kube_apis.custom_objects,
            virtual_server_setup.vs_name,
            patch_src,
            virtual_server_setup.namespace,
        )
        wait_before_test()

    def test_custom_listeners(self, kube_apis, crd_ingress_controller, virtual_server_setup) -> None:
        print("\nStep 1: Create GC resource")
        secret_name = create_secret_from_yaml(
            kube_apis.v1, virtual_server_setup.namespace, f"{TEST_DATA}/virtual-server-tls/tls-secret.yaml"
        )
        global_config_file = f"{TEST_DATA}/virtual-server-custom-listeners/global-configuration.yaml"
        gc_resource = create_gc_from_yaml(kube_apis.custom_objects, global_config_file, "nginx-ingress")
        vs_custom_listeners = f"{TEST_DATA}/virtual-server-custom-listeners/virtual-server.yaml"
        # Create VS with custom listener (http-8085, https-8445)
        patch_virtual_server_from_yaml(
            kube_apis.custom_objects,
            virtual_server_setup.vs_name,
            vs_custom_listeners,
            virtual_server_setup.namespace,
        )
        wait_before_test()
        print(virtual_server_setup.backend_1_url_custom_ssl)
        resp_custom_https_port = requests.get(
            virtual_server_setup.backend_1_url_custom_ssl,
            headers={"host": virtual_server_setup.vs_host},
            allow_redirects=False,
            verify=False,
        )
        print(virtual_server_setup.backend_1_url_custom)
        resp_custom_http_port = requests.get(
            virtual_server_setup.backend_1_url_custom,
            headers={"host": virtual_server_setup.vs_host},
        )
        print(resp_custom_https_port.status_code)
        print(resp_custom_https_port.text)
        print(resp_custom_http_port.status_code)
        print(resp_custom_http_port.text)

        print(virtual_server_setup.backend_1_url_ssl)
        resp_default_https_port = requests.get(
            virtual_server_setup.backend_1_url_ssl,
            headers={"host": virtual_server_setup.vs_host},
            allow_redirects=False,
            verify=False,
        )
        print(virtual_server_setup.backend_1_url)
        resp_default_http_port = requests.get(
            virtual_server_setup.backend_1_url,
            headers={"host": virtual_server_setup.vs_host},
        )
        print(resp_default_https_port.status_code)
        print(resp_default_https_port.text)
        print(resp_default_http_port.status_code)
        print(resp_default_http_port.text)

        delete_secret(kube_apis.v1, secret_name, virtual_server_setup.namespace)
        delete_gc(kube_apis.custom_objects, gc_resource, "nginx-ingress")
        self.restore_default_vs(kube_apis, virtual_server_setup)

        assert resp_custom_https_port.status_code == 200
        assert resp_custom_http_port.status_code == 200
        assert resp_default_https_port.status_code == 404
        assert resp_default_http_port.status_code == 404

    @pytest.mark.customlisteners
    def test_custom_listeners_vs_warning_on_delete_gc(self, kube_apis, crd_ingress_controller, virtual_server_setup) -> None:
        print("\nStep 1: Create GC resource")
        secret_name = create_secret_from_yaml(
            kube_apis.v1, virtual_server_setup.namespace, f"{TEST_DATA}/virtual-server-tls/tls-secret.yaml"
        )
        global_config_file = f"{TEST_DATA}/virtual-server-custom-listeners/global-configuration.yaml"
        gc_resource = create_gc_from_yaml(kube_apis.custom_objects, global_config_file, "nginx-ingress")
        vs_custom_listeners = f"{TEST_DATA}/virtual-server-custom-listeners/virtual-server.yaml"
        # Create VS with custom listener (http-8085, https-8445)
        patch_virtual_server_from_yaml(
            kube_apis.custom_objects,
            virtual_server_setup.vs_name,
            vs_custom_listeners,
            virtual_server_setup.namespace,
        )
        wait_before_test()
        print(virtual_server_setup.backend_1_url_custom_ssl)
        resp_custom_https_port = requests.get(
            virtual_server_setup.backend_1_url_custom_ssl,
            headers={"host": virtual_server_setup.vs_host},
            allow_redirects=False,
            verify=False,
        )
        print(virtual_server_setup.backend_1_url_custom)
        resp_custom_http_port = requests.get(
            virtual_server_setup.backend_1_url_custom,
            headers={"host": virtual_server_setup.vs_host},
        )
        print(resp_custom_https_port.status_code)
        print(resp_custom_https_port.text)
        print(resp_custom_http_port.status_code)
        print(resp_custom_http_port.text)

        print(virtual_server_setup.backend_1_url_ssl)
        resp_default_https_port = requests.get(
            virtual_server_setup.backend_1_url_ssl,
            headers={"host": virtual_server_setup.vs_host},
            allow_redirects=False,
            verify=False,
        )
        print(virtual_server_setup.backend_1_url)
        resp_default_http_port = requests.get(
            virtual_server_setup.backend_1_url,
            headers={"host": virtual_server_setup.vs_host},
        )
        print(resp_default_https_port.status_code)
        print(resp_default_https_port.text)
        print(resp_default_http_port.status_code)
        print(resp_default_http_port.text)

        delete_gc(kube_apis.custom_objects, gc_resource, "nginx-ingress")

        wait_before_test()
        print(virtual_server_setup.backend_1_url_custom_ssl)
        with pytest.raises(Exception) as e:
            requests.get(
                virtual_server_setup.backend_1_url_custom_ssl,
                headers={"host": virtual_server_setup.vs_host},
                allow_redirects=False,
                verify=False,
            )
        # assert "HTTPSConnectionPool(host='34.147.153.198', port=8445): Max retries exceeded with url: /backend1 (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x10f9f49d0>: Failed to establish a new connection: [Errno 61] Connection refused'))" == str(e.typevalue)


        # print(virtual_server_setup.backend_1_url_custom)
        # try:
        #     resp_custom_http_port_after_delete = requests.get(
        #         virtual_server_setup.backend_1_url_custom,
        #         headers={"host": virtual_server_setup.vs_host},
        #     )
        # except ConnectionRefusedError:
        #     pass
        # else:
        #     assert False, f"Expected: ConnectionRefusedError for url {virtual_server_setup.backend_1_url_custom}"

        response = read_vs(kube_apis.custom_objects, virtual_server_setup.namespace, virtual_server_setup)

        delete_secret(kube_apis.v1, secret_name, virtual_server_setup.namespace)
        self.restore_default_vs(kube_apis, virtual_server_setup)

        assert (
            response["status"]["reason"] == "Warning"
            and response["status"]["message"] == "Listeners defined, but no GlobalConfiguration deployed"
        )
        # assert resp_custom_https_port.status_code == 200
        # assert resp_custom_http_port.status_code == 200
        # assert resp_default_https_port.status_code == 404
        # assert resp_default_http_port.status_code == 404