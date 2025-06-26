import requests

url = "https://api.together.xyz/v1/chat/completions"
headers = {
    "Authorization": "Bearer 33f748c62ae5e7c2c33ac70e81ba230377131191aa24e30d99965c33ccb8232d",
    "Content-Type": "application/json"
}

data = {
    "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello"}
    ],
    "temperature": 0.2,
    "max_tokens": 50
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.json())
