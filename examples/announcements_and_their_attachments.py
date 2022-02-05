import PIL.Image

import netschoolapi
from examples.preparation.preparation import run_main
from examples.preparation.utils import pprint


async def main(client: netschoolapi.NetSchoolAPI):
    print("Announcements:")
    announcements = await client.announcements()
    pprint(announcements)
    print()
    print("Now showing all images found in announcements.")
    for announcement in announcements:
        for attachment in announcement.attachments:
            if attachment.name.endswith((".png", ".jpg", ".jpeg")):
                image = await client.download_attachment_as_bytes(attachment)
                PIL.Image.open(image).show()


run_main(main)
