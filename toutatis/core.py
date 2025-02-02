import argparse
import requests
from urllib.parse import quote_plus
from json import dumps, decoder

import phonenumbers
from phonenumbers.phonenumberutil import (
    region_code_for_country_code,
    region_code_for_number,
)
import pycountry


def getUserId(username, sessionsId):
    headers = {"User-Agent": "iphone_ua", "x-ig-app-id": "936619743392459"}
    api = requests.get(
        f'https://i.instagram.com/api/v1/users/web_profile_info/?username={username}',
        headers=headers,
        cookies={'sessionid': sessionsId}
    )
    try:
        if api.status_code == 404:
            return {"id": None, "error": "User not found"}

        id = api.json()["data"]['user']['id']
        return {"id": id, "error": None}

    except decoder.JSONDecodeError:
        return {"id": None, "error": "Rate limit"}


def getInfo(search, sessionId, searchType="username"):
    searchType = "username" if searchType == "username" else "id"

    if searchType == "username":
        data = getUserId(search, sessionId)
        if data["error"]:
            return data
        userId = data["id"]
    else:
        try:
            userId = str(int(search))
        except ValueError:
            return {"user": None, "error": "Invalid ID"}

    try:
        response = requests.get(
            f'https://i.instagram.com/api/v1/users/{userId}/info/',
            headers={'User-Agent': 'Instagram 64.0.0.14.96'},
            cookies={'sessionid': sessionId}
        )
        if response.status_code == 429:
            return {"user": None, "error": "Rate limit"}

        response.raise_for_status()

        info_user = response.json().get("user")
        if not info_user:
            return {"user": None, "error": "Not found"}

        info_user["userID"] = userId
        return {"user": info_user, "error": None}

    except requests.exceptions.RequestException:
        return {"user": None, "error": "Not found"}


def advanced_lookup(username):
    """
        Post to get obfuscated login infos
    """
    data = "signed_body=SIGNATURE." + quote_plus(dumps(
        {"q": username, "skip_recovery": "1"},
        separators=(",", ":")
    ))
    api = requests.post(
        'https://i.instagram.com/api/v1/users/lookup/',
        headers={
            "Accept-Language": "en-US",
            "User-Agent": "Instagram 101.0.0.15.120",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-IG-App-ID": "124024574287414",
            "Accept-Encoding": "gzip, deflate",
            "Host": "i.instagram.com",
            "Connection": "keep-alive",
            "Content-Length": str(len(data))
        },
        data=data
    )

    try:
        return ({"user": api.json(), "error": None})
    except decoder.JSONDecodeError:
        return ({"user": None, "error": "Rate limit"})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sessionid', help="Instagram session ID", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--username', help="One username")
    group.add_argument('-i', '--id', help="User ID")
    args = parser.parse_args()

    sessionsId = args.sessionid
    search_type = "id" if args.id else "username"
    search = args.id or args.username
    infos = getInfo(search, sessionsId, searchType=search_type)
    
    if not infos.get("user"):
        exit(infos["error"])

    infos = infos["user"]

    # 🔹 Imprime los datos completos para depuración
    print(dumps(infos, indent=4))  

    print("Informations about     : " + infos.get("username", "Unknown"))
    print("userID                 : " + infos.get("userID", "Unknown"))
    print("Linked WhatsApp        : " + str(infos.get("is_whatsapp_linked", "Unknown")))
    print("Verified Profile       : " + str(infos.get("is_verified", "Unknown")))

    if infos.get("public_email"):
        print("Public Email           : " + infos["public_email"])

    if infos.get("public_phone_number"):
        phone_country = infos.get("public_phone_country_code", "")
        phone_number = infos.get("public_phone_number", "")
        phonenr = f"+{phone_country} {phone_number}"

        try:
            pn = phonenumbers.parse(phonenr)
            countrycode = region_code_for_country_code(pn.country_code)
            country = pycountry.countries.get(alpha_2=countrycode)
            phonenr = f"{phonenr} ({country.name})"
        except Exception as e:
            print(f"Error procesando número de teléfono: {e}")

        print("Public Phone number    : " + phonenr)

    other_infos = advanced_lookup(infos["username"])

    if other_infos["error"] == "Rate limit":
        print("Rate limit please wait a few minutes before you try again")

    elif other_infos["user"].get("message") == "No users found":
        print("The lookup did not work on this account")
    else:
        if other_infos["user"].get("obfuscated_email"):
            print("Obfuscated email       : " + other_infos["user"]["obfuscated_email"])
        else:
            print("No obfuscated email found")

        if other_infos["user"].get("obfuscated_phone"):
            print("Obfuscated phone       : " + str(other_infos["user"]["obfuscated_phone"]))
        else:
            print("No obfuscated phone found")

    print("-" * 24)
    print("Profile Picture        : " + infos.get("hd_profile_pic_url_info", {}).get("url", "Unknown"))


if __name__ == "__main__":
    main()
    
