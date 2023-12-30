 

const emotionsData = {
    admiration: {
        emoji: '🌟',
        color: ['rgba(255, 102, 51, 1)'],
    },
    amusement: {
        emoji: '😄',
        color: ['rgba(255, 102, 51, 1)'],
    },
    anger: {
        emoji: '😡',
        color: ['rgba(204, 0, 0, 1)'],
    },
    annoyance: {
        emoji: '😨',
        color: ['rgba(102, 0, 0, 1)'],
    },
    approval: {
        emoji: '😄',
        color: ['rgba(255, 102, 51, 1)'],
    },
    caring: {
        emoji: '❤️',
        color: ['rgba(204, 0, 51, 1)'],
    },
    confusion: {
        emoji: '🤔',
        color: ['rgba(255, 153, 51, 1)'],
    },
    curiosity: {
        emoji: '🤔',
        color: ['rgba(255, 153, 51, 1)'],
    },
    desire: {
        emoji: '😍',
        color: ['rgba(204, 0, 51, 1)'],
    },
    disappointment: {
        emoji: '😞',
        color: ['rgba(51, 0, 51, 1)'],
    },
    disapproval: {
        emoji: '😒',
        color: ['rgba(51, 0, 51, 1)'],
    },
    disgust: {
        emoji: '🤮',
        color: ['rgba(0, 102, 0, 1)'],
    },
    embarrassment: {
        emoji: '😳',
        color: ['rgba(255, 153, 51, 1)'],
    },
    excitement: {
        emoji: '🎉',
        color: ['rgba(255, 153, 0, 1)'],
    },
    fear: {
        emoji: '😨',
        color: ['rgba(102, 0, 0, 1)'],
    },
    gratitude: {
        emoji: '🙌',
        color: ['rgba(153, 102, 51, 1)'],
    },
    grief: {
        emoji: '😢',
        color: ['rgba(0, 0, 51, 1)'],
    },
    joy: {
        emoji: '😄',
        color: ['rgba(255, 102, 51, 1)'],
    },
    love: {
        emoji: '❤️',
        color: ['rgba(204, 0, 51, 1)'],
    },
    nervousness: {
        emoji: '😰',
        color: ['rgba(102, 0, 0, 1)'],
    },
    optimism: {
        emoji: '😊',
        color: ['rgba(255, 102, 51, 1)'],
    },
    pride: {
        emoji: '🦚',
        color: ['rgba(102, 0, 102, 1)'],
    },
    realization: {
        emoji: '💡',
        color: ['rgba(255, 102, 51, 1)'],
    },
    relief: {
        emoji: '😌',
        color: ['rgba(0, 102, 204, 1)'],
    },
    remorse: {
        emoji: '😔',
        color: ['rgba(102, 0, 0, 1)'],
    },
    sadness: {
        emoji: '😢',
        color: ['rgba(0, 0, 51, 1)'],
    },
    surprise: {
        emoji: '😲',
        color: ['rgba(255, 153, 0, 1)'],
    },
    neutral: {
        emoji: '😶',
        color: ['rgba(153, 153, 153, 1)'],
    },
    positive: {
        emoji: '😊',
        color: ['rgba(0, 102, 0, 1)'],
    },
    negative: {
        emoji: '😰',
        color: ['rgba(204, 0, 51, 1)'],
    },
};

let backendURL
async function loadConfig() {
    try {
      const response = await fetch('config.json');
      const config = await response.json();
      backendURL = config.backendURL;
    } catch (error) {
      console.error('Error loading configuration:', error);
    }
  }
  
loadConfig();


