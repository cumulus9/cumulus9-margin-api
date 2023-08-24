# -*- coding: utf-8 -*-
# Cumulus9 - All rights reserved.

import requests
import base64


def get_access_token(api_credentials):
    basic_authorization_bytes = (api_credentials["client_id"] + ":" + api_credentials["client_secret"]).encode("ascii")
    basic_authorization_base64 = base64.b64encode(basic_authorization_bytes)
    headers = {
        "Authorization": "Basic " + basic_authorization_base64.decode("utf-8"),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = "grant_type=client_credentials&scope=riskcalc%2Fget"
    return requests.post(api_credentials["auth_endpoint"], headers=headers, data=data)


def post(url, data, api_credentials):
    try:
        auth = get_access_token(api_credentials)
        if auth.status_code == 200:
            access_token = auth.json()["access_token"]
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + access_token,
            }
            return requests.post(
                api_credentials["endpoint"] + url,
                headers=headers,
                json=data,
            )
        else:
            raise ValueError("HTTP", auth.status_code, "-", auth.reason)
    except Exception as error:
        raise ValueError("Cumulus9 API - " + str(error))
