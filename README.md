# Certbot dns-lexicon plugin

Certbot dns-lexicon is a missing plugin for Certbot that allows you to obtain certificate using the dns-lexicon library.
It allows you to use more than a standard number of multiple providers provided by the community to dns-lexicon.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install certbot-dns-lexicon.

```bash
pip install https://github.com/maciejszczurek/certbot-dns-lexicon/releases/download/v1.0.0/certbot_dns_lexicon-1.0.0-py3-none-any.whl
```

## Usage

Using the plugin is the same as for other plugins supplied to certbot. When generating the certificate, add
the `--authenticator dns-lexicon` parameter.

### Named arguments

| Argument                | Description                            |
| ----------------------- | -------------------------------------- |
| `--dns-lexicon-options` | dns-lexicon YAML provider file options |

For more information about configuring the dns-lexicon client, visit
this [page](https://dns-lexicon.readthedocs.io/en/latest/configuration_reference.html#passing-provider-options-to-lexicon).

In the configuration file, define the DNS provider you will use through the `provider_name` parameter.

## Addition information

The library includes an additional plugin to support seohost.pl provider in dns-lexicon.

## Contributing

Pull requests are always welcome.

## License

[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0)
