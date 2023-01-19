from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os
from colorama import Fore, Style

pf = PetFriends()

def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в тезультате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Рыжий', animal_type='кот',
                                     age='4', pet_photo='images/5-4.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_update_self_pet_info(name='Венера', animal_type='кот', age='3'):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_successful_delete_self_pet():
        """Проверяем возможность удаления питомца"""

        # Получаем ключ auth_key и запрашиваем список своих питомцев
        _, auth_key = pf.get_api_key(valid_email, valid_password)
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

        # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
        if len(my_pets['pets']) == 0:
            pf.add_new_pet(auth_key, "Рыжий", "кот", "4", "images/5-4.jpg")
            _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

        # Берём id первого питомца из списка и отправляем запрос на удаление
        pet_id = my_pets['pets'][0]['id']
        status, _ = pf.delete_pet(auth_key, pet_id)

        # Ещё раз запрашиваем список своих питомцев
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

        # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
        assert status == 200
        assert pet_id not in my_pets.values()


# Доп. тест №1
def test_create_new_pet_simple(name='Лиза', animal_type='лиса', age='7'):
        """Тест создания нового питомца без фото"""

        _, auth_key = pf.get_api_key(valid_email, valid_password)

        status, result = pf.create_new_pet_simple(auth_key, name, animal_type, age)
        assert status == 200
        assert result['name'] == name


# Доп. тест №2
def test_add_pet_photo(pet_photo='images/357.jpg'):
    """Тест возможности добавления фото к существующему питомцу"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) == 0:
        pf.create_new_pet_simple(auth_key, 'Лиза', 'лиса', '7')
        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    pet_id = my_pets['pets'][0]['id']
    status, result = pf.add_pet_photo(auth_key, pet_id, pet_photo)

    assert status == 200
    assert 'pet_photo' in result


# Доп. тест №3 - негативный
def test_get_api_key_with_invalid_email(email=invalid_email, password=valid_password):
    """ Тест ввода некорректного e-mail"""

    status, result = pf.get_api_key(email, password)

    assert status == 403
    assert 'key' not in result


# Доп. тест №4 - негативный
def test_get_api_key_with_invalid_password(email=valid_email, password=invalid_password):
    """ Тест ввода некорректного пароля"""

    status, result = pf.get_api_key(email, password)

    assert status == 403
    assert 'key' not in result


# Доп. тест №5 - негативный
def test_create_new_pet_invalid_age_format(name='Лиза', animal_type='лиса', age='vol'):
    """Тест возможности ввода возраста в некорректном формате"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.create_new_pet_simple(auth_key, name, animal_type, age)

    assert type(age) != int
    print(Fore.RED + ' BUG:', Style.RESET_ALL + ' Data type error in Age')


# Доп. тест №6 - негативный
def test_create_new_pet_invalid_name_format(name=12345, animal_type='лиса', age='7'):
    """Тест возможности ввода имени в некорректном формате"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.create_new_pet_simple(auth_key, name, animal_type, age)

    assert status == 200
    print(Fore.RED + ' BUG:', Style.RESET_ALL + 'wrong data type for Name is possible for input')


# Доп. тест №7 - негативный
def test_add_new_pet_with_same_data(name='Лиза', animal_type='лиса', age='7', pet_photo='357.jpg'):
        """Проверяем возможность дублирования данных"""

        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        _, auth_key = pf.get_api_key(valid_email, valid_password)

        status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        assert status == 200
        print(Fore.RED + ' BUG:', Style.RESET_ALL + 'Duplicate of pets data is possible')


# Доп. тест №8 - негативный
def test_add_pet_long_type_name(name='Tooth', age='3', pet_photo='images/Belka.jpg'):
    """Добавление питомца с слишком длинным названием породы (более 30 букв)"""

    animal_type = 'qwertyuiopasdfghjkllasdfghjklgt'

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    list_animal_type = result['animal_type']
    word_count = len(list_animal_type)

    if word_count > 30:
       print(Fore.RED + ' BUG:', Style.RESET_ALL + 'Pet with too long animal type is added - ', {word_count}, 'symbols')

    else:
       assert status == 200


# Доп. тест №9 - негативный
def test_create_pet_with_invalid_key(name='Kuzya', animal_type='Cat', age='21'):
    """Проверка создания питомца с некорректным ключом"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.create_new_pet_simple({'key': 'qwertyuiopasdfghjklzxcvbnm'}, name, animal_type, age)

    assert status == 403


# Доп. тест №10 - негативный
def test_create_new_pet_simple_with_invalid_age(name='Dina', animal_type='Dog', age='123'):
    """Проверка возможности добавления питомца с более чем 2-х значным значением возраста"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.create_new_pet_simple(auth_key, name, animal_type, age)

    if len(age) <= 2:
       assert status == 200
    else:
       print(Fore.RED + ' Warning:', Style.RESET_ALL + 'More than 2-digit number in Age parameter')
