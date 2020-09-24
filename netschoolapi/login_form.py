import httpx

ALL_LOGIN_ARGS = ("country", "state", "province", "city", "func", "school")

LOGIN_FORM_QUEUE = {
    "countries": "cid",
    "states": "sid",
    "provinces": "pid",
    "cities": "cn",
    "funcs": "sft",
    "schools": "scid",
}

ALL_LOGIN_KWARGS = {
    ALL_LOGIN_ARGS[i[0]]: i[1] for i in enumerate(LOGIN_FORM_QUEUE.keys())
}
# Должен получится такой словарь -> {"country": "countries", "state": "states", "province": "provinces", ... }


class LoginForm:
    def __init__(self, url, client=httpx.AsyncClient()):
        assert isinstance(url, str)
        self.url = url
        self.client = client

    @staticmethod
    def get_prepare_data(prepare_data, login_kwargs, k, v):
        """
        :param prepare_data: кладем лист с словарями -> [{}, ...]
        :param login_kwargs: всегда кладем login_kwargs
        :param k: Из ALL_LOGIN_KWARGS достаем название ключа ("country")
        :param v: Из ALL_LOGIN_KWARGS достаем значение ключа ("countries")
        """

        for i in prepare_data:  # Итерируем список на словари -> [{}, ...]
            if login_kwargs[k] in i["name"]:
                return LOGIN_FORM_QUEUE[v].upper(), i["id"]

    async def get_prepare_form_data(self):
        """
        Получить тот большой JSON файлик и перевести в наш удобный dict
        """
        async with self.client as client:
            resp = await client.get(self.url.rstrip("/") + "/webapi/prepareloginform")
            assert resp.status_code == 200

        return resp.json()

    async def get_login_data(self, last_keys):
        """
        Пример должного запроса:
        https://edu.admoblkaluga.ru:444/webapi/loginform?cid=2&sid=122&pid=36&cn=2025&sft=2&LASTNAME=sft
        :parameter last_keys: это словарь result в get_login_form
        """
        async with self.client as client:
            last_keys = last_keys.copy()
            last_keys["LASTNAME"] = list(last_keys.keys())[-1]
            resp = await client.get(self.url.rstrip("/") + "/webapi/loginform", params=last_keys)
            assert resp.status_code == 200

        return resp.json()

    async def get_login_form(self, **login_kwargs):

        prepare_data = await self.get_prepare_form_data()

        result = {}

        for k, v in ALL_LOGIN_KWARGS.items():
            # Смотрите ALL_LOGIN_KWARGS чтобы понять что мы итерируем...

            if isinstance(login_kwargs.get(k), str):
                data = self.get_prepare_data(prepare_data[v], login_kwargs, k, v)

                if data is not None:
                    result[data[0]] = data[1]

                else:
                    adv_prepare_data = await self.get_login_data(result)
                    data = self.get_prepare_data(adv_prepare_data["items"], login_kwargs, k, v)
                    assert data is not None, "Вы ошиблись в параметрах функции"
                    result[data[0]] = data[1]

            else:

                try:
                    adv_prepare_data = await self.get_login_data(result)
                    result[LOGIN_FORM_QUEUE[v].upper()] = adv_prepare_data["items"][0]["id"]
                except:
                    login = LOGIN_FORM_QUEUE[v]
                    result[login.upper()] = prepare_data[login]

        return result
