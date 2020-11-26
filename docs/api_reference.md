# АПИ «Сетевого города»

Эта вкладка для людей, которым уже не хватает просто netschoolapi. Здесь приводится небольшая справка о «внутренностях Сетевого города», его бэк-енде.

## WebAPI

WebAPI — способ общения с «Сетевым городом», которым пользуется netschoolapi. Это часть сайта, к котрой нет доступа через фронт-енд, но к нему можно посылать запросы, что и делает netschoolapi. У него нет официальной документации. Всё, что здесь представлено — последствия долгого ресёрча.

### Запросы к WebAPI

Схема для `GET`-, `POST`- запросов к WebAPI: `<URL СГО>/webapi/<METHOD>`. Мы опустим прочие части и будем писать лишь `<METHOD>`. Параметры посылаются как часть схемы, ответы возвращаются в формате JSON.

NB: Тут приводятся только запросы, которые может сделать обычный ученик. Всего методов WebAPI бесчисленное множество, с их помощью можно вертеть дневником как вздумается.

## References

Все запросы с префиксом `references` делаются GET-запросом и не требуют никаких прав.

### Образовательные организации

#### [references/eoRefs](responses/references/eoRefs.json)

Этим запросом можно получить всё об образовательных организациях. Запросы ниже возвращают более узкую информацию.

#### [references/functypes](responses/references/functypes.json)

Образовательные организации бывают четырёх основных типов:

1. Дошкольного образования
1. Общего
1. Дополнительного
1. Прочие

Первые три можно увидеть, когда вы входите на сайт: «Вход для учащихся» — «Тип ОО». netschoolapi используется только для учреждений общего образования.

Ещё существует «Управление Образованием», но ни одной организации с таким типом нет.

#### [references/eotypes](responses/references/eotypes.json)

Метод возвращает все возможные образовательные организации, разделённые на типы.

#### [references/eoforms](responses/references/eoforms.json)

ID ОО подряд.

#### [references/eolegalforms](responses/references/eolegalforms.json)

ЧТО ЭТО БЛЯТЬ?

#### [references/eolegalforms/fz83](responses/references/eolegalforms_fz83.json)

А ЧТО ЭТО БЛЯТЬ? Федеральный закон № 83 и что-то ещё, сука

#### [references/douGroupTypes](responses/references/dougrouptypes.json)

Типы общественных организаций для детей дошкольного возраста.


### Пользователи

#### [references/roles](responses/references/roles.json)

Типы пользователей.

#### [references/dwRoles](responses/references/dwRoles.json)

Хз чё это

#### [references/familyMemberTypes](responses/references/familyMemberTypes.json)

Члены семьи.

#### [references/familyObserveTypes](responses/references/familyObserveTypes.json)

Учёты, на которых может находиться семья.

### Прочее

#### [references/subjectFipi](responses/references/subjectFipi.json)

Предметы, согласно программе ФИПИ.

## UserContext

Здесь приведены не все запросы. Некоторые требуют дополнительных параметров или привелегий, некоторые возвращают мусор, вроде null или пустых массивов.

#### [context](responses/usercontext/context.json)

NB: Метод требует авторизации. Неавторизованный пользователь получит «ошибку доступа».

В netschoolapi метод используется для получения userId и yearId (!!!!schoolYearId (ссылка), не путать с globalYearId (ссылка)!!!!!).

#### [context/activeSessions](responses/usercontext/activeSessions.json)

Активные пользователи.

#### [context/students](responses/usercontext/students.json)

Ученики, чьи дневники можно посмотреть. Интересно, только если вы — родитель и у вас несколько детей.

#### [context/years](responses/usercontext/years.json)

Год, даты его начала и окончания и id этого года для конкретной школы.

## Accounts

#### [auth/account](responses/accounts/account.json)

Немного бесполезной информации о пользователе.

## Announcements

#### announcemets

Об объявлениях написано [здесь](/examples#_3).

Параметры:
- take (default: 5) — Количество возвращаемых объявлений, от новых к старым.
- skip (default: -1) — Сколько объявлений пропустить.
