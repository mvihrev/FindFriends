# FindFriends API

## Django-сервис, который позволяет пользователям заводить новых друзей


### Предисловие

 - Для упрощения проверки тестового задания файл `config.yaml` специально не был добавлен в `.gitignore`
 - К сожалению, не хватило времени для написания тестов и Dockerfile, а также правильной настройки permissions. При необходимости они могут быть сделаны
 - Изначально хотел воспользоваться библиотекой `drf-nested-routers`, так как это сильно бы упростило реализацию некоторых вещей из-за возможности оздавать вложенные маршруты любой глубины (например */api/users/{username}/friends/{username}/delete)*, но прочитал, что это является REST Anti-Pattern. По этой причине идею отбросил.
 - Понимаю, что некоторый вещи сделаны неидеально. Хотелось бы узнать, где и что можно улучшить. Буду очень благодарен за фидбэк, так как он поможет мне в дальнейшем профессиональном развитии! **Email:** `mvihrev.work@gmail.com` **Telegram:** `@cyberunique`



### Архитектура проекта
![image](https://github.com/mvihrev/FindFriends/assets/36511881/9837bc2e-86db-4ee4-b997-b422b4b0b551)


    User: username(PK, varchar(32));

    Friendship: friendship_id(PK, integer); first_user(FK); second_user(FK);

    Request: request_id(PK, integer); sender(FK); receiver(FK); status(varchar(1));

  Данная архитектура менее удобна для написания различных запросов по сравнению с (User, UserFriends, UserRequests), однако, значительно уменьшает количество записей в БД, сокращая занимаемую память. Считаю, что это достаточно важный параметр, поэтому были созданы именно такие таблицы.
  
### Запуск проекта 
1. Скачиваем проект ```git clone https://github.com/mvihrev/FindFriends```
2. Переходим в нужную папку ```cd FindFriends/FindFriends/```
3. Создаем виртуальное окружение ```python3 -m venv env```
4. Включаем виртуальное окружение ```source env/bin/activate```
5. Устанавливаем необходимые библиотеки ```pip install -r requirements.txt```
6. Создаем базу данных ```python3 manage.py makemigrations``` и ```python3 manage.py migrate```
7. Запускаем локальный сервер ```python3 manage.py runserver```

### Использование API
Для просмотра документации OpenAPI достаточно перейти по ссылке http://127.0.0.1:8000/api/schema/swagger-ui/#/ или открыть файл `schema.yml`

**Тэг №1 - friendships:**

  - Метод получения списка дружеских отношений ['GET'] - /api/friendships/
  
  - Метод создания новых дружеских отношений ['POST'] - /api/friendships/
  
  - Метод получения дружеского отношения идентификатору ['GET'] - /api/friendships/{id}/
  
  - Методы редактирования дружеского отношения ['PUT', 'PATCH'] - /api/friendships/{id}/
  
  - Метод удаления дружеского отношения ['DELETE'] - /api/friendships/{id}

 **Тэг №2 - requests:**
 
   - Метод получения списка запросов ['GET'] - /api/requests/
  
  - Метод создания нового запроса ['POST'] - /api/requests/
  
  - Метод получения запроса идентификатору ['GET'] - /api/requests/{id}/
  
  - Методы редактирования запроса ['PUT', 'PATCH'] - /api/requests/{id}/
  
  - Метод удаления запроса ['DELETE'] - /api/requests/{id}

**Тэг #3 - users:**

  - Метод получения списка пользователей ['GET'] - /api/users/
  
  - Метод создания нового пользователя ['POST'] - /api/users/
  
  - Метод получения пользователя по идентификатору ['GET'] - /api/users/{username}/
  
  - Методы редактирования пользователя ['PUT', 'PATCH'] - /api/users/{username}/
  
  - Метод удаления пользователя ['DELETE'] - /api/users/{username}/

  - Метод получения списка друзей пользователей ['GET'] - /api/users/{username}/friends/

  - Метод удаления пользователя из списка друзей ['GET'] - /api/users/{username}/friends/?delete={username}

  - Метод получения списка входящих запросов в друзья ['GET'] - /api/users/{username}/incoming/
  
  - Метод принятия входящей заявки в друзья ['GET'] - /api/users/{username}/incoming/?accept={request_id}
  
  - Метод отклонения входящей заявки в друзья ['GET'] - /api/users/{username}/incoming/?decline={request_id}

  - Метод получения списка исходящих запросов в друзья ['GET'] - /api/users/{username}/outgoing/

  - Метод получения статуса отношений с пользователем ['GET'] - /api/users/{username}/status/?checking_user={username}
  
  
