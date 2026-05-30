# 1. Імпорти
import pickle
from collections import UserDict
from datetime import datetime, date, timedelta


# 2. Класи (вже є з Кроку 1)
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    # реалізація класу
    pass


class Phone(Field):
    # реалізація класу
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("The phone number must be a 10-digits long.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            # Додайте перевірку коректності даних
            # та перетворіть рядок на об'єкт datetime
            string_to_object = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(string_to_object)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # реалізація класу

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number)
        if phone is not None:
            self.phones.remove(phone)
        else:
            raise ValueError("That phone number wasn't found!")

    def edit_phone(self, phone_number, new_phone):
        phone = self.find_phone(phone_number)
        if phone is None:
            raise ValueError("That phone number wasn't found!")
        new_phone_obj = Phone(new_phone)
        index = self.phones.index(phone)
        self.phones[index] = new_phone_obj

    def find_phone(self, value):
        for phone in self.phones:
            if phone.value == value:
                return phone
        return None

    def add_birthday(self, birthday_day):
        self.birthday = Birthday(birthday_day)

    def __str__(self):
        # Додано відображення дня народження, якщо воно є
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"


class AddressBook(UserDict):
    # реалізація класу
    def add_record(self, record_object):
        self.data[record_object.name.value] = record_object

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name not in self.data:
            raise KeyError("There is no such contact!")
        del self.data[name]

    def get_upcoming_birthdays(self):
        today = date.today()
        result = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            born = record.birthday.value
            try:
                candidate = born.replace(year=today.year)
            except ValueError:
                candidate = born.replace(year=today.year, day=28)

            if candidate < today:
                try:
                    candidate = born.replace(year=today.year + 1)
                except ValueError:
                    candidate = born.replace(year=today.year + 1, day=28)

            delta = (candidate - today).days

            if 0 <= delta <= 7:

                if candidate.weekday() == 5:
                    candidate += timedelta(days=2)
                elif candidate.weekday() == 6:
                    candidate += timedelta(days=1)

                result.append(
                    {
                        "name": record.name.value,
                        "congratulation_date": candidate.strftime("%d.%m.%Y"),
                    }
                )

        result.sort(
            key=lambda x: datetime.strptime(x["congratulation_date"], "%d.%m.%Y")
        )
        return result


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено


# 3. Декоратор
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError as e:
            return str(e)
        except IndexError:
            return "Not enough data!"

    return inner


# 4. Функції-обробники
def parse_input(user_input):
    parts = user_input.strip().split()

    if not parts:  # Якщо ввели порожній рядок
        return "", []

    cmd = parts[0].lower()  # Команду робимо маленькими літерами
    args = parts[1:]  # Аргументи (імена, телефони) залишаємо як є

    return cmd, args


@input_error
def add_birthday(args, book):
    name = args[0]
    birthday = args[1]
    record = book.find(name)  # ← як знайти контакт у книзі?
    if record is None:  # що робити якщо record == None?
        return "There is no record with that name!"
    record.add_birthday(birthday)  # що робити якщо знайшли?
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    if record.birthday is None:
        return "Contact is without birthday."
    return f"Birthday for {name}: {record.birthday}"


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays found in this period."
    return "\n".join(
        f"{record['name']}: {record['congratulation_date']}" for record in upcoming
    )


@input_error
def add_contact(args, book: AddressBook):
    name = args[0]
    # Беремо телефон тільки тоді, коли користувач його дійсно ввів
    phone = args[1] if len(args) > 1 else None

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
def change_phone(args, book):
    name = args[0]
    old_phone = args[1]
    new_phone = args[2]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.edit_phone(old_phone, new_phone)
    return "The phone number was changed."


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    return "; ".join(phone.value for phone in record.phones)


def show_all_contacts(book):
    if not book.data:
        return "There are no records."
    return "\n".join(str(record) for record in book.data.values())


# 5. Головна функція
def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all_contacts(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


# 6. Точка входу
if __name__ == "__main__":
    main()
