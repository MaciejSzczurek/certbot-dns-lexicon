from unittest import TestCase

from certbot_dns_lexicon.lexicon.providers import seohost
from lexicon.tests.providers.integration_tests import IntegrationTestsV2


class SeohostProviderTest(TestCase, IntegrationTestsV2):
    """TestCase for Seohost"""

    provider_name = "seohost"
    domain = "test-domain.pl"

    def _filter_post_data_parameters(self):
        return ["email", "password", "_token"]

    def _filter_headers(self):
        return ["Cookie"]

    def _filter_response(self, response):
        if "set-cookie" in response["headers"]:
            del response["headers"]["set-cookie"]

        return response

    def setup_method(self, _):
        self.provider_module = seohost

    def test_provider_module_shape(self):
        pass
