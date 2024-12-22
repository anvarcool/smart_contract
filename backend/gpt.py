from web3 import Web3
import json
import click

# Загрузка ABI
with open('C:/Python_3.11/Projects/education/artifacts/contracts/Education_system.sol/Education_system.json', 'rb') as f:
    conf = json.load(f)

# Установка соединения с блокчейном
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

if not w3.is_connected():
    raise ConnectionError("Ошибка подключения к блокчейну")

# Установка ABI и адреса контракта
abi = conf['abi']
address = '0x5FbDB2315678afecb367f032d93F642f64180aa3'
education = w3.eth.contract(address=address, abi=abi)

# Установка учетной записи по умолчанию
w3.eth.default_account = w3.eth.accounts[0]

@click.group()
def cli():
    """CLI для взаимодействия с контрактом Education System"""
    pass

@cli.command()
@click.argument('person', type=str)
@click.option('--isteacher', type=click.Choice(['true', 'false']), help="Роль пользователя: true (учитель), false (студент)")
def add_person(person, isteacher):
    is_teacher = isteacher == 'true'
    try:
        tx_hash = education.functions.add_person(person, is_teacher).transact({'from': w3.eth.default_account})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        click.echo(f"Пользователь добавлен, хэш транзакции: {receipt.transactionHash.hex()}")
    except Exception as e:
        click.echo(f"Ошибка транзакции: {e}")

@cli.command()
@click.argument('course_name', type=str)
def create_course(course_name):
    try:
        tx_hash = education.functions.create_course(course_name).transact({'from': w3.eth.default_account})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        click.echo(f"Курс создан, хэш транзакции: {receipt.transactionHash.hex()}")
    except Exception as e:
        click.echo(f"Ошибка транзакции: {e}")

@cli.command()
@click.argument('teacher', type=str)
@click.argument('course_name', type=str)
def define_course_teachers(teacher, course_name):
    try:
        tx_hash = education.functions.define_course_teachers(teacher, course_name).transact({'from': w3.eth.default_account})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        click.echo(f"Преподаватель назначен, хэш транзакции: {receipt.transactionHash.hex()}")
    except Exception as e:
        click.echo(f"Ошибка транзакции: {e}")

@cli.command()
@click.argument('course_name', type=str)
def attend_course(course_name):
    try:
        tx_hash = education.functions.attend_course(course_name).transact({'from': w3.eth.default_account})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        click.echo(f"Запись на курс выполнена, хэш транзакции: {receipt.transactionHash.hex()}")
    except Exception as e:
        click.echo(f"Ошибка транзакции: {e}")

@cli.command()
@click.argument('student', type=str)
@click.argument('course_name', type=str)
def approve_student(student, course_name):
    try:
        tx_hash = education.functions.approve_student(student, course_name).transact({'from': w3.eth.default_account})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        click.echo(f"Студент подтвержден, хэш транзакции: {receipt.transactionHash.hex()}")
    except Exception as e:
        click.echo(f"Ошибка транзакции: {e}")

# Пример обработки только чтения данных
@cli.command()
@click.argument('course_name', type=str)
@click.argument('start_dt', type=int)
@click.argument('end_dt', type=int)
def check_course_schedule(course_name, start_dt, end_dt):
    try:
        result = education.functions.check_course_schedule(course_name, start_dt, end_dt).call()
        click.echo(f"Расписание курса: {result}")
    except Exception as e:
        click.echo(f"Ошибка вызова функции: {e}")

cli()
