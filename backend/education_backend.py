from web3 import Web3
import json
import click

with open('C:/Python_3.11/Projects/education/artifacts/contracts/Education_system.sol/Education_system.json', 'rb') as f:
    conf = json.load(f)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Проверка соединения
if not w3.is_connected():
    raise ConnectionError("Ошибка подключения к блокчейну")

abi = conf['abi']

address = '0x5FbDB2315678afecb367f032d93F642f64180aa3'

education = w3.eth.contract(address=address, abi=abi)

w3.eth.default_account = w3.eth.accounts[0]

@click.group()
def cli():
    """CLI для взаимодействия с контрактом Education System"""
    pass

@cli.command()
@click.argument('person', type = str)
@click.argument('isteacher', type=click.Choice(['true', 'false']))
def add_person(person, isteacher):
    is_teacher = (isteacher == 'true')
    try:
        tx_hash = education.functions.add_person(person, is_teacher).transact({'from': w3.eth.default_account})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        click.echo(f"Пользователь добавлен, хэш транзакции: {receipt.transactionHash.hex()}")
    except Exception as e:
        click.echo(f"Ошибка транзакции: {e}")

@cli.command()
@click.argument('course_name', type=str)
def create_course(course_name):
    click.echo(education.functions.create_course(course_name).transact())

@cli.command()
@click.argument('teacher', type=str)
@click.argument('course_name', type=str)
def define_course_teachers(teacher, course_name):
    education.functions.define_course_teachers(teacher, course_name).transact()


@cli.command()
@click.argument('course_name', type=str)
def attend_course(course_name):
    education.functions.attend_course(course_name).transact()

@cli.command()
@click.argument('student', type=str)
@click.argument('course_name', type=str)
def approve_student(student, course_name):
    education.functions.approve_student(student, course_name).transact()

@cli.command()
@click.argument('datetime', type=int)
@click.argument('course_name', type=str)
def add_lesson(course_name, datetime):
    education.functions.add_lesson(course_name, datetime).transact()

@cli.command()
@click.argument('datetime', type=int)
@click.argument('course_name', type=str)
def remove_lesson(course_name, datetime):
    education.functions.remove_lesson(course_name, datetime).transact()

@cli.command()
@click.argument('datetime_old', type=int)
@click.argument('datetime_new', type=int)
@click.argument('course_name', type=str)
def edit_lesson(course_name, datetime_old, datetime_new):
    education.functions.edit_lesson(course_name, datetime_old, datetime_new).transact()

@cli.command()
@click.argument('person', type=str)
@click.argument('start_dt', type=int)
@click.argument('end_dt', type=int)
def check_persons_schedule(person, start_dt, end_dt):
    result = education.functions.check_persons_schedule(person, start_dt, end_dt).call()
    click.echo(result)

@cli.command()
@click.argument('course_name', type=str)
@click.argument('start_dt', type=int)
@click.argument('end_dt', type=int)
def check_course_schedule(course_name, start_dt,end_dt):
    result = education.functions.check_course_schedule(course_name, start_dt, end_dt).call()
    click.echo(result)

@cli.command()
@click.argument('student', type=str)
@click.argument('course_name', type=str)
def student_presence(student, course_name):
    try:
        education.functions.student_presence(student, course_name).transact()
    finally:
        print(1)

@cli.command()
@click.argument('student', type=str)
@click.argument('course_name', type=str)
@click.argument('date', type=int)
@click.argument('mark', type=int)
def mark_student(student, course_name, date, mark):
    education.functions.mark_student(student, course_name, date, mark).transact()

@cli.command()
@click.argument('person', type=str)
@click.argument('start_dt', type=int)
@click.argument('end_dt', type=int)
def check_person_marks(person, start_dt, end_dt):
    result =  education.functions.check_person_marks(person, start_dt, end_dt).call()
    click.echo(result)

@cli.command()
@click.argument('course_name', type=str)
@click.argument('start_dt', type=int)
@click.argument('end_dt', type=int)
def check_course_marks(course_name, start_dt, end_dt):
    result =  education.functions.check_course_marks(course_name, start_dt, end_dt).call()
    click.echo(result)

@cli.command()
@click.argument('student', type=str)
def student_statistics(student):
    result =  education.functions.student_statistics(student).call()
    click.echo(result)

@cli.command()
@click.argument('courseName', type=str)
def results_getter(courseName):
    result =  education.functions.results_getter(courseName).call()
    click.echo(result)

cli()
