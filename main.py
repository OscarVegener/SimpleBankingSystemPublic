import random
import sqlite3
from sqlite3 import Error

current_user = None
connection = None
cursor = None


def table():
    query = "SELECT * FROM card;"
    q = cursor.execute(query)
    output = cursor.fetchall()
    print(output)
    connection.commit()


class User:

    def __init__(self, registration):
        if registration:
            self.card_number = self.generate_card_number()
            self.pin = self.generate_pin()
            self.balance = 0
            self.id = None
            self.initialized = True
            print("Your card has been created")
            print("Your card number:\n{}".format(self.card_number))
            print("Your card PIN:\n{}".format(self.pin))
            # query = "INSERT INTO card (number, pin) VALUES({}, {});".format(self.card_number, self.pin)
            # cursor.execute(query)
            cursor.execute("INSERT INTO card (number, pin) VALUES(?, ?);", (self.card_number, self.pin,))
            connection.commit()
            query = "SELECT * FROM card WHERE number = {} AND pin = {};".format(self.card_number, self.pin)
            cursor.execute(query)
            connection.commit()
            result = cursor.fetchone()
            self.id = result[0]
        else:
            self.initialized = False
            self.card_number = None
            self.pin = None
            self.balance = None
            self.id = None

    def fill(self, number, pin):
        query = "SELECT * FROM card WHERE number = {} AND pin = {};".format(number, pin)
        cursor.execute(query)
        connection.commit()
        results = cursor.fetchone()
        self.id = results[0]
        self.card_number = results[1]
        self.pin = results[2]
        self.balance = results[3]

    def fetch(self):
        query = "SELECT * FROM card WHERE number = {} AND pin = {};".format(self.card_number, self.pin)
        cursor.execute(query)
        connection.commit()
        results = cursor.fetchone()
        self.id = results[0]
        self.card_number = results[1]
        self.pin = results[2]
        self.balance = results[3]

    def commit(self):
        # query = "UPDATE card SET number = {}, SET pin = {}, SET balance = {} WHERE id = {};".format(self.card_number,
        #                                                                                            self.pin,
        #                                                                                            self.balance,
        #                                                                                            self.id)
        # cursor.execute(query)
        cursor.execute("UPDATE card SET number = (?), SET pin = (?), SET balance = (?) "
                       "WHERE id = (?)", (self.card_number, self.pin, self.balance, self.id))
        connection.commit()

    def update_balance(self):
        params = (self.balance, self.id)
        # query = "UPDATE card SET balance = {} WHERE id = {};".format(self.balance, self.id)
        # cursor.execute("UPDATE card SET balance = () WHERE id = ();", params)
        cursor.execute("UPDATE card SET balance = (?) WHERE id = (?)", (self.balance, self.id,))
        connection.commit()

    def delete_account(self):
        query = "DELETE FROM card WHERE id = {}".format(self.id)
        cursor.execute(query)
        connection.commit()

    @staticmethod
    def generate_checksum(lst_number):
        for i in range(len(lst_number)):
            if i % 2 == 0:
                lst_number[i] *= 2
        digits_sum = 0
        for i in range(len(lst_number)):
            if lst_number[i] > 9:
                lst_number[i] -= 9
            digits_sum += lst_number[i]
        if digits_sum % 10 == 0:
            return 0
        else:
            return 10 - digits_sum % 10

    @staticmethod
    def generate_card_number():
        card_number = [4]
        for i in range(5):
            card_number.append(0)
        for i in range(9):
            i = random.randint(0, 9)
            card_number.append(i)
        str_number = [str(digit) for digit in card_number]
        checksum = str(User.generate_checksum(card_number))
        return "".join(str_number) + checksum

    @staticmethod
    def generate_pin():
        pin = []
        for i in range(4):
            i = random.randint(1, 9)
            pin.append(str(i))
        pin = "".join(pin)
        return pin


def login():
    print("Enter your card number:")
    c_number = input()
    print("Enter your PIN:")
    pin = input()
    try:
        query = "SELECT * FROM card WHERE number = {} AND pin = {};".format(c_number, pin)
        cursor.execute(query)
        connection.commit()
        result = cursor.fetchall()
    except Error as e:
        print("Wrong card number or PIN!")
        return -1
    finally:
        if len(result) < 1:
            print("Wrong card number or PIN!")
            return -1
        print("You have successfully logged in!")
        global current_user
        current_user = User(False)
        current_user.fill(c_number, pin)
        return 1


def validate_card(card_number):
    lst = [int(x) for x in card_number]
    number_sum = 0
    for i in range(len(lst) - 1):
        if i % 2 == 0:
            lst[i] *= 2
            if lst[i] > 9:
                lst[i] -= 9
        number_sum += lst[i]
    if number_sum % 10 == 10 - lst[len(lst) - 1]:
        return True
    else:
        return False


def user_cycle():
    global current_user
    while True:
        print("1. Balance")
        print("2. Add income")
        print("3. Do transfer")
        print("4. Close account")
        print("5. Log out")
        print("0. Exit")
        usr_input = int(input())
        if usr_input == 0:
            return 0
        elif usr_input == 5:
            print("You have successfully logged out!")
            return 5
        elif usr_input == 1:
            print()
            print("Balance: {}".format(current_user.balance))
            print()
        elif usr_input == 2:
            print("Enter income: ")
            amount = int(input())
            if amount >= 0:
                current_user.balance += amount
                current_user.update_balance()
                print("Income was added!")
        elif usr_input == 3:
            print("Transfer")
            print("Enter card number: ")
            number = input()
            if validate_card(number):
                if number == current_user.card_number:
                    print("You can't transfer money to the same account!")
                else:
                    query = "SELECT * FROM card WHERE number = {};".format(number)
                    cursor.execute(query)
                    connection.commit()
                    result = cursor.fetchone()
                    if result is not None:
                        print("Enter how much money you want to transfer:")
                        money = int(input())
                        if money > current_user.balance:
                            print("Not enough money!")
                        else:
                            current_user.balance -= money
                            current_user.update_balance()
                            query = "UPDATE card SET balance = balance + {} WHERE number = {};".format(money, number)
                            cursor.execute(query)
                            connection.commit()
                            print("Success!")
                    else:
                        print("Such a card does not exist.")
            else:
                print("Probably you made a mistake in the card number. Please try again!")
        elif usr_input == 4:
            current_user.delete_account()
            print("The account has been closed!")


def create_table():
    # query = "CREATE DATABASE card;"
    query = "CREATE TABLE IF NOT EXISTS card(" \
            "   id INTEGER PRIMARY KEY AUTOINCREMENT," \
            "   number TEXT," \
            "   pin TEXT," \
            "   balance INTEGER DEFAULT 0" \
            ");"
    cursor.execute(query)
    connection.commit()


def create_connection():
    try:
        global connection, cursor
        connection = sqlite3.connect('card.s3db')
        cursor = connection.cursor()
    except Error as e:
        print(e)
    finally:
        create_table()
        # table()
        while True:
            print("1. Create an account")
            print("2. Log into account")
            print("0. Exit")
            usr_input = int(input())
            if usr_input == 0:
                break
            elif usr_input == 1:
                User(True)
            elif usr_input == 2:
                ret = login()
                if ret == -1:
                    continue
                else:
                    cycle_ret = user_cycle()
                    if cycle_ret == 0:
                        break
                    elif cycle_ret == 5:
                        continue
        connection.close()


create_connection()
