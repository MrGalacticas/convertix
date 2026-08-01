import aiohttp


class Exchange:
    def __init__(self):
        self.rates = {}

    async def update_rates(self):
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
               data = await response.json()

        self.rates["UAH"] = 1.0

        for currency in data:
            code = currency["cc"]
            rate = currency["rate"]

            self.rates[code] = rate

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        from_rate = self.rates[from_currency]
        to_rate = self.rates[to_currency]

        amount_in_uah = amount * from_rate
        result = amount_in_uah / to_rate

        return round(result, 2)
                    