function updateEmotionBars(emotions, emotionContainerID = 'main-emotion-container') {
    
    const emotionContainer = document.getElementById(emotionContainerID);
    emotionContainer.innerHTML = '';
    
    let nrEmotions = (emotionContainerID == 'main-emotion-container') ? emotions_shown : 3;

    emotions.slice(0, nrEmotions).forEach(emotion => {
        const emotionBar = document.createElement('div');
        emotionBar.className = 'emotion-bar';

        const emotionName = document.createElement('p');
        emotionName.className = 'emotion-name';
        emotionName.innerText = `${emotion[0]} ${emotionsData[emotion[0]].emoji}`;


        const barContainer = document.createElement('div');
        barContainer.className = 'bar-container';
        
        const barFill = document.createElement('div');
        barFill.className = 'emotion-bar-fill';
        
        const widthPercentage = emotion[1] * 100;
        barFill.style.width = `${widthPercentage}%`;
        barFill.style.backgroundColor = emotionsData[emotion[0]].color;

        
        const barLabel = document.createElement('div');
        barLabel.className = 'emotion-bar-label';
        barLabel.innerText = `${(100*emotion[1]).toFixed(0)}%`;
        
        if (emotionContainerID != 'main-emotion-container') {
            barFill.style.display = "none";
            barContainer.style.backgroundColor = "rgba(0, 0, 0, 0)"; 
            barContainer.style.border = "none"; 
            barLabel.style.fontSize = `14px`;
            barLabel.style.fontWeight = 'bold';
            barLabel.style.textShadow = '2px 2px 2px rgba(0, 0, 0, 0.5)';
        }

        barContainer.appendChild(barFill);
        barContainer.appendChild(barLabel);
        emotionBar.appendChild(emotionName);
        emotionBar.appendChild(barContainer);
        emotionContainer.appendChild(emotionBar);
    });
}


let used_model="BERT"
document.getElementById("BertButton").classList.add("active");

document.getElementById("BertButton").onclick = function(){
    
    if (used_model == "BERT") return;
    else used_model="BERT";

    toggleModelButtons();
    
    let curr_text = document.getElementById("text-box").value;
    if (curr_text) sendTexts([curr_text]);
    else return;

    hideBatchAnalysisResult();

}

document.getElementById("LSTMButton").onclick = function(){

    if (used_model == "LSTM") return;
    else used_model="LSTM";

    toggleModelButtons();

    let curr_text = document.getElementById("text-box").value;
    if (curr_text) sendTexts([curr_text]);
    else return;

    hideBatchAnalysisResult();

}


function toggleModelButtons(){
    document.getElementById("BertButton").classList.toggle("active");
    document.getElementById("LSTMButton").classList.toggle("active");
    
}


let data, emotions_shown = 1;

