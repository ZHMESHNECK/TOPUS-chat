// login_form
const formlogin = document.getElementById('login_form');
formlogin.addEventListener('submit', (e) => {
    e.preventDefault();

    // Створюємо об'єкт зі зібраними даними
    const data = {
        username: document.getElementById('login_username').value,
        password: document.getElementById('login_password').value
    };


    let xhr = new XMLHttpRequest();
    xhr.open('POST', '/auth/login', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(data));

    xhr.onload = function () {
        if (xhr.status === 200) {
            let response = JSON.parse(xhr.responseText);
            localStorage.setItem('token', response.token);
            location.assign('/');

        } else {
            let response = JSON.parse(xhr.responseText);
            if (response.detail) {
                document.getElementById('signInError').style.display = "block";
                document.getElementById('signInError').textContent = response.detail;
            } else {
                document.getElementById('signInError').style.display = "none";
            }
        }
    };

})

// register_form
const formregister = document.getElementById('register_form');
formregister.addEventListener('submit', (e) => {
    e.preventDefault();
    // Створюємо об'єкт зі зібраними даними
    const data = {
        username: document.getElementById('signUpUsername').value,
        password: document.getElementById('signUpPassword').value,
        re_password: document.getElementById('signUpRePassword').value
    };


    let xhr = new XMLHttpRequest();
    xhr.open('POST', '/auth/registration', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(data));

    xhr.onload = function () {
        if (xhr.status === 201) {
            let response = JSON.parse(xhr.responseText);

            localStorage.setItem('token', response.token)

            location.assign('/');

        } else {
            let response = JSON.parse(xhr.responseText);
            if (response.detail) {
                document.getElementById('signInError').textContent = response.detail
            } else {
                document.getElementById('signUpError_username').textContent = ''

            }
            if (response.username) {
                document.getElementById('signUpError_username').textContent = response.username
            } else {
                document.getElementById('signUpError_username').textContent = ''

            }
            if (response.password) {
                document.getElementById('signUpError_password').textContent = response.password
            } else {
                document.getElementById('signUpError_password').textContent = ''

            }
            if (response.re_password) {
                document.getElementById('signUpError_re_password').textContent = response.re_password
            } else {
                document.getElementById('signUpError_re_password').textContent = ''

            }
        }
    };

})



document.getElementById('login').addEventListener('click', function () {
    document.getElementById('login_form').style.display = 'block';
    document.getElementById('register_form').style.display = 'none';
});

document.getElementById('register').addEventListener('click', function () {
    document.getElementById('register_form').style.display = 'block';
    document.getElementById('login_form').style.display = 'none';
});
