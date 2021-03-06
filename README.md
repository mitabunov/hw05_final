# Yatube - Социальная сеть блогеров. Учебный проект

Разработан в рамках обучения по программе "Python-разработчик" в Яндекс.Практикум.

Проект развернут на Яндекс.Облаке по адресу https://issafronov.co.vu/

## Концепция проекта Yatube
"Необходимо разработать социальную сеть для публикации личных дневников. Это будет сайт, на котором можно создать свою страницу. Если на нее зайти, то можно посмотреть все записи автора. Пользователи смогут заходить на чужие страницы, подписываться на авторов и комментировать их записи. Дизайн можно взять самый обычный, но красивый. Должно выглядеть нормально, поиграйте со шрифтами. Еще надо иметь возможность модерировать записи и блокировать пользователей, если начнут присылать спам. Записи можно отправить в сообщество и посмотреть там записи разных авторов. Вы же программисты, сами понимаете, как лучше сделать."

### Функции
* Создание сообщества для публикаций (только для администратора сайта)
* Регистрация, авторизация
* Публикация поста в ленте, и возможность выбора сообщества (необязательно)
* Добавление новых записей авторизованными пользователями
* Добавление изображений
* Добавление и редактирование комментариев
* Редактирование постов (только его автором)
* Возможность подписаться и отписаться на авторов
* Отдельная лента с постами, на авторов которых подписан пользователь
* Кэширование, работает на главной странице
* Пагинация

### Unittest
* После регистрации пользователя создается его персональная страница
* Авторизованный пользователь может опубликовать пост
* Неавторизованный посетитель не может опубликовать пост
* После публикации поста новая запись появляется на главной странице сайта, на персональной странице пользователя, и на отдельной странице поста;
* Авторизованный пользователь может отредактировать свой пост и его содержимое изменится на всех связанных страницах.
* Авторизованный пользователь может подписываться на других пользователей и удалять их из подписок;
* Новая запись пользователя появляется в ленте тех, кто на него подписан и не появляется в ленте тех, кто не подписан на него;
* Только авторизированный пользователь может комментировать посты.

### Стек технологий
+ python3
+ django 2.2
+ pytest 5.3.5
+ pytest-django 3.8.0
+ pillow 7.0.0
+ requests 2.22.0
+ sorl-thumbnail 12.6.3
+ mixer 7.1.2
+ django-debug-toolbar

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/issafronov/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Для доступа к панели администратора создайте администратора:

```
python manage.py createsuperuser
```

Запустить проект:

```
python3 manage.py runserver
```
