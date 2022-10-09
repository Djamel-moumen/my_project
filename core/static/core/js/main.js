var toResume = false;
const colors = [
    'rgb(224, 51, 38)',
    'rgb(38, 69, 224)',
    'rgb(224, 218, 38)',
    'rgb(202, 38, 224)',
    'rgb(38, 205, 224)',
]

const strategyDiv = `<hr><div class="strategy-div">
          <div class="form-check form-switch">
            <input class="form-check-input smart-switch" type="checkbox" name="smartbee" value="yes">
            <label class="form-check-label" for="smart-switch">Smart bees</label>
          </div>
          <div class="mb-3 mt-3">
            <input type="number" class="form-control nbr-bees-input" placeholder="Enter the number of bees">
          </div>
          <div class="mb-3">
            <input class="form-control nbr-neighbors-input" type="number" placeholder="Enter the number of neighbors">
          </div>
          <div class="mb-3">
            <input class="form-control max-chance-input" type="number" placeholder="Enter MaxChance">
          </div>
        </div>`

const ctx = document.getElementById('myChart').getContext('2d');
const myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [0],
        datasets: [{
            label: 'Comb 1',
            data: [{x: 0, y: 0}],
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});



const mySocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws'
    + window.location.pathname
);

mySocket.onmessage = function(e) {
    const message = JSON.parse(e.data);
    if (message["intent"] === "transaction_data") {
        displayTransactionData(message["content"]);
    } else if (message["intent"] === "update") {
        update(message["content"]);
    }
};

document.querySelector('#add-strategy-button').onclick = function(e) {
    var tag = document.createElement("div"); // <p></p>
    tag.innerHTML = strategyDiv
    var element = document.getElementById("strategies-container");
    element.appendChild(tag);
    chartAddStrategy();
    if (myChart.data.datasets.length == 6) {
        document.getElementById('add-strategy-button').disabled = true;
    }
};

document.querySelector('#launch-button').onclick = function(e) {
    disableInputs();
    document.getElementById('launch-button').disabled = true;
    document.getElementById('reset-button').disabled = true;

    if (toResume === false) {
        toResume = true;
        strategiesData = [];
        const strategyDivs = document.getElementById("strategies-container").getElementsByClassName("strategy-div");
        for (strategyDivTemp of strategyDivs) {
            strategiesData.push(
                {
                    "nbr_bees": strategyDivTemp.getElementsByClassName("nbr-bees-input")[0].value,
                    "nbr_neighbors": strategyDivTemp.getElementsByClassName("nbr-neighbors-input")[0].value,
                    "max_chance": strategyDivTemp.getElementsByClassName("max-chance-input")[0].value,
                    "smart": strategyDivTemp.getElementsByClassName("smart-switch")[0].checked
                }
            )
        }
        mySocket.send(JSON.stringify({
        'intent': 'launch',
        'content': strategiesData
        }));
        document.getElementById('pause-button').removeAttribute('disabled');
    } else {
        mySocket.send(JSON.stringify({
        'intent': 'resume'
        }));
        document.getElementById('pause-button').removeAttribute('disabled');
    }


};

document.querySelector('#pause-button').onclick = function(e) {
    document.getElementById('pause-button').disabled = true;
    mySocket.send(JSON.stringify({
    'intent': 'pause'
    }));
    document.getElementById('launch-button').removeAttribute('disabled');
    document.getElementById('reset-button').removeAttribute('disabled');
};

document.querySelector('#reset-button').onclick = function(e) {
    toResume = false;
    enableInputs();
    document.getElementById('reset-button').disabled = true;
    mySocket.send(JSON.stringify({
    'intent': 'stop'
    }));
    resetAll();
    document.getElementById('launch-button').removeAttribute('disabled');
};

function displayTransactionData(data) {
    for (const key of Object.keys(data)) {
        var tag = document.createElement("div"); // <p></p>
        var text = document.createTextNode(`${key}: ${data[key]}`);
        tag.appendChild(text); // <p>TEST TEXT</p>
        var element = document.getElementById("dataset-info-container");
        element.appendChild(tag);
    }

}

function update(data) {
    updateChart({"x": data['Nbr explored ars'], "y": data['Average fitness'], "num": data["num"]});
    updateTable(data["top 100 ars"])
}

function updateTable(arsList) {
    tableBody = document.getElementById("tbody");
    var content = ""
    for (ar of arsList) {
        content += `<tr>
            <td>(${ar.antecedent}) -> ${ar.consequence}</td>
            <td>${ar.support}</td>
            <td>${ar.confiance}</td>
            <td>${ar.fitness}</td>
            </tr>`
    }
    tbody.innerHTML = content;
}

function updateChart(data) {
    console.log(`${data["num"]} | ${data["x"]} | ${data["y"]}`);

    insert(myChart.data.labels, data["x"]);
    console.log(myChart.data.labels)

    myChart.data.datasets[data["num"]].data.push({x: data["x"], y: data["y"]});
    myChart.update();
}

function resetChart() {
    myChart.data.labels = [0];
    for (dataset of myChart.data.datasets) {
        dataset.data = [{x: 0, y: 0}];
    }
    myChart.update();
}

function resetTable() {
    tableBody = document.getElementById("tbody");
    var content = ""
    tbody.innerHTML = content;
}

function resetAll() {
    resetChart();
    resetTable();
}

function disableInputs() {
    document.getElementById("add-strategy-button").disabled = true;
    const strategyDivs = document.getElementById("strategies-container").getElementsByClassName("strategy-div");
    for (strategyDivTemp of strategyDivs) {
        strategyDivTemp.getElementsByClassName("nbr-bees-input")[0].disabled = true;
        strategyDivTemp.getElementsByClassName("nbr-neighbors-input")[0].disabled = true;
        strategyDivTemp.getElementsByClassName("max-chance-input")[0].disabled = true;
        strategyDivTemp.getElementsByClassName("smart-switch")[0].disabled = true;
    }
}

function enableInputs() {
    document.getElementById("add-strategy-button").disabled = false;
    const strategyDivs = document.getElementById("strategies-container").getElementsByClassName("strategy-div");
    for (strategyDivTemp of strategyDivs) {
        strategyDivTemp.getElementsByClassName("nbr-bees-input")[0].disabled = false;
        strategyDivTemp.getElementsByClassName("nbr-neighbors-input")[0].disabled = false;
        strategyDivTemp.getElementsByClassName("max-chance-input")[0].disabled = false;
        strategyDivTemp.getElementsByClassName("smart-switch")[0].disabled = false;
    }
}

function chartAddStrategy(nbrStrategies) {
    myChart.data.datasets.push({
        label: `Comb ${myChart.data.datasets.length + 1}`,
        data: [{x: 0, y: 0}],
        fill: false,
        borderColor: colors[myChart.data.datasets.length - 1],
        tension: 0.1
    });
    myChart.update()

}

function insert(arr, element) {
    if (element < arr[0]) {
        arr.splice(0, 0, element);
        return
    }
    if (element > arr[arr.length - 1]) {
        arr.push(element);
        return
    }
    for (let i = 1; i < arr.length; i++) {
	    if (element > arr[i - 1] && element < arr[i]) {
	        arr.splice(i, 0, element);
	    } else if (element === arr[i - 1] || element === arr[i]) {
	        return
	    }
    }
}


