let isListening = true;

function toggleMic() {
    const micBtn = document.getElementById('micBtn');
    const voiceCircle = document.getElementById('voiceCircle');
    const listeningText = document.getElementById('listeningText');
    
    isListening = !isListening;
    
    if (isListening) {
        micBtn.classList.add('active');
        voiceCircle.style.animation = 'pulse 2s ease-in-out infinite';
        listeningText.textContent = 'Escuchando...';
        listeningText.style.display = 'block';
    } else {
        micBtn.classList.remove('active');
        voiceCircle.style.animation = 'none';
        listeningText.style.display = 'none';
    }
}

function closeAssistant() {
    // Navigate back to navigation page
    window.location.href = 'navigation.html';
}

// Simulate conversation
function addMessage(text, isUser = false) {
    const conversationArea = document.querySelector('.conversation-area');
    const message = document.createElement('div');
    message.className = isUser ? 'message user-message' : 'message assistant-message';
    message.textContent = text;
    conversationArea.appendChild(message);
    conversationArea.scrollTop = conversationArea.scrollHeight;
}

// Example: Simulate assistant response after 2 seconds
setTimeout(() => {
    // You can add more conversation logic here
}, 2000);
