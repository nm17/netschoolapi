# Введение
NetSchool API это клиент для "Сетевого города. Образование" написанный на Python.
Каждый урок является своим соответствующим объектом питона.
Возможно в будущем будет добавлена возможность следить за новыми оценками.

## Начало работы
Установите пакет через pip:

```
pip3 install netschoolapi
```

## Пример использования
### Пример входа в систему

```
import trio

from netschoolapi import NetSchoolAPI


async def main():
    api = NetSchoolAPI("http://sgo.cit73.ru/")
    await api.login("Иван", "Иван555", "МАОУ многопрофильный лицей №20")
    print(await api.get_form_data())

trio.run(main)

```