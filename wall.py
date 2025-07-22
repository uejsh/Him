import requests
API_KEY = "cqt_rQVQQDWDMVPXjkQTMT9XTWdMdpq4"
WALLET_ADDRESS = "0xbc0663ef63add180609944c58ba7d4851890ca45"
HEADERS = {"x-api-key": API_KEY}

# Get all transactions
tx_url = "https://api.goldrushapi.com/v1/allchains/transactions/address/{wallet_address}"
transactions = requests.get(tx_url, headers=HEADERS)


print(transactions)
