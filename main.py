from web3 import Web3
from web3.middleware import geth_poa_middleware
from contract_info import abi, contract_address
import re
import getpass

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

contract = w3.eth.contract(address=contract_address, abi=abi)


def login():
    try:
        public_key = input("Введите публичный ключ: ")
        password = getpass.getpass("Введите пароль: ")
        w3.geth.personal.unlock_account(public_key, password)
        return public_key
    except Exception as e:
        print(f"Ошибка авторизации: {e}")
        return None


def is_strong_password(password):
    if len(password) < 12:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*()-+=]', password):
        return False
    return True


def register():
    while True:
        print("Условия для хорошего пароля: \n 1 - Минимум 12 символов\n 2 - Минимум 1 Заглавная буква\n 3 - Минимум 1 Строчная буква\n 4 - Минимум 1 цифра\n 5 - Минимум 1 спец.символ\n")
        password = getpass.getpass("Новый пароль: ")
        if is_strong_password(password):
            break
        else:
            print("Пароль слишком слабый. Убедитесь, что он содержит как минимум 12 символов, включая заглавные и строчные буквы, цифры и специальные символы.")
    try:
        account = w3.geth.personal.new_account(password)
        print(f"Публичный ключ: {account}")
    except Exception as e:
        print(f"Ошибка регистрации: {e}")


def send_eth(account):
    try:
        value = int(input("Введите количество эфира для отправки: "))
        tx_hash = contract.functions.toPay(account).transact({
            "from": account,
            "value": value,
        })
        print(f"Транзакция {tx_hash.hex()} отправлена")
    except ValueError:
        print("Ошибка: неверное значение")
    except Exception as e:
        print(f"Ошибка отправки эфира: {e}")


def get_balance(account):
    try:
        balance = contract.functions.getBalance().call({
            'from': account
        })
        print(f"Ваш баланс на смарт-контракта: {balance}")
    except Exception as e:
        print(f"Ошибка получения баланса: {e}")


def withdraw(account):
    try:
        amount = int(input("Введите количество эфира для вывода: "))
        tx_hash = contract.functions.withdrawFunds(amount).transact({
            'from': account,
        })
        print(f"Транзакция {tx_hash.hex()} отправлена")
    except ValueError:
        print("Ошибка: неверное значение")
    except Exception as e:
        print(f"Ошибка снятия средств: {e}")


def create_property(account):
    try:
        area = int(input("Введите площадь недвижимости: "))
        property_address = input("Введите адрес недвижимости: ")
        property_type = input("Введите тип недвижимости: ")
        tx_hash = contract.functions.createProperty(area, property_address, property_type).transact({
            'from': account
        })
        print(f"Транзакция {tx_hash.hex()} отправлена для создания недвижимости")
    except ValueError:
        print("Ошибка: неверное значение")
    except Exception as e:
        print(f"Ошибка создания недвижимости: {e}")


def create_listing(account):
    try:
        property_id = int(input("Введите ID недвижимости, для которой создается объявление: "))
        price = int(input("Введите цену продажи: "))
        tx_hash = contract.functions.createListing(property_id, price).transact({
            'from': account
        })
        print(f"Транзакция {tx_hash.hex()} отправлена для создания объявления")
    except ValueError:
        print("Ошибка: неверное значение")
    except Exception as e:
        print(f"Ошибка создания объявления: {e}")


def change_property_status(account):
    try:
        property_id = int(input("Введите ID недвижимости, для которой нужно изменить статус: "))
        new_status = bool(int(input("Выберите новый статус (0 - Неактивен, 1 - Активен): ")))
        tx_hash = contract.functions.changePropertyStatus(property_id, new_status).transact({
            'from': account
        })
        print(f"Транзакция {tx_hash.hex()} отправлена для изменения статуса недвижимости")
    except ValueError:
        print("Ошибка: неверное значение")
    except Exception as e:
        print(f"Ошибка изменения статуса недвижимости: {e}")


def change_listing_status(account):
    try:
        listing_id = int(input("Введите ID объявления, для которого нужно изменить статус: "))
        new_status = bool(int(input("Выберите новый статус (0 - Закрыто, 1 - Открыто): ")))
        tx_hash = contract.functions.changeListingStatus(listing_id, new_status).transact({
            'from': account
        })
        print(f"Транзакция {tx_hash.hex()} отправлена для изменения статуса объявления")
    except ValueError:
        print("Ошибка: неверное значение")
    except Exception as e:
        print(f"Ошибка изменения статуса объявления: {e}")


def get_properties_info():
    try:
        properties = contract.functions.getAllProperties().call()
        print("Информация о недвижимости:")
        for property in properties:
            print(f"ID: {property[0]}, Площадь: {property[1]}, Адрес: {property[2]}, Владелец: {property[3]}, Тип: {property[4]}, Статус: {'Активен' if property[5] else 'Неактивен'}")
    except Exception as e:
        print(f"Ошибка получения информации о недвижимости: {e}")


def get_listings_info():
    try:
        listings = contract.functions.getAllListings().call()
        print("Текущие объявления о продаже недвижимости:")
        for listing in listings:
            print(f"ID: {listing[0]}, Продавец: {listing[1]}, Покупатель: {listing[2]}, Цена: {listing[3]}, Недвижимость: {listing[4]}, Дата создания: {listing[5]}, Статус: {'Открыто' if listing[6] else 'Закрыто'}")
    except Exception as e:
        print(f"Ошибка получения информации о текущих объявлениях: {e}")


def purchase_property(account):
    try:
        listing_id = int(input("Введите ID объявления, чтобы купить недвижимость: "))
        tx_hash = contract.functions.purchaseProperty(listing_id).transact({
            'from': account,
            'value': 0
        })
        print(f"Транзакция {tx_hash.hex()} отправлена для покупки недвижимости")
    except ValueError:
        print("Ошибка: неверное значение")
    except Exception as e:
        print(f"Ошибка покупки недвижимости: {e}")


def main():
    account = ""
    while True:
        if account == "" or account is None:
            choice = int(input("Выберите: \n1 - Авторизация \n2 - Регистрация \n3 - Выход\nНомер операции: "))
            match choice:
                case 1:
                    account = login()
                case 2:
                    register()
                case 3:
                    print("Успешный выход!")
                    exit()
                case _:
                    print("Выберите от 1 до 3")
        else:
            choice = int(input("Выберите: \n1 - Отправить эфиры \n2 - Посмотреть баланс смарт-контракта \n3 - Посмотреть баланс аккаунта \n4 - Снять средства \n5 - Создание недвижимости \n6 - Создание объявления \n7 - Изменение статуса недвижимости \n8 - Изменение статуса объявления \n9 - Покупка недвижимости \n10 - Информация о недвижимости \n11 - Информация о объявлениях \n12 - Выход\nНомер операции: "))
            match choice:
                case 1:
                    send_eth(account)
                case 2:
                    get_balance(account)
                case 3:
                    print(f"Баланс аккауната: {w3.eth.get_balance(account)}")
                case 4:
                    withdraw(account)
                case 5:
                    create_property(account)
                case 6:
                    create_listing(account)
                case 7:
                    change_property_status(account)
                case 8:
                    change_listing_status(account)
                case 9:
                    purchase_property(account)
                case 10:
                    get_properties_info()
                case 11:
                    get_listings_info()
                case 12:
                    print("Успешный выход из аккаунта!")
                    account = ""
                case _:
                    print("Выберите от 1 до 12")


if __name__ == "__main__":
    main()

