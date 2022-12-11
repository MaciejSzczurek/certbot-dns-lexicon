import importlib
from typing import Optional, Hashable, Union, Final

import yaml
from certbot import errors
from certbot.plugins import dns_common
from certbot.plugins.dns_common_lexicon import LexiconClient

from lexicon.config import ConfigResolver

_CONFIG_TYPE: Final = dict[Hashable, Union[dict[Hashable, str], int]]


class Authenticator(dns_common.DNSAuthenticator):
    description = "Obtain certificate using a DNS TXT record with dns-lexicon plugin."

    def __init__(self, config, name):
        super().__init__(config, name)
        self.options: Optional[_CONFIG_TYPE] = None

    def _setup_credentials(self):
        with open(self.conf("options"), "r", encoding="utf-8") as file:
            self.options = yaml.load(file, Loader=yaml.Loader)

    def more_info(self) -> str:
        return "This plugin configures ACME universal authorization using dns-lexicon."

    @classmethod
    def add_parser_arguments(cls, add, default_propagation_seconds=60):
        super().add_parser_arguments(
            add, default_propagation_seconds=default_propagation_seconds
        )
        add("options", help="Lexicon options YAML file.")

    def _perform(self, domain, validation_name, validation):
        self._get_client().add_txt_record(domain, validation_name, validation)

    def _cleanup(self, domain, validation_name, validation):
        self._get_client().del_txt_record(domain, validation_name, validation)

    def _get_client(self) -> LexiconClient:
        if not self.options:
            raise errors.Error("Plugin has not been prepared.")

        return _LexiconClient(self.options)


class _LexiconClient(LexiconClient):
    def __init__(self, config: _CONFIG_TYPE):
        super().__init__()

        config["ttl"] = 60

        try:
            module = importlib.import_module(
                f"lexicon.providers.{config['provider_name']}"
            )
        except ModuleNotFoundError:
            module = importlib.import_module(
                f"certbot_dns_lexicon._internal.lexicon.providers.{config['provider_name']}"
            )

        provider_class = getattr(module, "Provider")

        self.provider = provider_class(ConfigResolver().with_env().with_dict(config))

    def _handle_general_error(self, e, domain_name):
        return
