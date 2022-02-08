import netschoolapi
from examples.preparation.preparation import run_main
from examples.preparation.utils import pprint


async def main(client: netschoolapi.NetSchoolAPI):
    print("School info:")
    pprint(await client.school())


run_main(main)
