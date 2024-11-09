// DOM Elements
const chatBox = document.getElementById('chatBox');
const questionInput = document.getElementById('questionInput');

// Function to add messages with specific formatting for the bot response
function addMessage(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

    if (!isUser) {
        const formattedMessage = message
            .replace(/Answer:/g, '<strong>Answer:</strong>')
            .replace(/Relevant Laws and Regulations:/g, '<strong>Relevant Laws and Regulations:</strong>')
            .replace(/Practical Steps or Resources:/g, '<strong>Practical Steps or Resources:</strong>')
            .replace(/Emergency Contacts:/g, '<strong>Emergency Contacts:</strong>');

        messageDiv.innerHTML = formattedMessage;
        
        // Add feedback buttons with timestamp as conversation ID
        const timestamp = new Date().toISOString();
        addFeedbackButtons(messageDiv, timestamp);
    } else {
        messageDiv.textContent = message;
    }

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to show loading state
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message loading';
    loadingDiv.textContent = 'Typing...';
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return loadingDiv;
}