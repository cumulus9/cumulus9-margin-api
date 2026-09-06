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
    private static readonly string C9ApiEndpoint =
        Environment.GetEnvironmentVariable("C9_API_ENDPOINT") ?? "xxxxxxxxxxxxxxxxxx";
    private static readonly string C9ApiSecret =
        Environment.GetEnvironmentVariable("C9_API_SECRET") ?? "sk-xxxxxxxxxxxxxxxxxx";

    static async Task Main()
    {
        var payload = @"{
            ""vendor_symbology"": ""clearing"",
            ""calculation_type"": ""margins"",
            ""in_memory"": true,
            ""portfolio"": [
                {
                    ""account_code"": ""Account 001"",
                    ""exchange_code"": ""ASX"",
                    ""contract_code"": ""AP"",
                    ""contract_type"": ""FUT"",
                    ""contract_expiry"": ""DEC-27"",
                    ""contract_strike"": """",
                    ""net_position"": ""500"",
                    ""account_type"": ""H""
                },
                {
                    ""account_code"": ""Account 001"",
                    ""exchange_code"": ""ICE.EU"",
                    ""contract_code"": ""B"",
                    ""contract_type"": ""FUT"",
                    ""contract_expiry"": ""DEC-27"",
                    ""contract_strike"": """",
                    ""net_position"": ""500"",
                    ""account_type"": ""H""
                },
                {
                    ""account_code"": ""Account 001"",
                    ""exchange_code"": ""NYMEX"",
                    ""contract_code"": ""LO"",
                    ""contract_type"": ""CALL"",
                    ""contract_expiry"": ""DEC-27"",
                    ""contract_strike"": ""50"",
                    ""net_position"": ""-1000"",
                    ""account_type"": ""H""
                },
                {
                    ""account_code"": ""Account 002"",
                    ""exchange_code"": ""EUREX"",
                    ""contract_code"": ""FDAX"",
                    ""contract_type"": ""FUT"",
                    ""contract_expiry"": ""17-DEC-27"",
                    ""contract_strike"": """",
                    ""net_position"": ""-50"",
                    ""account_type"": ""H""
                }
            ]
        }";

        using var client = new HttpClient();
        client.DefaultRequestHeaders.UserAgent.ParseAdd("cumulus9-csharp-example/1.0");
        client.DefaultRequestHeaders.Add("Authorization", $"Bearer {C9ApiSecret}");

        var content = new StringContent(payload, Encoding.UTF8, "application/json");
        var response = await client.PostAsync($"{C9ApiEndpoint}/portfolios", content);
        var body = await response.Content.ReadAsStringAsync();

        if (!response.IsSuccessStatusCode)
        {
            Console.Error.WriteLine($"Error: {response.StatusCode} {body}");
            return;
        }

        var doc = JsonDocument.Parse(body);
        var formatted = JsonSerializer.Serialize(doc, new JsonSerializerOptions { WriteIndented = true });

        Console.WriteLine(formatted);
    }
}
