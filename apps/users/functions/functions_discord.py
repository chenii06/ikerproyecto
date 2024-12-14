# Django
from django.db.models import F, Window, Sum, Case, When, CharField, Value, ExpressionWrapper, Func, IntegerField, BooleanField, Q, OuterRef, Subquery
from django.db.models.functions import Rank, Lag, Lead
from django_cte import CTEManager, With

# Functions
from apps.demonlist import functions

# Models
from apps.demonlist.models import Demon, Record, Changelog
from apps.users.models import Profile

# Utils
import requests
import time


server_id = "1269343828075348064"
bot_token = ""
client_id = "1271128335988293652"
client_secret = "HmWS9WcIA7KE8NtiZDJEfmI-W5P_BaPr"

roles_dict = {"ALL RATED LIST COMPLETED": "1190944270346096700",
              "All Unrated List Complete": "1201169315471294514",
              "List Points": "1189409689813917808",
              "+500 List Points": "1201912102093344868",
              "+1000 List Points": "1190667405282779188",
              "+1500 List Points": "1191834424740950146",
              "+2000 List Points": "1191591867750551652",
              "+2500 List Points": "1193259053263102092",
              "+3000 List Points": "1192189434905514044",
              "+3500 List Points": "1198744419260694649",
              "+4000 List Points": "1192189628887859210",
              "+4500 List Points": "1198745411582697574",
              "+5000 List Points": "1192189804570484766",
              "+5500 List Points": "1198747642088411238",
              "+6000 List Points": "1198747184116543588",
              "+6500 List Points": "1198747785118371951",
              "+7000 List Points": "1198747351360213102",
              "+7500 List Points": "1198748402935156847",
              "+8000 List Points": "1198748876052643912",
              "First Record": "1189409922866233494",
              "Top #1 Demon": "1189411032406446090",
              "Top #1 Unrated Demon": "1201169234374434826",
              "#1 Player": "1190666100069900340",
              "Verified": "1190847323622871170",





            "Developer": "1189387302108135554",
            "Notify Changelog": "1189412915552452608",
            "List Helper": "1189387383490228236",
            }


# Función para que un usuario se autorice con discord
def exchange_code(code):

    API_ENDPOINT = "https://discord.com/api/v10/oauth2/token"
    REDIRECT_URI = "https://www.geomax.site/users/oauth2/login/redirect"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(API_ENDPOINT, data=data, headers=headers, auth=(client_id, client_secret))

    credentials = response.json()

    access_token = credentials["access_token"]
    response = requests.get("https://discord.com/api/v10/users/@me", headers={
        "Authorization": f"Bearer {access_token}"
    })
    user = response.json()
    return user




# Función para actualizar cierto rol en todos los miembros
def members_rol(role_name, option):
    bot_url = f"https://discord.com/api/v10/guilds/{server_id}/members"
    if role_name != "Top Player":
        role_id = roles_dict[role_name]

        headers = {
            'Authorization': f'Bot {bot_token}',
        }

        iteration = True
        after = 0
        members_with_role = []
        while iteration:
            response = requests.get(bot_url, headers=headers, params = {"limit": 1000, "after": after})

            if response.status_code == 200:
                members_with_role.extend(member["user"]["id"] for member in response.json() if role_id in member["roles"])
                if len(response.json()) < 1000:
                    iteration = False
                after = response.json()[-1]["user"]["id"]
            else:
                iteration = False
                print(f"Error: La solicitud a la API de Discord falló con el código {response.status_code}.")
                return []

    members = list(Profile.objects.filter(id_discord__isnull=False, verified=True).values_list("id_discord", flat=True))
    if option == "remove_role":
        discord_user_rol(members, [role_id], False)
    elif option == "confirm_role":
        if role_name == "ALL RATED LIST COMPLETED":
            check_all_rated_list(members, "platformer")
        elif role_name == "All Unrated List Complete":
            check_all_unrated_list(members, "platformer")
        elif role_name == "List Points":
            check_list_points(members, "platformer")
        elif role_name == "Top #1 Demon":
            check_top_1_rated(members)
        elif role_name == "Top #1 Unrated Demon":
            check_top_1_unrated(members)
        elif role_name == "Top Player":
            check_top_player(members, "platformer")
        elif role_name == "First Record":
            check_first_victor(members, "platformer")

# Función para checar que tenga toda la rated_list completada
def check_all_rated_list(discord_users_to_check, mode):
    for discord_user_id in discord_users_to_check:
        all_demons = list(Demon.objects.filter(mode=mode, category="rated").order_by("rated_position").values_list("level", flat=True))
        player_demons = list(Record.objects.filter(demon__mode=mode, demon__category="rated", player__id_discord=discord_user_id, accepted=True).distinct().order_by("demon__rated_position").values_list("demon__level", flat=True))

        if all_demons == player_demons:
            discord_user_rol([discord_user_id], [roles_dict["ALL RATED LIST COMPLETED"]], True)
        else:
            discord_user_rol([discord_user_id], [roles_dict["ALL RATED LIST COMPLETED"]], False)

# Función para checar que tenga toda la unrated_list completada
def check_all_unrated_list(discord_users_to_check, mode):
    for discord_user_id in discord_users_to_check:
        all_demons = list(Demon.objects.filter(mode=mode, category="unrated").order_by("unrated_position").values_list("level", flat=True))
        player_demons = list(Record.objects.filter(demon__mode=mode, demon__category="unrated", player__id_discord=discord_user_id, accepted=True).distinct().order_by("demon__unrated_position").values_list("demon__level", flat=True))

        if all_demons == player_demons:
            discord_user_rol([discord_user_id], [roles_dict["All Unrated List Complete"]], True)
        else:
            discord_user_rol([discord_user_id], [roles_dict["All Unrated List Complete"]], False)


