
from service import LunarBirthday


client_id = '108884890762-0jpidgfadtlp0f90urv6513vah5uphbu.apps.googleusercontent.com'
client_secret = 'u9gk_gb4pyoE_WeGqQj6iBY5'


def test_lunar():

    lunar_birthday = LunarBirthday(client_id, client_secret)

    lunar_birthday.get_contacts_birthdays()
    # lunar_birthday.insert_event_to_calendar()


if __name__ == '__main__':
    test_lunar()