async function sendTexts(texts, command="classify-sentences"){

    let body;
    body = JSON.stringify({ texts: texts, used_model: used_model});

    try {
        showWheel(command == "classify-sentences" ? "upper" : "lower");
        const response = await fetch(`${backendURL}/${command}`, {
            method: "POST",
            mode: "cors",
            headers: {
                "Content-Type": "application/json",
            },
            body: body,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        if (command == "classify-sentences"){
        data = await response.json();

        data = Object.entries(data[0]);
        data.sort(function(a, b) { return b[1] - a[1] });

        updateEmotionBars(data);
        }

        else{
            
            data = await response.json();

            document.getElementById("batchResultPositiveSentence").textContent = data.most_positive;
            document.getElementById("batchResultNegativeSentence").textContent = data.most_negative;

            emotions = Object.entries(data.emotions);
            emotions = emotions.filter(function(entry) {return entry[0] !== "neutral";}); //TODO
            emotions.sort(function(a, b) { return b[1] - a[1] });

            updateEmotionBars(emotions, emotionContainerID = "emotion-container-batch-emotions");


            sentiment = Object.entries(data.sentiment);
            sentiment.sort(function(a, b) { return b[1] - a[1] });

            updateEmotionBars(sentiment, emotionContainerID = "emotion-container-batch-sentiment");

            jsonString = data.full_report;

            document.getElementById("batchAnalysisResult").style.display = "flex";

            window.scrollTo(0, document.body.scrollHeight);
        }
        
    
    
    } catch (error) {

        
        console.error("Error:", error);
    }

    hideWheel(command == "classify-sentences" ? "upper" : "lower");
    document.getElementById("stacked-buttons-wrapper").style.display="flex";

 }


function emotionsShown(direction){

    if ( emotions_shown + direction > 4 || emotions_shown + direction < 1)
    {
        return;
    }

    emotions_shown += direction;
    updateEmotionBars(data);
}


const randomTexts = [
    "Hello, World!",
    "JavaScript is awesome",
    "Choose me!",
    "Randomness is fun",
    "Learning AI brings me so much joy!", 
    "Ugh, that chicken is rotten",
    "It's a beautiful summer!",
    "I'm sorry for breaking your heart...",
    "Vistula is a river in Poland",
    "This tool recognizes 28 emotions, it's stunning!",
    "Thanks for staying with me at the hospital!",
    "As the dark shadows crept closer, a chilling sense of fear began to consume me",
    "I'm so proud of you!",
    "A sudden clap of thunder startled everyone",
    "I adore you, baby.",
    "Product did not live up to the online description. Not worth it.", 
    "I was disappointed with the service.",
    "There are 50 states in the USA.",
    "I will not say that I like it.",
    "I like going to the gym and doing yoga.",
    "Because of him I was forced to wait 2 hours in the cold...",
    "Reviews on the website were fake and misleading.",
    "I want this dress so much!"
      ];
      

function hideBatchAnalysisResult(){
    document.getElementById("batchAnalysisResult").style.display = "none";
}

let typingTimer;
const doneTypingInterval = 1000; 

function typedText(text, dont_wait=false) {

    if (text.length == 0)
    {
        return;
    }

    if(dont_wait){
        sendTexts([text]);
    }

    else{
        clearTimeout(typingTimer); 

        typingTimer = setTimeout(() => {
            sendTexts([text]);
        }, doneTypingInterval);
    }
    
}



function insertRandomText() {
    
    hideBatchAnalysisResult();

    const textBox = document.getElementById("text-box");

    let randomText;
    do 
    {
        randomText = randomTexts[Math.floor(Math.random() * randomTexts.length)];
    } 
    while (randomText == textBox.value)

    textBox.value = randomText;
    typedText(randomText, dont_wait=true); // Call your typedText function
}


function split_string(text){

    var result = text.split(/\n|\./);

    result = result.filter(function(item) {
        return item.trim() !== "";
    }).map(function(item) {
        return item.trim(); 
    });

    console.log(result);

    return result
}

document.getElementById("spinning-wheel-upper").style.display = 'none';
document.getElementById("spinning-wheel-lower").style.display = 'none';

function showWheel(which="upper"){
    document.getElementById(`spinning-wheel-${which}`).style.display = 'block';
}

function hideWheel(which="upper"){
    document.getElementById(`spinning-wheel-${which}`).style.display =  'none';
}

function exemplaryBatchPrediction(){
    sendTexts(randomTexts, command="generate-report");
}

function handleFileChange(event) {

    const selectedFile = event.target.files[0];
    const reader = new FileReader();

            reader.onload = function (e) {
                const fileContent = e.target.result;     
                if (fileContent.length > 0) sendTexts(split_string(fileContent), command="generate-report");
            };

            reader.readAsText(selectedFile);

    document.getElementById("fileInput").value = "";
}


var jsonString = null;
var downloadLink = document.getElementById('downloadLink');

downloadLink.addEventListener('click', function() {
    var blob = new Blob([jsonString], { type: 'application/json' });
    
    dataUrl = URL.createObjectURL(blob);
    window.open(dataUrl, '_blank');
});


function showExemplaryFile(){
    var blob = new Blob([randomTexts.join('\n')], { type: 'text/plain' });
    dataUrl = URL.createObjectURL(blob);
    window.open(dataUrl, '_blank');
}


var hoverElement = document.getElementById('info-button');
var explanation = document.getElementById('explanation');


hoverElement.addEventListener('mouseover', function() {
    hideBatchAnalysisResult();
    explanation.style.display = 'block';
});

hoverElement.addEventListener('mouseout', function() {
    explanation.style.display = 'none';
});


fetch(`${backendURL}/health-check`)
  .then(response => {
    if (!response.ok) {
      throw new Error(`Network response was not ok: ${response.statusText}`);
    }
    return response.text();
  })
  .then(data => {
    console.log('Health check response:', data);
  })
  .catch(error => {
    console.error('Error during health check:', error.message);
  });
