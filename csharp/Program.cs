// Cumulus9 - All rights reserved.

// To run this example:
// dotnet build && dotnet run

using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;

class Program
{
    // please contact support@cumulus9.com to receive the below credentials
    private const string C9ApiEndpoint = "xxxxxxxxxxxxxxxxxx";
    private const string C9ApiSecret = "xxxxxxxxxxxxxxxxxx";

    static async Task Main()
    {
        var portfolioPayload = @"
        {
            ""vendor_symbology"": ""clearing"",
            ""calculation_type"": ""margins"",
            ""execution_mode"": ""sync"",
            ""portfolio"": [
                {
                    ""account_code"": ""Account 001"",
                    ""exchange_code"": ""ASX"",
                    ""contract_code"": ""XT"",
                    ""contract_type"": ""F"",
                    ""contract_expiry"": ""DEC-25"",
                    ""contract_strike"": """",
                    ""net_position"": ""500""
                },
                {
                    ""account_code"": ""Account 001"",
                    ""exchange_code"": ""ICE.EU"",
                    ""contract_code"": ""B"",
                    ""contract_type"": ""Future"",
                    ""contract_expiry"": ""DEC-25"",
                    ""contract_strike"": """",
                    ""net_position"": ""500""
                },
                {
                    ""account_code"": ""Account 001"",
                    ""exchange_code"": ""NYMEX"",
                    ""contract_code"": ""LO"",
                    ""contract_type"": ""CALL"",
                    ""contract_expiry"": ""202512"",
                    ""contract_strike"": ""50.1"",
                    ""net_position"": ""-1000""
                },
                {
                    ""account_code"": ""Account 002"",
                    ""exchange_code"": ""EUREX"",
                    ""contract_code"": ""FDAX"",
                    ""contract_type"": ""FUT"",
                    ""contract_expiry"": ""202612"",
                    ""contract_strike"": """",
                    ""net_position"": ""-50""
                }
            ]
        }";

        var response = await PostPortfolio(portfolioPayload);

        Console.WriteLine(response);
    }

    private static async Task<string> PostPortfolio(string portfolioPayload)
    {
        using (var httpClient = new HttpClient())
        {

            httpClient.DefaultRequestVersion = new Version(2, 0);
            httpClient.DefaultRequestHeaders.UserAgent.ParseAdd("cumulus9-margin-api/1.0");
            httpClient.DefaultRequestHeaders.Accept.ParseAdd("*/*");
            httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {C9ApiSecret}");
            var content = new StringContent(portfolioPayload, Encoding.UTF8, "application/json");
            var response = await httpClient.PostAsync($"{C9ApiEndpoint}/portfolios", content);

            Console.WriteLine(response);
            Console.WriteLine($"{C9ApiEndpoint}/healthcheck");

            if (!response.IsSuccessStatusCode)
            {
                Console.WriteLine($"Error in posting portfolio: {response.StatusCode}");
                return null;
            }

            var responseBody = await response.Content.ReadAsStringAsync();
            return JObject.Parse(responseBody).ToString();
        }
    }
}
