from service import LunarBirthday

client_id = '108884890762-0jpidgfadtlp0f90urv6513vah5uphbu.apps.googleusercontent.com'
client_secret = 'u9gk_gb4pyoE_WeGqQj6iBY5'


def test_lunar():

    lunar_birthday = LunarBirthday(client_id, client_secret)

    lunar_birthday.get_contacts_birthdays()
    print('获取联系人成功')
    lunar_birthday.insert_event_to_calendar()
    print('更新生日事件完成')


if __name__ == '__main__':
    test_lunar()
