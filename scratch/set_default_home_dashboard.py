import requests

auth = ("fran.jose.estella@gmail.com", "admin123")
headers = {
    "Content-Type": "application/json"
}
payload = {
    "homeDashboardUID": "mes-home-v1"
}

# 1. Update org preferences
try:
    response = requests.put("http://localhost:3010/api/org/preferences", json=payload, auth=auth, headers=headers)
    print("Org Preferences Status Code:", response.status_code)
    print("Org Preferences Response Body:", response.text)
except Exception as e:
    print("Org Preferences Error:", e)

# 2. Update current user preferences
try:
    response = requests.put("http://localhost:3010/api/user/preferences", json=payload, auth=auth, headers=headers)
    print("User Preferences Status Code:", response.status_code)
    print("User Preferences Response Body:", response.text)
except Exception as e:
    print("User Preferences Error:", e)
