import fire

from lunar_birthday.core import LunarBirthday


class Command:
    """Google calendar Tool
    """

    def insert(self):
        """get all birthdays from your contacts and then insert
        """
        self.lb = LunarBirthday()
        self.lb.get_contacts_birthdays()
        self.lb.insert_event_to_calendar()


def main():
    fire.Fire(Command)
