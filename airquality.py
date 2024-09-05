import requests
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Coordenadas de Porto Alegre
latitude = "-30.0346"
longitude = "-51.2177"
api_key = "15a29fa2c0dca0d064e607ce8c261b89"

# Função para obter dados de qualidade do ar
def get_air_quality_data(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)
    data = response.json()

    # Verificar se a chave 'list' está presente na resposta
    if 'list' not in data:
        print("Erro: Resposta da API não contém a chave 'list'.")
        print("Resposta completa da API:", data)
        return None

    # Verificar se 'components' e 'main' estão presentes no primeiro item da lista
    if 'components' not in data['list'][0] or 'main' not in data['list'][0]:
        print("Erro: A estrutura esperada não está presente.")
        print("Resposta completa da API:", data)
        return None

    return data


# Função para salvar dados no Google Sheets
def save_to_google_sheets(data):
    if data is None:
        print("Erro: Dados inválidos. O salvamento foi cancelado.")
        return

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    SPREADSHEET_ID = '1xbrPGrpdTk94ntYxpj-4snbN4qXrK7zLoWmt1OYjyF0'
    RANGE_NAME = 'Sheet1!A2'

    components = data['list'][0]['components']
    aqi = data['list'][0]['main']['aqi']
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    values = [
        [timestamp, aqi, components['co'], components['no2'], components['o3'], components['pm2_5']]
    ]
    body = {
        'values': values
    }

    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="RAW",
        body=body
    ).execute()


# Script principal
if __name__ == "__main__":
    data = get_air_quality_data(latitude, longitude, api_key)
    save_to_google_sheets(data)