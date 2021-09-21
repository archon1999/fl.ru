from django.db import models
from django.utils import timezone


def chapter_to_tag(text):
    new_text = str()
    for char in text:
        if char.isalnum():
            new_text += char.lower()
        else:
            new_text += '_'

    return new_text


class Chapter(models.Model):
    chapters = models.Manager()
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        to="self",
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    projects = models.Manager()
    article = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.IntegerField(null=True)
    deadline = models.DateField(null=True)
    safe_deal = models.BooleanField(default=False)
    without_executor = models.BooleanField(default=False)
    chapters = models.ManyToManyField(Chapter)
    published = models.DateTimeField()
    url = models.URLField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_description(self):
        description = self.description
        if len(description) > 700:
            description = description[:700] + '...'

        return description

    def get_safe_deal_info(self):
        if self.safe_deal:
            return '🛡 Безопасная сделка'
        else:
            return ''

    def get_budget_info(self):
        if self.budget:
            return str(self.budget) + ' руб.'
        else:
            return 'ожидает предложений'

    def get_deadline_info(self):
        if self.deadline:
            return self.deadline
        else:
            return 'по договоренности'

    def get_chapters_info(self):
        chapters_info = str()
        for chapter in self.chapters.all():
            chapter_info = '#' + chapter_to_tag(chapter.name)
            chapters_info += chapter_info + ' '
            if chapter.parent:
                parent_info = '#' + chapter_to_tag(chapter.parent.name)
                chapters_info += parent_info + ' '

        return chapters_info

    def __str__(self):
        return self.title


class BotUser(models.Model):
    users = models.Manager()
    chat_id = models.IntegerField(unique=True)
    full_name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class BotUserFilter(models.Model):
    user = models.OneToOneField(
        to=BotUser,
        on_delete=models.CASCADE,
        related_name='filter'
    )
    budget_min = models.IntegerField(null=True, blank=True)
    budget_max = models.IntegerField(null=True, blank=True)
    only_safe_deal = models.BooleanField(default=False)
    only_without_executor = models.BooleanField(default=True)
    chapters = models.ManyToManyField(Chapter)

    def is_valid_project(self, project: Project):
        budget_min = self.budget_min or 0
        budget_max = self.budget_max or 10**9
        if project.budget:
            if not(budget_min <= project.budget <= budget_max):
                return False

        if self.only_safe_deal and not project.safe_deal:
            return False

        if self.only_without_executor and not project.without_executor:
            return False

        user_filter_chapters = self.chapters.all()
        if not user_filter_chapters.exists():
            return True

        for chapter in project.chapters.all():
            if chapter in user_filter_chapters:
                return True

        return False

    def __str__(self):
        return str(self.user)


class UnfulfilledManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            when__lt=timezone.now(),
            done=False,
        )


class TaskManager(models.Model):
    class Type(models.TextChoices):
        NEW_PROJECT = 'New project'

    tasks = models.Manager()
    unfulfilled = UnfulfilledManager()

    type = models.CharField(max_length=30, choices=Type.choices)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    when = models.DateTimeField(default=timezone.now)
    done = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-when']

    def __str__(self):
        return f'{self.id}. {self.type}({self.project.id})'


class KeyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=Template.Type.KEY)


class MessageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=Template.Type.MESSAGE)


class SmileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=Template.Type.SMILE)


class Template(models.Model):
    class Type(models.TextChoices):
        KEY = 'Key'
        MESSAGE = 'Message'
        SMILE = 'Smile'

    templates = models.Manager()
    keys = KeyManager()
    messages = MessageManager()
    smiles = SmileManager()

    title = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=Type.choices)
    body_ru = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)

        keys = Template.keys.all()
        messages = Template.messages.all()
        smiles = Template.smiles.all()
        with open('backend/templates.py', 'w') as file:
            file.write('from .models import Template\n\n')
            file.write('\n')
            file.write('keys = Template.keys.all()\n')
            file.write('messages = Template.messages.all()\n')
            file.write('smiles = Template.smiles.all()\n\n')
            file.write('\n')
            file.write('class Keys():\n')
            for index, key in enumerate(keys):
                file.write(f'    {key.title} = keys[{index}]\n')

            file.write('\n\n')
            file.write('class Messages():\n')
            for index, message in enumerate(messages):
                file.write(f'    {message.title} = messages[{index}]\n')

            file.write('\n\n')
            file.write('class Smiles():\n')
            for index, smile in enumerate(smiles):
                file.write(f'    {smile.title} = smiles[{index}]\n')

        return result

    @property
    def text(self):
        return self.body_ru

    def get(self, lang):
        return getattr(self, f'body_{lang}')

    def getall(self):
        return (self.body_ru,)

    def format(self, **kwargs):
        return self.text.format(**kwargs)

    def __format__(self, format_spec):
        return format(self.text, format_spec)

    def __str__(self):
        return self.title
