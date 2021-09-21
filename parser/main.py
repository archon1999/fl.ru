import time
import datetime
import traceback

import pytz

import config

from backend.models import Project as ProjectDB
from backend.models import Chapter as ChapterDB

from utils import get_last_projects_by_datetime, Project


def get_last_update_datetime():
    project = ProjectDB.projects.first()
    utc = pytz.UTC
    tz = pytz.timezone('Asia/Tashkent')
    if not project:
        dt = datetime.datetime.now()
        dt -= datetime.timedelta(minutes=5)
        return tz.localize(dt)

    return tz.normalize(project.published.replace(tzinfo=utc))


def migrate_to_db(new_projects: list[Project]):
    for project in sorted(new_projects, key=lambda project: project.published):
        if ProjectDB.projects.filter(article=project.article).exists():
            continue

        kwargs = project.__dict__.copy()
        kwargs.pop('chapters')
        project_db = ProjectDB.projects.create(**kwargs)

        for parent, child in project.chapters:
            chapter_db, success = ChapterDB.chapters.get_or_create(name=child)
            if success:
                parent = ChapterDB.chapters.create(name=parent)
                chapter_db.parent = parent
                chapter_db.save()

            project_db.chapters.add(chapter_db)


def main():
    while True:
        try:
            last_update_datetime = get_last_update_datetime()
            projects = get_last_projects_by_datetime(last_update_datetime)
            migrate_to_db(projects)
        except Exception:
            traceback.print_exc()
        finally:
            time.sleep(60)


if __name__ == "__main__":
    main()
