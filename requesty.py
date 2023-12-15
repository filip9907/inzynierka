import datetime
import requests

LOGIN_URL = "https://logowanie.tauron-dystrybucja.pl/login"
DATA_URL = "https://elicznik.tauron-dystrybucja.pl/energia/do/dane"

def login(username, password):
    session = requests.Session()
    session.get(LOGIN_URL)
    session.post(
        LOGIN_URL,
        data={
            "username": username,
            "password": password,
            "service": "https://elicznik.tauron-dystrybucja.pl",
        },
    )
    return session

def get_raw_data(session, start_date, end_date=None):
    end_date = end_date or start_date
    response = session.get(
        DATA_URL,
        params={
            "form[from]": start_date.strftime("%d.%m.%Y"),
            "form[to]": end_date.strftime("%d.%m.%Y"),
            "form[type]": "godzin",  # or "dzien"
            "form[energy][consum]": 1,
            "form[energy][oze]": 1,
            "form[energy][netto]": 1,
            "form[energy][netto_oze]": 1,
            "form[fileType]": "CSV",  # or "XLS"
        },
    )

    if response.status_code == 200:
        return response.text.splitlines()
    else:
        print(response.status_code)
        print(response.text)
        response.raise_for_status()
#login=""
#passwrd=""
# Previous code for login
session = login(login, passwrd)

# Example usage of get_raw_data with specific parameters
start_date = datetime.date(2023, 1, 1)
end_date = datetime.date(2023, 1, 7)  # Replace with your desired end date
raw_data = get_raw_data(session, start_date, end_date)

# Print the generated link for reference
generated_link = f"{DATA_URL}?{'&'.join([f'{key}={value}' for key, value in {'form[from]': start_date.strftime('%d.%m.%Y'), 'form[to]': end_date.strftime('%d.%m.%Y'), 'form[type]': 'godzin', 'form[energy][consum]': 1, 'form[energy][oze]': 1, 'form[energy][netto]': 1, 'form[energy][netto_oze]': 1, 'form[fileType]': 'CSV'}.items()])}"
print("Generated Link:", generated_link)

# Process the raw data (assuming it's CSV with semicolon as delimiter)
# The rest of the code for processing the data remains unchanged
