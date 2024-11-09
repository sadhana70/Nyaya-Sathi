// Auth0 configuration
let auth0Client = null;

// Update the Auth0 script import in your HTML first
async function configureAuth0() {
    auth0Client = await auth0.createAuth0Client({
        domain: '',//removed due to github private key issues
        clientId: '',//removed due to github private key issues
        authorizationParams: {
            redirect_uri: window.location.origin,
            audience: ''//removed due to github private key issues
        }
    });
}

// Handle authentication
async function initializeAuth() {
    try {
        await configureAuth0();

        // Check for callback
        if (window.location.search.includes("code=")) {
            try {
                await auth0Client.handleRedirectCallback();
                window.history.replaceState({}, document.title, window.location.pathname);
            } catch (callbackError) {
                console.error("Callback handling error:", callbackError);
            }
        }

        await updateUI();
    } catch (error) {
        console.error("Auth0 initialization error:", error);
        addMessage("Authentication system is currently unavailable. Please try again later.");
    }
}

// Update UI based on authentication state
async function updateUI() {
    try {
        const isAuthenticated = await auth0Client.isAuthenticated();

        // Show login/logout buttons and main-container
        document.getElementById('loginButton').style.display = isAuthenticated ? 'none' : 'block';
        document.getElementById('logoutButton').style.display = isAuthenticated ? 'block' : 'none';
        document.getElementById('main-container').style.display = isAuthenticated ? 'block' : 'none';
        document.getElementById('chatBox').style.display = isAuthenticated ? 'block' : 'none';
        document.getElementById('login-container').style.display = isAuthenticated ? 'none' : 'block'; // Update for login-container visibility

        if (isAuthenticated) {
            const user = await auth0Client.getUser();
            console.log('User logged in:', user);
            initializeChat();
        }
    } catch (error) {
        console.error("Error updating UI:", error);
    }
}

// Login function
async function login() {
    try {
        await auth0Client.loginWithRedirect();
    } catch (error) {
        console.error("Login error:", error);
    }
}

// Logout function
async function logout() {
    try {
        await auth0Client.logout({
            logoutParams: {
                returnTo: window.location.origin
            }
        });
    } catch (error) {
        console.error("Logout error:", error);
    }
}

// DOM Elements
const chatBox = document.getElementById('chatBox');
const questionInput = document.getElementById('questionInput');

// Message handling functions
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
    } else {
        messageDiv.textContent = message;
    }

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message loading';
    loadingDiv.textContent = 'Typing...';
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return loadingDiv;
}

// Updated sendQuestion function with error handling
async function sendQuestion() {
    const question = questionInput.value.trim();
    if (!question) return;

    let loadingDiv;
    try {
        addMessage(question, true);
        questionInput.value = '';

        loadingDiv = showLoading();

        const token = await auth0Client.getTokenSilently({
            authorizationParams: {
                audience: ''//removed due to github private key issues
            }
        });

        // Using port 5000 instead of 8000
        const response = await fetch('http://localhost:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ text: question })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server response:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        loadingDiv.remove();
        addMessage(data.response);

    } catch (error) {
        console.error('Detailed error:', error);
        if (loadingDiv) loadingDiv.remove();
        addMessage('Sorry, there was an error processing your question. Please try again.');
    }
}

// Event listener for Enter key
questionInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendQuestion();
    }
});

// Function to handle suggestion clicks
function askQuestion(question) {
    questionInput.value = question;
    sendQuestion();
}

// Initialize chat function
function initializeChat() {
    chatBox.innerHTML = ''; // Clear any existing messages
    addMessage("👋 नमस्ते! I'm your Women's Rights Assistant. How can I assist you today?");
}

// Initialize Auth0 when page loads
document.addEventListener('DOMContentLoaded', () => {
    initializeAuth();
});
