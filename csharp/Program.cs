// Cumulus9 - All rights reserved.
// Basic synchronous margin calculation for an ETD portfolio.
// Run: dotnet build && dotnet run

using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

class Program
{
    // Credentials -- contact support@cumulus9.com to obtain these.
    private const string C9ApiEndpoint = "xxxxxxxxxxxxxxxxxx";
    private const string C9ApiSecret = "sk-xxxxxxxxxxxxxxxxxx";

    static async Task Main()
    {
        var payload = @"{
            ""vendor_symbology"": ""clearing"",
            ""calculation_type"": ""margins"",
            ""portfolio"": [
                {
                    ""account_code"": ""Account 001"",
                    ""exchange_code"": ""ASX"",
                    ""contract_code"": ""XT"",
                    ""contract_type"": ""F"",
                    ""contract_expiry"": ""DEC-25"",
                    ""contract_strike"": """",
                    ""net_position"": ""500"",
                    ""account_type"": ""H""
                },
                {
                    ""account_code"": ""Account 001"",
                    ""exchange_code"": ""ICE.EU"",
                    ""contract_code"": ""B"",
                    ""contract_type"": ""Future"",
                    ""contract_expiry"": ""DEC-25"",
                    ""contract_strike"": """",
                    ""net_position"": ""500"",
                    ""account_type"": ""H""
                },
                {
                    ""account_code"": ""Account 001"",
                    ""exchange_code"": ""NYMEX"",
                    ""contract_code"": ""LO"",
                    ""contract_type"": ""CALL"",
                    ""contract_expiry"": ""202512"",
                    ""contract_strike"": ""50.1"",
                    ""net_position"": ""-1000"",
                    ""account_type"": ""H""
                },
                {
                    ""account_code"": ""Account 002"",
                    ""exchange_code"": ""EUREX"",
                    ""contract_code"": ""FDAX"",
                    ""contract_type"": ""FUT"",
                    ""contract_expiry"": ""202612"",
                    ""contract_strike"": """",
                    ""net_position"": ""-50"",
                    ""account_type"": ""H""
                }
            ]
        }";

        using var client = new HttpClient();
        client.DefaultRequestHeaders.Add("Authorization", $"Bearer {C9ApiSecret}");

        var content = new StringContent(payload, Encoding.UTF8, "application/json");
        var response = await client.PostAsync($"{C9ApiEndpoint}/portfolios", content);

        if (!response.IsSuccessStatusCode)
        {
            Console.Error.WriteLine($"Error: {response.StatusCode}");
            return;
        }

        var body = await response.Content.ReadAsStringAsync();
        var doc = JsonDocument.Parse(body);
        var formatted = JsonSerializer.Serialize(doc, new JsonSerializerOptions { WriteIndented = true });

        Console.WriteLine(formatted);
    }
}