# Función para checar los puntos de lista que tiene cada usuario
def check_list_points(discord_users_to_check, mode):
    for discord_user_id in discord_users_to_check:
        try:
            profile = Profile.objects.filter(id_discord=discord_user_id, verified=True)[0]
        except:
            break
        if mode == "classic":
            """classic_list_points = profile.classic_list_points
            if classic_list_points >= 1:
                discord_user_rol([discord_user_id], [roles_dict[f"Classic List Points"]], True)
            else:
                discord_user_rol([discord_user_id], [roles_dict[f"Classic List Points"]], False)"""
            pass
        elif mode == "platformer":
            platformer_list_points = profile.platformer_list_points
            if platformer_list_points >= 1:
                discord_user_rol([discord_user_id], [roles_dict[f"List Points"]], True)
            else:
                discord_user_rol([discord_user_id], [roles_dict[f"List Points"]], False)
        for i in range(16):

            points_role = (i + 1) * 500

            if mode == "classic":
                """if classic_list_points >= points_role:
                    discord_user_rol([discord_user_id], [roles_dict[f"+{points_role} Classic List Points"]], True)
                else:
                    discord_user_rol([discord_user_id], [roles_dict[f"+{points_role} Classic List Points"]], False)"""
                pass
            elif mode == "platformer":
                if platformer_list_points >= points_role:
                    discord_user_rol([discord_user_id], [roles_dict[f"+{points_role} List Points"]], True)
                else:
                    discord_user_rol([discord_user_id], [roles_dict[f"+{points_role} List Points"]], False)


# Función para checar si es first victor
def check_first_victor(discord_users_to_check):
    for discord_user_id in discord_users_to_check:
        first_victor = Record.objects.filter(player__id_discord=discord_user_id, top_order=1).exists()

        if first_victor:
            discord_user_rol([discord_user_id], [roles_dict[f"First Record"]], True)
        else:
            discord_user_rol([discord_user_id], [roles_dict[f"First Record"]], False)


# Función para checar si se ha completado el top 1 rated
def check_top_1_rated(discord_users_to_check):
    for discord_user_id in discord_users_to_check:
        top_1_rated = Record.objects.filter(player__id_discord=discord_user_id, demon__rated_position=1, accepted=True).exists()

        if top_1_rated:
            discord_user_rol([discord_user_id], [roles_dict[f"Top #1 Demon"]], True)
        else:
            discord_user_rol([discord_user_id], [roles_dict[f"Top #1 Demon"]], False)

# Función para checar si se ha completado el top 1 unrated
def check_top_1_unrated(discord_users_to_check):
    for discord_user_id in discord_users_to_check:
        top_1_unrated = Record.objects.filter(player__id_discord=discord_user_id, demon__unrated_position=1, accepted=True).exists()

        if top_1_unrated:
            discord_user_rol([discord_user_id], [roles_dict[f"Top #1 Unrated Demon"]], True)
        else:
            discord_user_rol([discord_user_id], [roles_dict[f"Top #1 Unrated Demon"]], False)


# Función para checar quién es el top 1 en la leaderboard
def check_top_player(discord_users_to_check, mode):
    for discord_user_id in discord_users_to_check:

        if mode == "classic":
            """cte = With(Profile.objects.filter(classic_list_points__gte=1).annotate(
                position=Window(expression=Rank(), order_by=F('classic_list_points').desc())
            ))
            role_word = "Classic "
            """
            pass
        elif mode == "platformer":
            cte = With(Profile.objects.filter(platformer_list_points__gte=1).annotate(
                position=Window(expression=Rank(), order_by=F('platformer_list_points').desc())
            ))
            role_word = ""
        top_1_player = cte.queryset().with_cte(cte).filter(id_discord=discord_user_id, position=1).exists()

        if top_1_player:
            discord_user_rol([discord_user_id], [roles_dict[f"{role_word}#1 Player"]], True)
        else:
            discord_user_rol([discord_user_id], [roles_dict[f"{role_word}#1 Player"]], False)

# Función para asignar o quitar un rol a un usuario
def discord_user_rol(users_to_assign, roles_to_assign, add):

    for user_id in users_to_assign:
        for role_id in roles_to_assign:
            url = f"https://discord.com/api/v10/guilds/{server_id}/members/{user_id}/roles/{role_id}"

            response_sent = False
            while not(response_sent):

                if add:
                    response = requests.put(url, headers={"Authorization": f"Bot {bot_token}"}, verify=False)
                else:
                    response = requests.delete(url, headers={"Authorization": f"Bot {bot_token}"}, verify=False)

                if response.status_code == 429:
                    time.sleep(1)
                else:
                    response_sent = True

    return response







# Función para saber cuántos miembros con cierto rol hay
def num_members_rol():
    bot_url = f"https://discord.com/api/v10/guilds/{server_id}/members"
    role_id = "1189412915552452608"
    role_name = "Notify Changelog"

    headers = {
        'Authorization': f'Bot {bot_token}',
    }

    iteration = True
    after = 0
    members_with_role = 0
    while iteration:
        response = requests.get(bot_url, headers=headers, params = {"limit": 1000, "after": after})

        if response.status_code == 200:
            members_with_role += len([
                member for member in response.json() if role_id in member["roles"]
            ])
            if len(response.json()) < 1000:
                iteration = False
            after = response.json()[-1]["user"]["id"]
        else:
            iteration = False
            print(f"Error: La solicitud a la API de Discord falló con el código {response.status_code}.")
            return []
    
    print(f"Cantidad de miembros con el rol {role_name}: {members_with_role}")
    
    return response
