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

// Main function to send questions and handle responses
async function sendQuestion() {
    const question = questionInput.value.trim();
    if (!question) return;

    try {
        addMessage(question, true); // Show user's message
        questionInput.value = '';

        const loadingDiv = showLoading(); // Show loading indicator

        // Send request to backend
        const response = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: question }),
        });

        loadingDiv.remove(); // Remove loading indicator

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        addMessage(data.response); // Add bot's response

    } catch (error) {
        console.error('Error in sendQuestion:', error);
        addMessage('Sorry, there was an error processing your question. Please check if the backend server is running (localhost:8000) and try again.');
    }
}
