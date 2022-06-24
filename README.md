# *Мега площадка для онлайн торговли магазинами в условиях пандемии*

## Для первого запуска:

### Установите зависимости из каталога requirements:
* `base.txt` - Общие зависимости
* `dev.txt` - Для разработки
* `prod.txt` - Для публикации сайта


### Переименуйте `.env-dist` в `.env` и заполните необходимые данные:

* DATABASE_URL: 
* * postgres://user:pass@localhost:port/dbname
* * sqlite:///db.sqlite3
* SECRET_KEY: сгенерируйте свой секретный ключ 
```
from django.core.management.utils import get_random_secret_key 
get_random_secret_key()
```

### Задайте переменную окружения `DJANGO_SETTINGS_MODULE=market.settings.dev` (*market.settings.prod ДЛЯ PRODUCTION!!!!*)
* Linux: `export DJANGO_SETTINGS_MODULE=market.settings.dev`
* Windows: `set DJANGO_SETTINGS_MODULE=market.settings.dev`
* С помощью django: `python manage.py runserver --settings market.settings.dev`
* C помощью PyCharm: [PyCharm EditConfiguration](https://stackoverflow.com/a/42708480/16184934)


