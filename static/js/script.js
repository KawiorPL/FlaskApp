var socket = io();

function uruchomCheck_Data() {
    socket.emit('uruchom_Check_Data');
}

function uruchomCheck_Data() {
    socket.emit('uruchom_czyszczenie_Data');
}


function zbierajDane() {
    const urlInput = document.getElementById('urlInput');
    if (urlInput && urlInput.value) {
        const url = urlInput.value;
        socket.emit('zbieraj_Dane', { url: url });
    } else {
        alert('Proszę wprowadzić URL.');
    }
}

socket.on('connect', function() {
    console.log('Połączono z serwerem SocketIO');
});

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
