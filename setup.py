import argparse
import requests
import json
from json import decoder


def getUserId(username, sessionId):
    headers = {"User-Agent": "iphone_ua", "x-ig-app-id": "936619743392459"}
    api = requests.get(
        f'https://i.instagram.com/api/v1/users/web_profile_info/?username={username}',
        headers=headers,
        cookies={'sessionid': sessionId}
    )
    try:
        if api.status_code == 404:
            return {"id": None, "error": "User not found"}

        user_id = api.json()["data"]['user']['id']
        return {"id": user_id, "error": None}

    except decoder.JSONDecodeError:
        return {"id": None, "error": "Rate limit"}


def getInfo(username, sessionId):
    data = getUserId(username, sessionId)
    if data["error"]:
        return data

    userId = data["id"]
    try:
        response = requests.get(
            f'https://i.instagram.com/api/v1/users/{userId}/info/',
            headers={'User-Agent': 'Instagram 64.0.0.14.96'},
            cookies={'sessionid': sessionId}
        )
        if response.status_code == 429:
            return {"user": None, "error": "Rate limit"}

        response.raise_for_status()
        info_user = response.json()

        # Imprime la respuesta completa de la API
        print("\n📢 API Response:\n", json.dumps(info_user, indent=4))

        user_data = info_user.get("user", {})

        return {
            "username": user_data.get("username", "Unknown"),
            "email": user_data.get("public_email", "No email found"),
            "phone": f'+{user_data.get("public_phone_country_code", "")} {user_data.get("public_phone_number", "No phone found")}'
        }

    except requests.exceptions.RequestException:
        return {"user": None, "error": "Not found"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sessionid', help="Instagram session ID", required=True)
    parser.add_argument('-u', '--username', help="Username", required=True)
    args = parser.parse_args()

    result = getInfo(args.username, args.sessionid)

    if "error" in result:
        print(result["error"])
    else:
        print(f"\n✅ Extracted Data:")
        print(f"Username: {result['username']}")
        print(f"Email: {result['email']}")
        print(f"Phone: {result['phone']}")


if __name__ == "__main__":
    main()
