import datetime
import re
from urllib.parse import urljoin

import pytz
import requests
from bs4 import BeautifulSoup


BASE_URL = 'https://fl.ru'
PROJECTS_URL = urljoin(BASE_URL, 'projects')
MAX_PARSE_PAGE_NUMBER = 50


class Project():
    def __init__(self, article=str(), title=str(), description=str(),
                 budget=int(), deadline=None,
                 safe_deal=bool(), without_executor=bool, chapters=list(),
                 published=datetime.datetime.now(), url=str()):
        self.article = article
        self.title = title
        self.description = description
        self.budget = budget
        self.deadline = deadline
        self.safe_deal = safe_deal
        self.without_executor = without_executor
        self.chapters = chapters
        if not chapters:
            self.chapters = list()
        self.published = published
        self.url = url

    def __str__(self):
        return self.title


def get_html(url, params=None):
    response = requests.get(url, params)
    if response.ok:
        return response.text


def parse_project_article(project_url):
    return project_url.rstrip('/').split('/')[-2]


def text_to_date(text: str) -> datetime.date:
    try:
        day, month, year = map(int, text.split('.'))
        return datetime.date(day=day, month=month, year=year)
    except Exception:
        return None


def parse_project_published(text: str) -> datetime.datetime:
    if 'поднят' in text:
        text = text[text.find('поднят:')+8:len(text)-1]

    text = text[:18]
    date, time = text.split('|')
    day, month, year = map(int, date.split('.'))
    hour, minute = map(int, time.split(':'))
    published = datetime.datetime(day=day, month=month, year=year,
                                  hour=hour, minute=minute)
    published += datetime.timedelta(hours=2)
    return published


def parse_project_budget(text: str):
    try:
        text = text.removesuffix(r'руб/заказ').strip().replace(' ', '')
        return int(text)
    except Exception:
        return None


def parse_project_chapters(text: str):
    chapters = []
    for chapter in text.split(','):
        try:
            parent, child = chapter.split(' / ')
            chapters.append((parent.strip(), child.strip()))
        except ValueError:
            pass

    return chapters


def get_project(project_url):
    html = get_html(project_url)
    soup = BeautifulSoup(html, 'lxml')

    project = Project()
    project.article = parse_project_article(project_url)
    project.url = project_url

    title_tag = soup.find('h1', class_='b-page__title')
    project.title = title_tag.text.strip()

    description_tag = soup.find('div', id=f'projectp{project.article}')
    project.description = description_tag.text.strip()

    if soup.find(title='Оплата через Безопасную сделку'):
        project.safe_deal = True

    budget_tag = soup.find(string=re.compile('Бюджет:')).next_element
    project.budget = parse_project_budget(budget_tag.text.strip())

    if (deadline_string := soup.find(string=re.compile('Дедлайн:'))):
        deadline_tag = deadline_string.next_element
        project.deadline = text_to_date(deadline_tag.text.strip())

    if soup.find(string=re.compile('Исполнитель определен:')):
        project.without_executor = False
    else:
        project.without_executor = True

    if (published_string := soup.find(string=re.compile('Опубликован:'))):
        published_tag = published_string.next_element.next_element
        project.published = parse_project_published(published_tag.text.strip())
        tz = pytz.timezone('Asia/Tashkent')
        project.published = tz.localize(project.published)

    if (chapters_string := soup.find(string=re.compile('Разделы:'))):
        chapters_tag = chapters_string.next_element.next_element
        for parent, child in parse_project_chapters(chapters_tag.text):
            project.chapters.append((parent, child))

    return project


def parse_projects_by_datetime(html, dt: datetime.datetime) \
                               -> tuple[list[Project], bool]:
    soup = BeautifulSoup(html, 'lxml')
    projects = []
    for project_tag in soup.find_all(class_='b-post'):
        if 'topprjpay' in project_tag.get('class'):
            continue

        a_tag = project_tag.find('a', class_='b-post__link')
        project_url = urljoin(BASE_URL, a_tag.get('href'))
        project = get_project(project_url)
        if project.published < dt:
            return projects, True

        projects.append(project)

    return projects, False


def get_last_projects_by_datetime(dt: datetime) -> list[Project]:
    projects = []
    for page_number in range(1, MAX_PARSE_PAGE_NUMBER+1):
        params = {'kind': 1, 'page': page_number}
        html = get_html(PROJECTS_URL, params)
        new_projects, stop = parse_projects_by_datetime(html, dt)
        projects.extend(new_projects)
        if stop:
            break

    return projects


def parse_projects_by_count(html, count) \
                               -> tuple[list[Project], bool]:
    soup = BeautifulSoup(html, 'lxml')
    projects = []
    for project_tag in soup.find_all(class_='b-post'):
        if 'topprjpay' in project_tag.get('class'):
            continue

        a_tag = project_tag.find('a', class_='b-post__link')
        project_url = urljoin(BASE_URL, a_tag.get('href'))
        project = get_project(project_url)
        projects.append(project)
        if len(projects) == count:
            return projects, True

    return projects, False


def get_last_projects_by_count(count=1) -> list[Project]:
    projects = []
    for page_number in range(1, MAX_PARSE_PAGE_NUMBER+1):
        params = {'kind': 1, 'page': page_number}
        html = get_html(PROJECTS_URL, params)
        new_projects, stop = parse_projects_by_count(html, count-len(projects))
        if stop:
            break

        projects.extend(new_projects)

    return projects
