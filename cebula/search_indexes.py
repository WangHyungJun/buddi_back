import datetime
from haystack import indexes
from cebula.models import MyUser, Book, Note, Question


class MyUserIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    username = indexes.CharField(model_attr='username')
    pub_date = indexes.DateTimeField(model_attr='last_login', null=True)
    content_auto = indexes.EdgeNgramField(model_attr='username')

    def get_model(self):
        return MyUser

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

class BookIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name="search/book_text.txt")
    title = indexes.CharField(model_attr='title')
    authors = indexes.CharField()

    def get_model(self):
        return Book

    def index_queryset(self, using=None):
        return self.get_model().objects.all()


class NoteIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name="search/note_text.txt")
    author = indexes.CharField(model_attr='user')
    pub_date = indexes.DateTimeField(model_attr='pub_date')

    def get_model(self):
        return Note

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, template_name="search/question_text.txt")
    owner = indexes.CharField(model_attr='owner')
    content_auto = indexes.EdgeNgramField(model_attr='question_text')

    def get_model(self):
        return Question

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())

