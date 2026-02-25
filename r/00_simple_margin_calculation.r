# -*- coding: utf-8 -*-
# Cumulus9 - All rights reserved.

# install the required packages if you haven't already:
# install.packages("httr")
# install.packages("jsonlite")

library(httr)
library(jsonlite)

# API credentials (please contact support@cumulus9.com to receive the below credentials)
c9_api_endpoint <- "xxxxxxxxxxxxxxxxxx"
c9_api_secret <- "xxxxxxxxxxxxxxxxxx"

# -----------------------------------------------------------------------------
# REST API function to post portfolio
# -----------------------------------------------------------------------------

post_portfolio <- function(url, data) {
  tryCatch({
    headers <- add_headers(
      `Content-Type` = "application/json",
      Authorization = paste("Bearer", c9_api_secret)
    )
    
    response <- POST(
      paste0(c9_api_endpoint, url),
      body = toJSON(data, auto_unbox = TRUE),
      encode = "json",
      headers
    )
    
    return(response)
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

# post portfolio and receive the margin results in json format
results <- post_portfolio("/portfolios", portfolio_payload)
results_json <- content(results, as = "parsed")

# print results in JSON format
cat(toJSON(results_json, pretty = TRUE))
