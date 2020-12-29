import secrets
import sqlite3
import string


class BankingSystem:
    iin = '400000'

    def __init__(self):
        self.logged_in = False
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.create_table()
        self.menu()

    def create_table(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS card ('
                         '   id INTEGER PRIMARY KEY AUTOINCREMENT,'
                         '   number TEXT,'
                         '   pin TEXT,'
                         '   balance INTEGER DEFAULT 0'
                         ');')
        self.conn.commit()

    def create_account(self):
        account = self.Account(self)
        print('Your card has been created')
        print('Your card number:')
        print(account.card_number)
        print('Your card pin:')
        print(account.pin)

    def login(self):
        card_num_input = input('Enter your card number:')
        pin_input = input('Enter your pin:')
        self.cur.execute('SELECT number, pin'
                         '  FROM card;')
        logins = self.cur.fetchall()
        if (card_num_input, pin_input) in logins:
            print('You have successfully logged in!')
            self.logged_in = True
            self.account_menu(card_num_input)
        else:
            print('Wrong card number or pin!')

    def menu(self):
        while not self.logged_in:
            choice = input('''
            1. Create an account
            2. Log into account
            0. Exit
            ''')
            if choice == '1':
                self.create_account()
            elif choice == '2':
                self.login()
            elif choice == '0':
                print('Bye!')
                self.cur.close()
                self.conn.close()
                exit()

    def account_menu(self, card_number):
        while self.logged_in:
            choice = input('''
            1. Balance
            2. Add income
            3. Do transfer
            4. Close account
            5. Log out
            0. Exit
            ''')
            if choice == '1':
                self.print_balance(card_number)
            elif choice == '2':
                self.add_income(card_number, input('Enter income:'))
                print('Income was added!')
            elif choice == '3':
                self.transfer(card_number)
            elif choice == '4':
                self.close_account(card_number)
            elif choice == '5':
                self.logged_in = False
                print('You have successfully logged out!')
            elif choice == '0':
                print('Bye!')
                self.cur.close()
                self.conn.close()
                exit()

    def balance(self, card_number):
        self.cur.execute(f'SELECT balance'
                         f'  FROM card'
                         f' WHERE number = "{card_number}";')
        return int(self.cur.fetchone()[0])

    def print_balance(self, card_number):
        print(f'Balance: {self.balance(card_number)}')

    def add_income(self, card_number, income):
        self.cur.execute(f'UPDATE card'
                         f'   SET balance = balance + {income}'
                         f' WHERE number = "{card_number}";')
        self.conn.commit()

    def transfer(self, card_number):
        print('Transfer')
        other_card_num = input('Enter card number:')
        if other_card_num == card_number:
            print("You can't transfer money to the same account!")
        elif not self.checksum_correct(other_card_num):
            print('Probably you made a mistake in the card number. Please try again!')
        elif not self.card_exists(other_card_num):
            print('Such a card does not exist.')
        else:
            transfer_amount = int(input('Enter how much money you want to transfer:'))
            if transfer_amount > self.balance(card_number):
                print('Not enough money!')
            else:
                self.add_income(card_number, -transfer_amount)
                self.add_income(other_card_num, transfer_amount)
                print('Success!')

    def checksum_correct(self, card_number):
        return card_number[-1] == self.Account.checksum(self, card_number[:6], card_number[6:-1])

    def card_exists(self, card_number):
        self.cur.execute('SELECT number'
                         '  FROM card;')
        return card_number in [result[0] for result in self.cur.fetchall()]

    def close_account(self, card_number):
        self.cur.execute(f'DELETE FROM card'
                         f' WHERE number = "{card_number}";')
        self.conn.commit()
        print('The account has been closed!')

    class Account:
        card_number = ''
        pin = ''

        def __init__(self, banking_system):
            self.banking_system = banking_system
            self.conn = self.banking_system.conn
            self.cur = self.banking_system.cur
            self.acc_number = self.new_acc_number()
            self.card_number = (self.banking_system.iin + self.acc_number
                                + self.checksum(self, self.banking_system.iin, self.acc_number))
            self.pin = self.new_pin(self)
            self.cur.execute(f'INSERT INTO card (number, pin)'
                             f'VALUES ({self.card_number}, {self.pin});')
            self.conn.commit()

        def new_acc_number(self):
            acc_number = ''
            self.cur.execute('SELECT substr(number, 7, 9)'
                             '  FROM card;')
            acc_nums = [result[0] for result in self.cur.fetchall()]
            acc_num_unique = False
            while not acc_num_unique:
                acc_number = ''.join(secrets.choice(string.digits) for _ in range(9))
                if acc_number not in acc_nums:
                    acc_num_unique = True
            return acc_number

        @staticmethod
        def checksum(self, iin, acc_number):
            # Luhn algorithm
            digits = [int(digit) for digit in list(iin + acc_number)]
            for i in range(len(digits)):
                if (i + 1) % 2:
                    digits[i] *= 2
                if digits[i] > 9:
                    digits[i] -= 9
            return str(-sum(digits) % 10)

        @staticmethod
        def new_pin(self):
            return ''.join(secrets.choice(string.digits) for _ in range(4))


banking_system = BankingSystem()