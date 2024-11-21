<header>
        <h1>Описание работы сервиса и команды</h1>
        <p>Этот проект реализует веб-приложение с помощью FastAPI для управления пользователями, чатами и системой авторизации. Сервис предоставляет возможность пользователям общаться через WebSocket, получать и отправлять сообщения, а также выполнять административные операции. Разделение ответственности реализовано через маршруты для обычных пользователей, администраторов и авторизации.</p>
    </header>
    
  <section>
      <h2>Основные компоненты и функционал</h2>
      
  <h3>1. Авторизация и регистрация</h3>
  <p><strong>Маршруты:</strong></p>
  <ul>
      <li><code>/register</code>: регистрация нового пользователя.</li>
      <li><code>/login</code>: вход в систему с генерацией токена.</li>
  </ul>
  <p><strong>Используемые технологии:</strong></p>
  <ul>
      <li>Токены JWT для аутентификации.</li>
      <li>OAuth2PasswordBearer для получения токена.</li>
  </ul>

  <h3>2. Работа с чатами</h3>
  <p><strong>Маршрут WebSocket:</strong></p>
  <ul>
      <li><code>/ws/chat</code>: создание подключения для обмена сообщениями.</li>
      <li>Сообщения отправляются в формате json : <code>{"message":"","username_to":""}</code></li>
        <li>После отправкии сообщения приходит результат отправки в виде json : <code>{"status":"","error":""}</code></li>
  </ul>
  <p><strong>Функционал:</strong></p>
  <ul>
      <li>Проверка токена перед подключением.</li>
      <li>Возможность отправки сообщений между пользователями.</li>
      <li>Отключение WebSocket при нарушении политики (например, неверный токен).</li>
  </ul>

  <h3>3. Работа с сообщениями</h3>
  <p><strong>Маршруты для пользователей:</strong></p>
  <ul>
      <li><code>/getallmessages</code>: получить все сообщения.</li>
      <li><code>/getallchats</code>: получить все чаты.</li>
      <li><code>/getreadedmessages</code>: получить прочитанные сообщения.</li>
      <li><code>/getnotreadedmessages</code>: получить непрочитанные сообщения.</li>
      <li><code>/readnotreaded</code>: отметить все непрочитанные сообщения как прочитанные.</li>
      <li><code>/readnotreadedfromuser</code>: отметить сообщения от конкретного пользователя как прочитанные.</li>
  </ul>

  <h3>4. Административные команды</h3>
    <p><strong>Маршруты для администраторов:</strong></p>
  <p>Автоматический админ,которого можно заблокировать ,после создания других:
        username : admin
        name : Admin User
        mail : admin@example.com
        password : securepassword
</p>
  <ul>
      <li><code>/readuserchats</code>: получить все чаты конкретного пользователя.</li>
      <li><code>/getallactiveusers</code>: получить список активных пользователей.</li>
      <li><code>/blockuser</code>: заблокировать пользователя.</li>
      <li><code>/unblockuser</code>: разблокировать пользователя.</li>
  </ul>
  <p><strong>Функционал:</strong></p>
  <ul>
      <li>Проверка, что пользователь является администратором.</li>
      <li>Управление доступом пользователей к системе.</li>
  </ul>
  </section>
  
  <section>
      <h2>Архитектура</h2>
      <ul>
          <li>FastAPI используется для реализации API и маршрутов.</li>
          <li>WebSocket для чатов.</li>
          <li>SQLAlchemy (Async) для асинхронного взаимодействия с базой данных.</li>
          <li>JWT для безопасной авторизации.</li>
          <li><strong>Маршруты разделены:</strong>
              <ul>
                  <li><code>auth_router</code>: для авторизации и регистрации.</li>
                  <li><code>user_router</code>: для операций пользователя.</li>
                  <li><code>admin_router</code>: для административных операций.</li>
              </ul>
          </li>
          <li><strong>Управление WebSocket:</strong>
              <ul>
                  <li><code>ws_manager</code> для отслеживания подключений.</li>
              </ul>
          </li>
      </ul>
  </section>
  
  <section>
      <h2>Примеры команд и взаимодействий</h2>
      <h3>Пользовательский сценарий:</h3>
      <ol>
          <li>Пользователь регистрируется через <code>/register</code> и получает токен.</li>
          <li>Авторизуется через <code>/login</code>, получая токен для доступа.</li>
          <li>Подключается к WebSocket <code>/ws/chat</code> для общения.</li>
          <li>Читает и управляет своими сообщениями через API <code>/getallmessages</code> и другие.</li>
      </ol>
      
  <h3>Администраторский сценарий:</h3>
  <ol>
      <li>Авторизуется с токеном администратора.</li>
      <li>Получает список активных пользователей через <code>/getallactiveusers</code>.</li>
      <li>Блокирует пользователя через <code>/blockuser</code>.</li>
  </ol>
  </section>
  
  <section>
      <h2>Примечания</h2>
      <ul>
          <li>Используемый <code>SECRET_KEY</code> и <code>ALGORITHM</code> критически важны для безопасности. Они должны быть надежно защищены.</li>
          <li>Для повышения удобства можно добавить обработку ошибок с пользовательскими сообщениями и логирование действий.</li>
      </ul>
  </section>
