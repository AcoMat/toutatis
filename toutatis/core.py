import phonenumbers
import pycountry
from phonenumbers import region_code_for_country_code

# Asegúrate de que se han obtenido correctamente los datos de la cuenta
search = args.id or args.username
infos = getInfo(search, sessionsId, searchType=search_type)

if not infos.get("user"):
    exit(infos["error"])

infos = infos["user"]

print("Informations about     : " + infos["username"])
print("userID                 : " + infos["userID"])

# Verificar si la clave 'full_name' existe
full_name = infos.get("full_name", "No disponible")
print("Full Name              : " + full_name)

print("Verified               : " + str(infos['is_verified']) + " | Is business Account : " + str(infos["is_business"]))
print("Is private Account     : " + str(infos["is_private"]))
print("Follower               : " + str(infos["follower_count"]) + " | Following : " + str(infos["following_count"]))
print("Number of posts        : " + str(infos["media_count"]))

# Verificar si la URL externa existe
if infos.get("external_url"):
    print("External url           : " + infos["external_url"])

print("IGTV posts             : " + str(infos["total_igtv_videos"]))
print("Biography              : " + (f"""\n{" " * 25}""").join(infos["biography"].split("\n")))
print("Linked WhatsApp        : " + str(infos["is_whatsapp_linked"]))
print("Memorial Account       : " + str(infos["is_memorialized"]))
print("New Instagram user     : " + str(infos["is_new_to_instagram"]))

# Verificar si 'public_email' y 'public_phone_number' existen
if "public_email" in infos and infos["public_email"]:
    print("Public Email           : " + infos["public_email"])

if "public_phone_number" in infos and str(infos["public_phone_number"]):
    phonenr = "+" + str(infos["public_phone_country_code"]) + " " + str(infos["public_phone_number"])
    try:
        pn = phonenumbers.parse(phonenr)
        countrycode = region_code_for_country_code(pn.country_code)
        country = pycountry.countries.get(alpha_2=countrycode)
        phonenr = phonenr + " ({}) ".format(country.name)
    except Exception as e:
        print(f"Error al procesar el teléfono: {e}")
    print("Public Phone number    : " + phonenr)

other_infos = advanced_lookup(infos["username"])

if other_infos.get("error") == "rate limit":
    print("Rate limit please wait a few minutes before you try again")
elif "message" in other_infos.get("user", {}):
    if other_infos["user"].get("message") == "No users found":
        print("The lookup did not work on this account")
    else:
        print(other_infos["user"]["message"])
else:
    if "obfuscated_email" in other_infos.get("user", {}):
        if other_infos["user"]["obfuscated_email"]:
            print("Obfuscated email       : " + other_infos["user"]["obfuscated_email"])
        else:
            print("No obfuscated email found")

    if "obfuscated_phone" in other_infos.get("user", {}):
        if str(other_infos["user"]["obfuscated_phone"]):
            print("Obfuscated phone       : " + str(other_infos["user"]["obfuscated_phone"]))
        else:
            print("No obfuscated phone found")

print("-" * 24)
print("Profile Picture        : " + infos["hd_profile_pic_url_info"]["url"])
