<h3>Сервис авторизации по номеру телефона</h3> 

<p>Первичная подготовка проекта к работе:</p>

<blockquote>Рекомендуемой виртуальной средой для разработки проекта
является poetry, вследствие чего перед началом работы с проектом необходимо
установить данный пакет командой pip install poetry</blockquote>
<ul>
<li>Выполняется установка зависимостей проекта командой <cite>poetry install</cite></li>
<li>Выполняется применение миграций командой <cite>python manage.py migrate</cite></li>
<li>Выполняется запуск проекта командой <cite>python manage.py runserver</cite></li>
</ul>

Последовательность работы с API сервиса:

1. По адресу <i>/users/auth/</i> пользователь отправляет POST запрос 
с указанием номера телефона в поле "phone_number". Производится валидация введённого номера 
посредством сериализатора.
2. При успешной валидации введённого пользователем на предыдущем шаге номера телефона 
происходит редирект (GET запрос) на адрес <i>/users/user_login/</i>. При этом происходит 
вызов сервисной функции generate_auth_code(), отвечающей за генерацию случайного 
4-х значного кода авторизации. Данный код сохраняется в текущей сессии.
    <blockquote> Для упрощения тестирования и отладки работы сервиса код, сгенерированный 
    в функции generate_auth_code() выводится в консоль. При дальнейшем развитии сервиса 
    сгенерированный код будет отправляться непосредственно на указанный пользователем
    номер телефона. </blockquote>
3. Пользователь отправляет POST запрос по адресу <i>/users/user_login/</i> с указанием 
кода авторизации в поле "verification_code". Если код введён корректно, сервис отвечает 
сообщением об успешной авторизации. Пользователь сохраняется в атрибут request.user. При этом
пользователь, который ранее не был зарегистрирован в системе автоматически добавляется 
в базу данных.
4. Проверку авторизации можно выполнить по адресу <i>/users/profile/</i>. При успешной 
проведённой авторизации пользователь увидит информацию о своём профиле.
5. Для удаления пользователя из сессии необходимо выполнить GET запрос по адресу 
<i>/users/logout/</i>

<p>Список зарегистрированных в системе пользователей доступен по адресу /users/list/. 
Управление профилем отдельного пользователя выполняется по адресу 
<i>/users/list/>>id пользователя<<</i></p>

<blockquote>Подробное описание API доступно по адресу /users/docs/</blockquote>

Дополнительно, в данном сервисе реализована реферальная система. Каждому пользователю 
при первой авторизации присваивается случайным образом сгенерированный инвайт-код. 
Далее пользователи могут ввести код реферера (другого пользователя) в своём профиле 
в поле invited_by, тем самым сохраняя информацию о пользователе, пригласившем данного 
реферала к участию в сервисе.
