from django.db import models
from django.utils.translation import gettext_lazy as _


class CategoryBase(models.Model):
    name = models.CharField(max_length=250, verbose_name=_("Имя категории"))
    sort_index = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ('sort_index', 'name')

    def __str__(self) -> str:
        return f"{self.name}"


class Category(CategoryBase):
    ...

    @property
    def subcategories(self):
        return self.subcategory_set.filter(is_active=True)


class SubCategory(CategoryBase):
    parent_id = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{super().__str__()} / {self.parent_id.name}"
