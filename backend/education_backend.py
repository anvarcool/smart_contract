from web3 import Web3
import json
import click

# Загрузка ABI контракта
with open('C:/Python_3.11/Projects/education/artifacts/contracts/Education_system.sol/Education_system.json', 'rb') as f:
    conf = json.load(f)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Проверка соединения
if not w3.is_connected():
    raise ConnectionError("Ошибка подключения к блокчейну")

# Установка ABI и адреса контракта
abi = conf['abi']
address = '0x5FbDB2315678afecb367f032d93F642f64180aa3'
education = w3.eth.contract(address=address, abi=abi)



def send_signed_transaction(account, tx):
    """Подписывает и отправляет транзакцию, возвращает receipt."""
    nonce = w3.eth.get_transaction_count(account.address)
    tx['nonce'] = nonce
    tx['gas'] = 3000000
    tx['maxFeePerGas'] = w3.to_wei('50', 'gwei')
    tx['maxPriorityFeePerGas'] = w3.to_wei('2', 'gwei')
    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)



@click.group()
def cli():
    pass


@cli.command()
@click.argument('person', type=str)
@click.argument('isteacher', type=click.Choice(['true', 'false']))
@click.argument('private_key', type = str)
def add_person(person, isteacher, private_key):
    account = w3.eth.account.from_key(private_key)
    is_teacher = (isteacher == 'true')
    try:
        tx = education.functions.add_person(person, is_teacher).build_transaction({'from': account.address})
        receipt = send_signed_transaction(account, tx)
        click.echo(f"Добавлен {'преподаватель' if is_teacher else 'студент'}, хэш транзакции: {receipt.transactionHash.hex()}")
    except Exception as e:
        click.echo(f"Ошибка транзакции: {e}")

