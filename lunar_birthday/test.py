from core import LunarBirthday


def test_lunar():

    lunar_birthday = LunarBirthday()

    lunar_birthday.get_contacts_birthdays()
    print('获取联系人成功')
    lunar_birthday.insert_event_to_calendar()
    print('更新生日事件完成')


if __name__ == '__main__':
    test_lunar()
