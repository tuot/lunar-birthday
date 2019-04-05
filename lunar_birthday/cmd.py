import os
import logging
import argparse
import sys

from lunar_birthday.service import LunarBirthday


def parse_args():
    parser = argparse.ArgumentParser(description='Google calendar Tool')
    parser.add_argument('client_id', help='setup client id')
    parser.add_argument('client_secret', help='setup client secret')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-a',
        '--add',
        action='store_true',
        help='get all all birthdays from your contacts and then insert')
    group.add_argument(
        '-f',
        '--file',
        help='insert all events to google calendar from your all events file')

    return parser.parse_args()


def main():
    args = parse_args()
    sys.argv[1:] = []
    print(args)
    if args.client_id and args.client_secret:
        lb = LunarBirthday(args.client_id, args.client_secret)
        if args.add:
            lb.get_contacts_birthdays()
            lb.insert_event_to_calendar()
        elif args.file:
            if os.path.exists(args.file):
                lb.insert_event_to_calendar(bir_file=args.file)
            else:
                logging.error('File does not exist')
                exit(0)
