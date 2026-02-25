# -*- coding: utf-8 -*-
# Cumulus9 - All rights reserved.

import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# please contact support@cumulus9.com to receive the below credentials
c9_api_endpoint = os.getenv("C9_API_ENDPOINT")
c9_api_secret = os.getenv("C9_API_SECRET")

# -----------------------------------------------------------------------------
# REST API function to query the Cumulus9 API
# -----------------------------------------------------------------------------


def get(url):
    try:
        headers = {"Content-Type": "application/json", "Authorization": "Bearer " + c9_api_secret}
        return requests.get(c9_api_endpoint + url, headers=headers)
    except Exception as error:
        raise ValueError("Cumulus9 API - " + str(error)) from error


# -----------------------------------------------------------------------------
# Example of the Cumulus9 API response after calling the healthcheck endpoint
# -----------------------------------------------------------------------------

response = get("/healthcheck/analytics-engine")

print(json.dumps(response.json(), indent=4))

# -----------------------------------------------------------------------------
# Example of the Cumulus9 API response after calling the healthcheck endpoint
# -----------------------------------------------------------------------------

# [
#     {
#         "healthcheck": 1719582349212,
#         "service": "client-api",
#         "start_time": "2024-06-28T12:28:18.506Z",
#         "status": "OK",
#         "version": "0.0.170"
#     },
#     {
#         "healthcheck": 1719582349319,
#         "service": "analytics",
#         "status": "OK",
#         "version": "1.0.0"
#     },
#     {
#         "healthcheck": 1719582349340,
#         "service": "b3core",
#         "status": "OK",
#         "version": "1.0.0"
#     },
#     {
#         "healthcheck": 1719582349340,
#         "service": "eurexpme",
#         "status": "OK",
#         "version": "1.0.0"
#     },
#     {
#         "healthcheck": 1719582349368,
#         "service": "euronextvar",
#         "status": "OK",
#         "version": "1.0.0",
#         "parameters": {
#             "comder": {
#                 "file_date": "20240627",
#                 "marginable_contract": [
#                     {
#                         "symbol_code": "EBM",
#                         "asset_type": "F",
#                         "mat_dt": 20241210,
#                         "option_type": "N",
#                         "strike": 0
#                     },
#                     {
#                         "symbol_code": "EBM",
#                         "asset_type": "F",
#                         "mat_dt": 20261210,
#                         "option_type": "N",
#                         "strike": 0
#                     },
#                    ...
#                 ]
#             },
#             "eqder": {
#                 "file_date": "20240627",
#                 "marginable_contract": [
#                     {
#                         "symbol_code": "AEX",
#                         "asset_type": "S",
#                         "mat_dt": 0,
#                         "option_type": "N",
#                         "strike": 0
#                     },
#                     {
#                         "symbol_code": "BX1",
#                         "asset_type": "S",
#                         "mat_dt": 0,
#                         "option_type": "N",
#                         "strike": 0
#                     },
#                     ...
#                 ]
#             }
#         }
#     },
#     {
#         "healthcheck": 1719582349251,
#         "service": "jpxvar",
#         "parameters": {
#             "COM": "20240627",
#             "IDX": "20240627",
#             "JGB": "20240627",
#             "ODEX": "20240627",
#             "SPE": "20240627",
#             "SSO": "20240627"
#         },
#         "status": "OK",
#         "version": "0.0.19",
#         "start_time": "2024-06-28T05:20:50.087Z"
#     },
#     {
#         "healthcheck": 1719582349273,
#         "service": "nodal",
#         "parameters": "20240627",
#         "status": "OK",
#         "version": "0.0.15",
#         "start_time": "2024-06-28T03:20:38.455Z"
#     },
#     {
#         "healthcheck": 1719582349254,
#         "service": "occtims",
#         "status": "OK",
#         "version": "0.0.5"
#     },
#     {
#         "healthcheck": 1719582349377,
#         "service": "omxoms",
#         "status": "OK",
#         "version": "1.0.0",
#         "parameters": "20240627"
#     },
#     {
#         "healthcheck": 1719582349358,
#         "service": "omxspan",
#         "status": "OK",
#         "version": "1.0.0",
#         "parameters": "20240627"
#     },
#     {
#         "healthcheck": 1719582349312,
#         "service": "poslimits",
#         "parameters": "20240216",
#         "status": "OK",
#         "version": "0.0.3",
#         "start_time": "2024-02-20T07:27:25.208Z"
#     },
#     {
#         "healthcheck": 1719582349327,
#         "service": "posvalidator",
#         "start_time": "2024-06-28T13:41:05.263Z",
#         "status": "OK",
#         "version": "0.0.9",
#         "parameters": {
#             "bdate": "20240628",
#             "last_modified": "2024-06-28 13:30:27"
#         }
#     },
#     {
#         "healthcheck": 1719582349367,
#         "service": "rskaddon",
#         "parameters": {
#             "lme": "risk_23_033"
#         },
#         "status": "OK",
#         "version": "0.0.3",
#         "start_time": "2024-03-10T10:05:41.177Z"
#     },
#     {
#         "healthcheck": 1719582349388,
#         "service": "simm",
#         "start_time": "2024-06-09T13:08:14.687Z",
#         "status": "OK",
#         "version": "0.0.4"
#     },
#     {
#         "healthcheck": 1719582349309,
#         "service": "span",
#         "parameters": {
#             "APX": "20240620",
#             "ASXCLF": "20240620",
#             "BMDC": "20240620",
#             "BTNL": "20240620",
#             "CDC": "20240620",
#             "CFX": "20240620",
#             "DCCC": "20240620",
#             "DIFX": "20240620",
#             "ECC": "20240620",
#             "FEX": "20240620",
#             "HKEX": "20240620",
#             "ICE": "20240620",
#             "KDPW": "20240621",
#             "KELER": "20240620",
#             "LME": "20240620",
#             "MATIF": "20240620",
#             "MGE": "20240620",
#             "MONEP": "20240620",
#             "NSCCL": "20240620",
#             "NZX": "20240620",
#             "OSE": "20231102",
#             "SAU": "20240613",
#             "SDCO": "20240620",
#             "SGX": "20240620",
#             "SML": "20240620",
#             "TFE": "20240620",
#             "TIF": "20240620",
#             "XMAR": "20240620"
#         },
#         "status": "OK",
#         "version": "0.0.13",
#         "start_time": "2024-06-28T04:11:01.377Z"
#     },
#     {
#         "healthcheck": 1719582349307,
#         "service": "span2",
#         "parameters": "20240627_FNO_SPAN2_C",
#         "status": "OK",
#         "version": "1.1.42",
#         "start_time": "2024-06-28T06:36:03.942Z"
#     }
# ]
