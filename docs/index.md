# netschoolapi

Netschoolapi&nbsp;&mdash; Python-клиент для &laquo;Сетевого города&raquo;, созданный,
чтобы сделать жизнь проще. Теперь нет надобности
в&nbsp;сайте &laquo;Сетевого города&raquo;, потому, что дневник&nbsp;&mdash; больше, чем сайт.

Netschoolapi&nbsp;&mdash; то&nbsp;же, что и&nbsp;&laquo;Сетевой город&raquo;, но&nbsp;с&nbsp;ним в&nbsp;паре десяток строк кода
можно создать бота для&nbsp;ВК или Телеграма,
и&nbsp;пользоваться &laquo;электронным дневником&raquo; в&nbsp;любимом мессенджере.

!!! Warning
    netschoolapi не&nbsp;поддерживает &laquo;электронные дневники&raquo;.

## Установка {#install}

### Python {#python_install}

Netschoolapi требует установки [Python](https://www.python.org) не&nbsp;ниже версии 3.7.
В&nbsp;интернете тысячи гайдов по&nbsp;его установке.

### netschoolapi {#netschoolapi_install}

Netschoolapi устанавливается с&nbsp;помощью стандартного пакетного менеджера [pip](https://pip.pypa.io):
```shell
python -m pip install -U netschoolapi
```

## Начало работы {#get_started}

```python
import asyncio

from netschoolapi import NetSchoolAPI


async def main():
    async with NetSchoolAPI(
            'https://edu.admoblkaluga.ru:444/',  # Сайт «Сетевого города»
            'Ваш_Вася_Пупкин',  # Логин
            'с3кр37НыЙ_П4Р0Ль',  # Пароль от дневника
            # Адрес вашей школы. Вы видите его когда входите на сайт СГО
            # Указывайте всё как на сайте, буква к букве, это важно!
            (
                'Калужская обл',  # Область
                'Городской округ Обнинск',  # Округ или район
                'Обнинск, г.', # Населённый пункт.
                               # Хоть Обнинск и является единственной опцией,
                               # но его тоже нужно указывать
                'Общеобразовательная',  # Это тоже
                'МБОУ "СОШ "Технический лицей"',  # Образовательная организация
            ),
    ) as api:
        print(await api.get_diary())


event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(main())
```
