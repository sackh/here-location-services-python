# Copyright (C) 2019-2020 HERE Europe B.V.
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
# SPDX-License-Identifier: Apache-2.0
# License-Filename: LICENSE

"""This module contains classes for accessing `HERE Routing API <https://developer.here.com/documentation/routing-api/8.17.0/dev_guide/index.html>_`. # noqa E501
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests

from .apis import Api
from .exceptions import ApiError


class RoutingApi(Api):
    """A class for accessing HERE routing APIs."""

    def __init__(
        self, api_key: Optional[str] = None, proxies: Optional[dict] = None, country: str = "row"
    ):
        super(RoutingApi, self).__init__(api_key, proxies, country)
        self._base_url = f"https://router.{self._get_url_string()}"

    def route(
        self,
        transport_mode: str,
        origin: List,
        destination: List,
        via: Optional[List[Tuple]] = None,
        departure_time: Optional[datetime] = None,
        routing_mode: str = "fast",
        alternatives: int = 0,
        units: str = "metric",
        lang: str = "en-US",
        return_results: Optional[List] = None,
        spans: Optional[List] = None,
    ):
        """Calculate ``car`` route between two endpoints.

        :param transport_mode: A string to represent mode of transport.
        :param origin: A list of ``latitude`` and ``longitude`` of origin point of route.
        :param destination: A list of ``latitude`` and ``longitude`` of destination point of route.
        :param via: A list of tuples of ``latitude`` and ``longitude`` of via points.
        :param departure_time: :class:`datetime.datetime` object.
        :param routing_mode: A string to represent routing mode.
        :param alternatives: Number of alternative routes to return aside from the optimal route.
            default value is ``0`` and maximum is ``6``.
        :param units: A string representing units of measurement used in guidance instructions.
            The default is metric.
        :param lang: A string representing preferred language of the response.
            The value should comply with the IETF BCP 47.
        :param return_results: A list of strings.
        :param spans: A list of strings to define which attributes are included in the response
            spans.
        :return: :class:`requests.Response` object.
        :raises ApiError: If ``status_code`` of API response is not 200.
        """
        path = "v8/routes"
        url = f"{self._base_url}/{path}"
        params: Dict[str, str] = {
            "origin": ",".join([str(i) for i in origin]),
            "destination": ",".join([str(i) for i in destination]),
            "transportMode": transport_mode,
        }
        if via:
            lat, lng = via[0]
            url += f"?via={lat},{lng}"
            for lat, lng in via[1:]:
                url += f"&via{lat},{lng}"
        if departure_time:
            params["departureTime"] = departure_time.isoformat(timespec="seconds")
        params["routingMode"] = routing_mode
        params["alternatives"] = str(alternatives)
        params["units"] = units
        params["lang"] = lang
        if return_results:
            params["return"] = ",".join(return_results)
        if spans:
            params["spans"] = ",".join(spans)

        if self.credential_params:
            params.update(self.credential_params)

        resp = requests.get(url, params=params, proxies=self.proxies)
        if resp.status_code == 200:
            return resp
        else:
            raise ApiError(resp)