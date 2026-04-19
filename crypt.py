import json
import ssl
import urllib.parse
import urllib.request
import certifi
def get_crypt_to_usd():
    params = urllib.parse.urlencode(
        {
            "start": "1",
            "limit": "30",
            "convert": "USD",
        }
    )
    request = urllib.request.Request(
        f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?{params}",
        headers={
            "Accept": "application/json",
            "X-CMC_PRO_API_KEY": "dc37e8804ae847fd965f3f473be59451",
        },
    )
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(request, context=context) as response:
        data = json.load(response)

    crypto_list = data.get('data', [])

    info = []
    data = []

    for crypto in crypto_list:
        price = float(f'{crypto['quote']['USD']['price']:.2f}')
        if price != 1.00 and price != 0.00:
            data.append(crypto['name'])
            data.append(f"{crypto['quote']['RUB']['price']:.2f}")
            info.append(data)
        data = []
    return info
print(get_crypt_to_usd())