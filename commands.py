import json

import requests as requests

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    # Transmits commands to Discord.
    print("Sending commands...")
    with open("commands.json", "r") as command_file:
        data = command_file.read()
        data = json.loads(data)

    app_id = os.getenv("app_id")
    api_url = f"https://discord.com/api/v10/applications/{app_id}"

    api_url += "/guilds/981646409176588308" # COMMENT THIS LINE OUT FOR PROD

    api_url += "/commands"

    token = os.getenv("token")
    headers = {
        "Authorization": f"Bot {token}"
    }

    r = requests.put(url=api_url, headers=headers, json=data)
    print(r.content)
