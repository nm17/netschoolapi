import netschoolapi
from examples.preparation.preparation import run_main
from examples.preparation.utils import pprint


async def main(client: netschoolapi.NetSchoolAPI):
    print("Overdue:")
    pprint(await client.overdue())


run_main(main)