@cli.command()
@click.argument('course_name', type= str)
@click.argument('private_key', type = str)
def create_course(course_name, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        tx = education.functions.create_course(course_name).build_transaction({'from': account.address})
        receipt = send_signed_transaction(account, tx)
        click.echo(f"Создан курс {course_name}, хэш транзакции: {receipt.transactionHash.hex()}")

    except Exception as e:
        click.echo(f"Ошибка транзакции: {e}")


@cli.command()
@click.argument('teacher', type=str)
@click.argument('course_name', type=str)
@click.argument('private_key', type = str)

def define_course_teachers(teacher, course_name, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        tx = education.functions.define_course_teachers(teacher, course_name).build_transaction({'from': account.address})
        receipt = send_signed_transaction(account, tx)
        click.echo(f"на курс {course_name} добавлен преподаватель, хэш транзакции: {receipt.transactionHash.hex()}")

    except Exception as e:
        click.echo(f"Ошибка транзакции: {e}")

@cli.command()
@click.argument('course_name', type=str)
@click.argument('private_key', type = str)

def attend_course(course_name, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        tx = education.functions.attend_course(course_name).build_transaction({'from': account.address})
        receipt = send_signed_transaction(account, tx)
        click.echo(f"Вы встали в очередь на курс {course_name}, хэш транзакции: {receipt.transactionHash.hex()}")
    except Exception as e:
        click.echo(f"Ошибка транзакции: {e}")

@cli.command()
@click.argument('student', type=str)
@click.argument('course_name', type=str)
@click.argument('private_key', type = str)

def approve_student(student, course_name, private_key):
    try: 
        account = w3.eth.account.from_key(private_key)
        tx = education.functions.approve_student(student, course_name).build_transaction({'from': account.address})
        receipt = send_signed_transaction(account, tx)
        click.echo(f"Студент записан на курс {course_name}, хэш транзакции: {receipt.transactionHash.hex()}")

    except Exception as e:
        click.echo(f"Ошибка транзакции: {e}")
@cli.command()
@click.argument('course_name', type=str)
@click.argument('datetime', type=int)
@click.argument('private_key', type = str)

def add_lesson(course_name, datetime, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        tx = education.functions.add_lesson(course_name, datetime).build_transaction({'from': account.address})
        receipt = send_signed_transaction(account, tx)
        click.echo(f"добавлено занятие на курс {course_name} на время {datetime}, хэш транзакции: {receipt.transactionHash.hex()}")

    except Exception as e:
        click.echo(f"Ошибка транзакции: {e}")

@cli.command()
@click.argument('course_name', type=str)
@click.argument('datetime', type=int)
@click.argument('private_key', type = str)

def remove_lesson(course_name, datetime, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        tx = education.functions.remove_lesson(course_name, datetime).build_transaction({'from': account.address})
        receipt = send_signed_transaction(account, tx)
        click.echo(f"удалено занятие на курсе {course_name} на время {datetime}, хэш транзакции: {receipt.transactionHash.hex()}")

    except Exception as e:
        click.echo(f"Ошибка транзакции: {e}")

@cli.command()
@click.argument('course_name', type=str)
@click.argument('datetime_old', type=int)
@click.argument('datetime_new', type=int)
@click.argument('private_key', type = str)

def edit_lesson(course_name, datetime_old, datetime_new, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        tx = education.functions.edit_lesson(course_name, datetime_old, datetime_new).build_transaction({'from': account.address})
        receipt = send_signed_transaction(account, tx)
        click.echo(f"изменено время занятия на курсе {course_name} с {datetime_old} на {datetime_new}, хэш транзакции: {receipt.transactionHash.hex()}")


    except Exception as e:
        click.echo(f"Ошибка транзакции: {e}")

@cli.command()
@click.argument('person', type=str)
@click.argument('start_dt', type=int)
@click.argument('end_dt', type=int)
def check_persons_schedule(person, start_dt, end_dt):
    try:
        result = education.functions.check_persons_schedule(person, start_dt, end_dt).call()
        print('расписание:', result)

    except Exception as e:
        click.echo(f"Ошибка вывода: {e}")

@cli.command()
@click.argument('course_name', type=str)
@click.argument('start_dt', type=int)
@click.argument('end_dt', type=int)
def check_course_schedule(course_name, start_dt, end_dt):
    try:
        result = education.functions.check_course_schedule(course_name, start_dt, end_dt).call()
        print(f'расписание курса {course_name}:', result)

    except Exception as e:
        click.echo(f"Ошибка вывода: {e}")

@cli.command()
@click.argument('student', type=str)
@click.argument('course_name', type=str)
@click.argument('private_key', type = str)

def student_presence(student, course_name, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        tx = education.functions.student_presence(student, course_name).build_transaction({'from': account.address})
        receipt = send_signed_transaction(account, tx)
        click.echo(f"отметили студента на курсе {course_name}, хэш транзакции: {receipt.transactionHash.hex()}")

    except Exception as e:
        click.echo(f"Ошибка вывода: {e}")
    

@cli.command()
@click.argument('student', type=str)
@click.argument('course_name', type=str)
@click.argument('date', type=int)
@click.argument('mark', type=int)
@click.argument('private_key', type = str)

def mark_student(student, course_name, date, mark, private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        tx = education.functions.mark_student(student, course_name, date, mark).build_transaction({'from': account.address})
        receipt = send_signed_transaction(account, tx)
        click.echo(f"поставлена оценка {mark} студенту на курсе {course_name} на дату {date}, хэш транзакции: {receipt.transactionHash.hex()}")

    
    except Exception as e:
        click.echo(f"Ошибка вывода: {e}")

@cli.command()
@click.argument('person', type=str)
@click.argument('start_dt', type=int)
@click.argument('end_dt', type=int)

def check_person_marks(person, start_dt, end_dt):
    try:
        result =  education.functions.check_person_marks(person, start_dt, end_dt).call()
        print('оценки:', result)

    except Exception as e:
        click.echo(f"Ошибка вывода: {e}")

@cli.command()
@click.argument('course_name', type=str)
@click.argument('start_dt', type=int)
@click.argument('end_dt', type=int)

def check_course_marks(course_name, start_dt, end_dt):
    try:
        result =  education.functions.check_course_marks(course_name, start_dt, end_dt).call()
        print(f'оценки на курсе {course_name}:', result)
    
    except Exception as e:
        click.echo(f"Ошибка вывода: {e}")

@cli.command()
@click.argument('student', type=str)
def student_statistics(student):
    try:
        result =  education.functions.student_statistics(student).call()
        print('статистика по студенту:', result)
    
    except Exception as e:
        click.echo(f"Ошибка вывода: {e}")

@cli.command()
@click.argument('course_name', type=str)
def results_getter(course_name):
    try:
        result =  education.functions.results_getter(course_name).call()
        print(f'статистика по курсу {course_name}:', result)
    
    except Exception as e:
        click.echo(f"Ошибка вывода: {e}")

cli()
