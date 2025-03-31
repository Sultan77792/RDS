$(document).ready(function() {
    // Загрузка списка пользователей
    function loadUsers() {
        $.get('/users/', function(data) {
            const tableBody = $('#usersTableBody');
            tableBody.empty(); // Очистка перед добавлением новых данных
            data.forEach(user => {
                tableBody.append(`
                    <tr data-id="${user.id}">
                        <td>${user.id}</td>
                        <td>${user.username}</td>
                        <td>${user.roles}</td>
                        <td>${user.region}</td>
                        <td>
                            <button class="btn btn-danger btn-sm delete-user" data-id="${user.id}">Удалить</button>
                        </td>
                    </tr>
                `);
            });
        }).fail(function(xhr) {
            alert('Ошибка загрузки пользователей: ' + xhr.responseJSON.error);
        });
    }

    // Открытие модального окна
    $('#addUserBtn').click(function() {
        $('#addUserModal').modal('show');
    });

    // Сохранение нового пользователя
    $('#saveUserBtn').click(function() {
        const userData = {
            username: $('#username').val().trim(),
            password: $('#password').val().trim(),
            roles: $('#roles').val().trim(),
            region: $('#region').val().trim()
        };

        if (!userData.username || !userData.password || !userData.roles || !userData.region) {
            alert('Все поля обязательны для заполнения');
            return;
        }

        $.ajax({
            url: '/users/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(userData),
            success: function(response) {
                $('#addUserModal').modal('hide');
                $('#addUserForm')[0].reset();
                loadUsers();
            },
            error: function(xhr) {
                alert('Ошибка при добавлении пользователя: ' + xhr.responseJSON.error);
            }
        });
    });

    // Удаление пользователя
    $(document).on('click', '.delete-user', function() {
        const userId = $(this).data('id');
        if (confirm('Вы уверены, что хотите удалить этого пользователя?')) {
            $.ajax({
                url: `/users/${userId}`,
                type: 'DELETE',
                success: function(response) {
                    loadUsers();
                },
                error: function(xhr) {
                    alert('Ошибка при удалении пользователя: ' + xhr.responseJSON.error);
                }
            });
        }
    });

    // Первоначальная загрузка пользователей
    loadUsers();
});