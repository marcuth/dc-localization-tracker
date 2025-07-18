from dcutils.static.localization import Localization
from discord_webhook import DiscordWebhook
from datetime import datetime
import decouple
import json
import os

localization_comparison_webhook_url = decouple.config("DISCORD_LOCALIZATION_COMPARISON_WEBHOOK_URL")
localization_file_sending_webhook_url = decouple.config("DISCORD_LOCALIZATION_FILE_SENDING_WEBHOOK_URL")

languages = ["br", "en", "es"]

localizations_out_dir = "localizations"
compressed_localizations_out_dir = os.path.join(localizations_out_dir, "compressed")

def send_message_of_comparision_result_on_discord(comparasion_result: dict, language: str) -> None:
    webhook = DiscordWebhook(localization_comparison_webhook_url)

    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y - %H:%M:%S")

    comparasion_result_filename = "comparasion_result.json"
    file_content = json.dumps(comparasion_result, indent = 4)

    webhook.add_file(file = file_content, filename = comparasion_result_filename)

    message_content = f"Resultado da comparação para o dados de localização `{language}` em {current_time}."
    webhook.set_content(message_content)

    response = webhook.execute()
    
    if response.status_code != 200:
        print(f"Falha ao enviar mensagem para o Discord: {response.status_code} {response.reason}")

def send_message_of_compressed_localization(compressed_localization_file_path: str, language: str) -> None:
    webhook = DiscordWebhook(localization_file_sending_webhook_url)

    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y - %H:%M:%S")
    localization_filename = f"localization_{language}_{now.month}_{now.day}_{now.year}.json.gz"

    with open(compressed_localization_file_path, "rb") as file:
        file_content = file.read()

    webhook.add_file(file = file_content, filename = localization_filename)

    message_content = f"Dados de localização `{language}` em {current_time}."
    webhook.set_content(message_content)

    response = webhook.execute()
    
    if response.status_code != 200:
        print(f"Falha ao enviar mensagem para o Discord: {response.status_code} {response.reason}")

def main() -> None:
    if not os.path.exists(localizations_out_dir):
        os.mkdir(localizations_out_dir)

    if not os.path.exists(compressed_localizations_out_dir):
        os.mkdir(compressed_localizations_out_dir)

    for language in languages:
        localization = Localization(language)
        localization_filename = f"localization_{language}.json"
        localization_file_path = os.path.join(localizations_out_dir, localization_filename)

        if os.path.exists(localization_file_path):
            old_localization = Localization.load_file(localization_file_path)
            comparasion_result = localization.compare(old_localization)
            has_changes = len(comparasion_result["new_fields"]) > 0 or len(comparasion_result["edited_fields"]) > 0 or len(comparasion_result["deleted_fields"]) > 0

            if has_changes:
                try:
                    send_message_of_comparision_result_on_discord(comparasion_result, language)

                except:
                    pass

        localization.save_file(localization_file_path)

        compressed_localization_filename = f"localization_{language}.json.gz"
        compressed_localization_file_path = os.path.join(compressed_localizations_out_dir, compressed_localization_filename)

        localization.save_compressed_file(compressed_localization_file_path)

        try:
            send_message_of_compressed_localization(compressed_localization_file_path, language)

        except:
            pass

if __name__ == "__main__":
    main()