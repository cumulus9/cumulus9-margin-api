# -*- coding: utf-8 -*-
# Cumulus9 - All rights reserved.

import os
import requests
import base64


def getAccessToken():
    basic_authorization_bytes = (
        os.environ.get("C9_API_CLIENT_ID")
        + ":"
        + os.environ.get("C9_API_CLIENT_SECRET")
    ).encode("ascii")
    basic_authorization_base64 = base64.b64encode(basic_authorization_bytes)
    headers = {
        "Authorization": "Basic " + basic_authorization_base64.decode("utf-8"),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = "grant_type=client_credentials&scope=riskcalc%2Fget"
    return requests.post(
        os.environ.get("C9_API_AUTH_ENDPOINT"), headers=headers, data=data
    )


def postPorfolio(portfolioJson):
    try:
        auth = getAccessToken()
        if auth.status_code == 200:
            access_token = auth.json()["access_token"]
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + access_token,
            }
            return requests.post(
                os.environ.get("C9_API_ENDPOINT") + "/portfolios",
                headers=headers,
                json=portfolioJson,
            )
        else:
            raise ValueError("HTTP", auth.status_code, "-", auth.reason)
    except Exception as error:
        raise ValueError("Cumulus9 API - " + str(error))
