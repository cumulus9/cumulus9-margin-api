# Cumulus9 - All rights reserved.
# Basic synchronous margin calculation for an ETD portfolio.

library(httr)
library(jsonlite)

# Credentials -- contact support@cumulus9.com to obtain these.
c9_api_endpoint <- "xxxxxxxxxxxxxxxxxx"
c9_api_secret <- "sk-xxxxxxxxxxxxxxxxxx"

# ---------------------------------------------------------------------------
# Portfolio payload
# ---------------------------------------------------------------------------

payload <- list(
  vendor_symbology = "clearing",
  calculation_type = "margins",
  portfolio = list(
    list(
      account_code = "Account 001",
      exchange_code = "ASX",
      contract_code = "XT",
      contract_type = "F",
      contract_expiry = "DEC-25",
      contract_strike = "",
      net_position = "500",
      account_type = "H"
    ),
    list(
      account_code = "Account 001",
      exchange_code = "ICE.EU",
      contract_code = "B",
      contract_type = "Future",
      contract_expiry = "DEC-25",
      contract_strike = "",
      net_position = "500",
      account_type = "H"
    ),
    list(
      account_code = "Account 001",
      exchange_code = "NYMEX",
      contract_code = "LO",
      contract_type = "CALL",
      contract_expiry = "202512",
      contract_strike = "50.1",
      net_position = "-1000",
      account_type = "H"
    ),
    list(
      account_code = "Account 002",
      exchange_code = "EUREX",
      contract_code = "FDAX",
      contract_type = "FUT",
      contract_expiry = "202612",
      contract_strike = "",
      net_position = "-50",
      account_type = "H"
    )
  )
)

# ---------------------------------------------------------------------------
# Submit and print results
# ---------------------------------------------------------------------------

response <- POST(
  paste0(c9_api_endpoint, "/portfolios"),
  body = toJSON(payload, auto_unbox = TRUE),
  encode = "json",
  add_headers(
    `Content-Type` = "application/json",
    Authorization = paste("Bearer", c9_api_secret)
  )
)

stop_for_status(response)

results <- content(response, as = "parsed")
cat(toJSON(results, pretty = TRUE, auto_unbox = TRUE))
