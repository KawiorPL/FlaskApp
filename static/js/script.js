var socket = io();


socket.on('connect', () => {
    console.log('Połączono z serwerem WebSocket');
});

socket.on('generowanie_rozpoczęte', () => {
    alert('Rozpoczęto generowanie wykresu. Proszę czekać.');
});

socket.on('generowanie_w_toku', () => {
    alert('Generowanie wykresu jest już w toku.');
});

socket.on('wykres_istnieje', () => {
    wyswietlWykres();
});

socket.on('chart_gotowy', () => {
    console.log('Otrzymano powiadomienie o gotowym wykresie');
    wyswietlWykres();
});

function uruchomChart() {
    socket.emit('uruchom_Chart');
    // Ustaw odświeżenie strony po 10 sekundach (10000 milisekund)
    setTimeout(function() {
        location.reload();
    }, 10000);
}
function wyswietlWykres() {
    const chartContainer = document.getElementById('chart-container');
    chartContainer.innerHTML = '';
    const img = document.createElement('img');
    img.src = '\static\charts\analizaAktorow.png?t=' + new Date().getTime();
    img.alt = 'Wygenerowany Wykres';
    chartContainer.appendChild(img);
}



function uruchomTworzenie_Db() {
    socket.emit('uruchom_Tworzenie_DB');
    setTimeout(function() {
        location.reload();
    }, 5000);
}


function uruchomCheck_Data() {
    socket.emit('uruchom_Check_Data');
}

function uruchomClear_Data() {
    socket.emit('uruchom_czyszczenie_Data');
}


function isValidURL(url) {
    const urlPattern = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/;
    return urlPattern.test(url);
}

function zbierajDane() {
    const urlInput = document.getElementById('urlInput');
    if (!urlInput) {
        alert('Błąd: Pole URL nie zostało znalezione w HTML.');
        return;
    }

    const url = urlInput.value.trim(); // Remove whitespace
    if (!url) {
        alert('Proszę wprowadzić URL.');
        return;
    }

    if (!isValidURL(url)) {
        alert('Niepoprawny URL. Proszę wprowadzić poprawny adres URL.');
        return;
    }

    if (!socket) {
        alert('Błąd: Socket nie został zainicjalizowany.');
        return;
    }

    socket.emit('zbieraj_Dane', { url: url });
    console.log('Wysłano URL:', url);
}

socket.on('disconnect', function() {
    console.log('Rozłączono z serwerem SocketIO');
});

socket.on('script_output', function(msg) {
    console.log("Otrzymano dane: ", msg);

    var outputDiv = document.getElementById('output');

    // Dodawanie nowych danych bez czyszczenia
    var newOutputLine = document.createElement('div');
    newOutputLine.textContent = '[' + msg.script + ']: ' + msg.output;
    outputDiv.appendChild(newOutputLine);
});

socket.on('script_error', function(msg) {
    console.log("Otrzymano błąd: ", msg);

    var errorDiv = document.getElementById('output');
    var newErrorLine = document.createElement('div');
    newErrorLine.classList.add('error');
    newErrorLine.textContent = 'Błąd w [' + msg.script + ']: ' + msg.error;
    errorDiv.appendChild(newErrorLine);
});
