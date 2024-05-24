import aiohttp
import asyncio
from datetime import datetime, timedelta
import json
import sys

class PrivatBankAPI:
    def __init__(self):
        self.base_url = 'https://api.privatbank.ua/p24api/'

    async def fetch_exchange_rate(self, session, date, currency):
        url = f'{self.base_url}exchange_rates?json&date={date}'
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                for item in data['exchangeRate']:
                    if item['currency'] == currency:
                        return {
                            "date": date,
                            "currency": currency,
                            "saleRate": item.get("saleRate", None),
                            "purchaseRate": item.get("purchaseRate", None)
                        }
            else:
                raise Exception(f"Failed to fetch data for {currency} on {date}: {response.status}")

    async def get_exchange_rates(self, currencies, days):
        today = datetime.now()
        results = {}
        async with aiohttp.ClientSession() as session:
            tasks = []
            for currency in currencies:
                for i in range(days):
                    date = (today - timedelta(days=i)).strftime('%d.%m.%Y')
                    task = self.fetch_exchange_rate(session, date, currency)
                    tasks.append(task)

            responses = await asyncio.gather(*tasks)

            for response in responses:
                if response:
                    date = response['date']
                    currency = response['currency']
                    if date not in results:
                        results[date] = {}
                    results[date][currency] = {
                        'sale': response['saleRate'],
                        'purchase': response['purchaseRate']
                    }
        formatted_results = [{date: data} for date, data in results.items()]
        return formatted_results

async def main():
    currencies = ['USD', 'EUR']
    if len(sys.argv) < 2:
        print("Usage: python script.py DAYS [ADDITIONAL_CURRENCY]")
        return

    if len(sys.argv) > 2:
        additional_currency = sys.argv[2].upper()
        if additional_currency not in currencies:
            currencies.append(additional_currency)

    try:
        days = int(sys.argv[1])
        if days > 10:
            print("DAYS cannot be more than 10. Setting days to 10.")
            days = 10
    except ValueError:
        print("DAYS must be an integer")
        return

    api = PrivatBankAPI()
    try:
        result = await api.get_exchange_rates(currencies, days)
        print(json.dumps(result, indent=4))
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
