import pickle
from datetime import datetime, timedelta

class AddressBook:
    def __init__(self):
        self.records = {}

    def add_record(self, record):
        self.records[record.name.value] = record

    def find(self, name):
        return self.records.get(name)

    def get_all_records(self):
        return self.records.values()

    def save_to_file(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load_from_file(filename):
        try:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook()

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def to_dict(self):
        return {
            'name': self.name.value,
            'phones': [phone.value for phone in self.phones],
            'birthday': self.birthday.value if self.birthday else None
        }

    @classmethod
    def from_dict(cls, data):
        record = cls(data['name'])
        for phone in data['phones']:
            record.add_phone(phone)
        if data['birthday']:
            record.add_birthday(data['birthday'])
        return record

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e)
    return wrapper

@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    return "Contact not found."

@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is on {record.birthday.value}."
    return "Birthday not found."

@input_error
def birthdays(args, book):
    today = datetime.today()
    next_week = today + timedelta(days=7)
    upcoming_birthdays = [
        record.name.value for record in book.get_all_records()
        if record.birthday and today <= datetime.strptime(record.birthday.value, '%d.%m.%Y') <= next_week
    ]
    return "Upcoming birthdays: " + ", ".join(upcoming_birthdays) if upcoming_birthdays else "No birthdays in the next week."

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        for phone in record.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return f"Phone number updated for {name}."
        return "Old phone number not found."
    return "Contact not found."

@input_error
def find_contact(args, book):
    name, *_ = args
    record = book.find(name)
    if record:
        phones = ', '.join(phone.value for phone in record.phones)
        birthday = record.birthday.value if record.birthday else "N/A"
        return f"Name: {record.name.value}, Phones: {phones}, Birthday: {birthday}"
    return "Contact not found."

def parse_input(user_input):
    return user_input.strip().split()

def main():
    book = AddressBook.load_from_file('address_book.pkl')

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            book.save_to_file('address_book.pkl')
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(find_contact(args, book))

        elif command == "all":
            for record in book.get_all_records():
                phones = ', '.join(phone.value for phone in record.phones)
                birthday = record.birthday.value if record.birthday else "N/A"
                print(f"Name: {record.name.value}, Phones: {phones}, Birthday: {birthday}")

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
