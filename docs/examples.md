# Примеры использования

## Шаблон проекта {#template}

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
        
        # Твой код живёт здесь


event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(main())
``` 

## Как я могу...

### ...получить дневник? {#get-diary}

```python
diary = await api.get_diary()

# diary = Diary(schedule=[week_day=WeekDay(day=1, lessons=[Lesson(subject='История', ...), ...]), ...], ...)
```
