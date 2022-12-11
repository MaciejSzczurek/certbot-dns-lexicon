from typing import Optional, List, Dict, Union, Final

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet
from requests import Session, Response

from lexicon.config import ConfigResolver
from lexicon.exceptions import AuthenticationError
from lexicon.providers.base import Provider as BaseProvider


class Provider(BaseProvider):
    DEFAULT_TTL: Final = "86400"
    HTML_PARSER: Final = "html.parser"
    TOKEN_SELECTOR: Final = "input[name='_token']"
    HOST: Final = "https://panel.seohost.pl"

    def __init__(self, config: Union[ConfigResolver, Dict]):
        super().__init__(config)

        if not self._get_provider_option("auth_email"):
            raise Exception("Error, login is not provided")
        if not self._get_provider_option("auth_password"):
            raise Exception("Error, password is not provided")

        self.auth_email = self._get_provider_option("auth_email")
        self.auth_password = self._get_provider_option("auth_password")
        self.session: Optional[Session] = None
        self.zone_url: Optional[str] = None

    def _authenticate(self) -> None:
        self.session = requests.Session()

        soup = BeautifulSoup(self._get("/login").content, self.HTML_PARSER)
        self._post(
            "/login",
            {
                "_token": soup.select_one(self.TOKEN_SELECTOR)["value"],
                "email": self.auth_email,
                "password": self.auth_password,
            },
        )

        zones = BeautifulSoup(self._get("/dns").content, self.HTML_PARSER).select(
            "#dns-table tr > td > a:nth-child(1)"
        )
        if self.domain not in {domain.text for domain in zones}:
            raise AuthenticationError(f"Domain {self.domain} is not found")

        self.zone_url = [
            domain["href"] for domain in zones if domain.text == self.domain
        ][0].replace(self.HOST, "")

        self.domain_id = self.domain

    def _create_record(self, rtype: str, name: str, content: str) -> bool:
        ttl = self._get_lexicon_option("ttl")
        soup = BeautifulSoup(self._get(self.zone_url).content, self.HTML_PARSER)
        form = soup.select_one(
            "div.card-box:nth-child(3) > div:nth-child(2) > form:nth-child(1)"
        )

        for record in self._list_records(rtype, name, content):
            if (
                    record["type"] == rtype
                    and self._relative_name(record["name"]) == self._relative_name(name)
                    and record["content"] == content
            ):
                return True

        self._post(
            form.attrs["action"],
            {
                "_token": form.select_one(self.TOKEN_SELECTOR)["value"],
                "dns_id": form.select_one("input[name='dns_id']")["value"],
                "domain": form.select_one("input[name='domain']")["value"],
                "user_id": form.select_one("input[name='user_id']")["value"],
                "record_type": rtype,
                "record_name": self._full_name(name),
                "record_prio": "0",
                "record_value": content,
                "record_ttl": ttl if ttl else self.DEFAULT_TTL,
            },
        )

        return True

    def _update_record(
        self,
        identifier: Optional[str] = None,
        rtype: Optional[str] = None,
        name: Optional[str] = None,
        content: Optional[str] = None,
    ) -> bool:
        ttl = self._get_lexicon_option("ttl")
        soup = BeautifulSoup(self._get(self.zone_url).content, self.HTML_PARSER)
        form = soup.select_one(
            "div.card-box:nth-child(3) > div:nth-child(2) > form:nth-child(1)"
        )

        if not identifier:
            records = self._list_records(rtype, name)
        else:
            records = [
                record
                for record in self._list_records()
                if "id" in record and record["id"] == identifier
            ]

        if len(records) == 1 and "id" in records[0]:
            original_record = records[0]
        elif len(records) > 1:
            raise Exception("Several record identifiers match the request")
        else:
            raise Exception("Record identifier could not be found")

        self._patch(
            f"/dns/records/{original_record['id']}",
            {
                "_token": form.select_one(self.TOKEN_SELECTOR)["value"],
                "record_type": rtype if rtype else original_record["type"],
                "record_name": self._full_name(
                    name if name else original_record["name"]
                ),
                "record_prio": "0",
                "record_value": content if content else original_record["content"],
                "record_ttl": ttl if ttl else self.DEFAULT_TTL,
            },
        )

        return True

    def _delete_record(
        self,
        identifier: Optional[str] = None,
        rtype: Optional[str] = None,
        name: Optional[str] = None,
        content: Optional[str] = None,
    ) -> bool:
        delete_records_id = []
        if not identifier:
            delete_records_id = [
                record["id"]
                for record in self._list_records(rtype, name, content)
                if "id" in record
            ]
        else:
            delete_records_id.append(identifier)

        token = BeautifulSoup(
            self._get(self.zone_url).content, self.HTML_PARSER
        ).select_one(self.TOKEN_SELECTOR)["value"]

        for record_id in delete_records_id:
            self._request("DELETE", f"/dns/records/{record_id}", {"_token": token})

        return True

    def _list_records(
        self,
        rtype: Optional[str] = None,
        name: Optional[str] = None,
        content: Optional[str] = None,
    ) -> List[Dict]:
        records_table: list[ResultSet[Tag]] = [
            record.select("td")
            for record in BeautifulSoup(
                self._get(self.zone_url).content, self.HTML_PARSER
            ).select(".table tr")
        ][1:]
        records: list[dict] = []
        for record in records_table:
            converted_record = {
                "type": record[0].text.strip(),
                "name": self._full_name(record[1].text.strip()),
                "content": record[2].text.strip(),
                "ttl": record[3].text.strip(),
            }

            form = record[4].select_one("form")
            if form:
                action = form.attrs["action"]
                converted_record["id"] = action[action.rindex("/") + 1 :]

            records.append(converted_record)

        if rtype:
            records = [record for record in records if record["type"] == rtype]
        if name:
            full_name = self._full_name(name)
            records = [record for record in records if record["name"] == full_name]
        if content:
            lower_content = content.lower()
            records = [
                record
                for record in records
                if record["content"].lower() == lower_content
            ]

        return records

    def _request(
        self,
        action: str = "GET",
        url: str = "/",
        data: Optional[Dict] = None,
        query_params: Optional[Dict] = None,
    ) -> Response:
        return self.session.request(
            action,
            url if url.startswith(self.HOST) else f"{self.HOST}{url}",
            data=data,
            params=query_params,
        )
