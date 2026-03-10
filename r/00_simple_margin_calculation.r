# -*- coding: utf-8 -*-
# Cumulus9 - All rights reserved.

# install the required packages if you haven't already:
# install.packages("httr")
# install.packages("jsonlite")
# install.packages('base64enc')

library(httr)
library(jsonlite)
library(base64enc)

# API credentials (contact support@cumulus9.com to receive the below credentials)
c9_api_endpoint <- "xxxxxxxxxxxxxxxxxx"
c9_api_auth_endpoint <- "xxxxxxxxxxxxxxxxxx"

# -----------------------------------------------------------------------------
# REST API functions to retrieve the Cumulus9 access token and post portfolio
# -----------------------------------------------------------------------------

post_portfolio <- function(url, data, api_credentials) {
  tryCatch({
    
    if (status_code(auth) == 200) {
      headers <- add_headers(
        `Content-Type` = "application/json",
        Authorization = paste("Bearer", c9_api_secret)
      )
      
      response <- POST(
        paste0(api_credentials$endpoint, url),
        body = toJSON(data, auto_unbox = TRUE),
        encode = "json",
        headers
      )
      
      return(response)
    } else {
      stop("HTTP ", status_code(auth), " - ", http_status(auth)$message)
    }
  }, error = function(e) {
    stop("Cumulus9 API - ", e$message)
  })
}

# -----------------------------------------------------------------------------
# Create the portfolio payload and post it to Cumulus9 API
# -----------------------------------------------------------------------------

portfolio_payload <- list(
  vendor_symbology = "clearing",
  calculation_type = "margins",
  execution_mode = "sync",
  portfolio = list(
    list(
      account_code = "Account 001",
      exchange_code = "ASX",
      contract_code = "XT",
      contract_type = "F",
      contract_expiry = "DEC-25",
      contract_strike = "",
      net_position = "500"
    ),
    list(
      account_code = "Account 001",
      exchange_code = "ICE.EU",
      contract_code = "B",
      contract_type = "Future",
      contract_expiry = "DEC-25",
      contract_strike = "",
      net_position = "500"
    ),
    list(
      account_code = "Account 001",
      exchange_code = "NYMEX",
      contract_code = "LO",
      contract_type = "CALL",
      contract_expiry = "202512",
      contract_strike = "50.1",
      net_position = "-1000"
    ),
    list(
      account_code = "Account 002",
      exchange_code = "EUREX",
      contract_code = "FDAX",
      contract_type = "FUT",
      contract_expiry = "202612",
      contract_strike = "",
      net_position = "-50"
    )
  )
)

# create credentials list
api_credentials <- list(
  endpoint = c9_api_endpoint,
  auth_endpoint = c9_api_auth_endpoint,
)

# post portfolio and receive the margin results in json format
results <- post_portfolio("/portfolios", portfolio_payload, api_credentials)
results_json <- content(results, as = "parsed")

# print results in JSON format
cat(toJSON(results_json, pretty = TRUE))