import netschoolapi
from examples.preparation import utils
from preparation.preparation import run_main


async def main(client: netschoolapi.NetSchoolAPI):
    print("Diary:")
    diary = await client.diary()
    utils.pprint(diary)
    for day in diary.schedule:
        for lesson in day.lessons:
            for assignment in lesson.assignments:
                attachments = await client.attachments(assignment)
                if attachments:
                    print(
                        f"Some attachments found on day {day.day} on "
                        f"{lesson.subject} homework: {attachments}"
                    )
                    # You can also download them using
                    # .download_attachment() or .download_attachment_as_bytes()


run_main(main)
