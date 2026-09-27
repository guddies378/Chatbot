class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button'),
            statusIndicator: document.getElementById('chatbot-status')
        };

        this.state = false;
        this.messages = [];
    }

    display() {
        const { openButton, chatBox, sendButton } = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox));

        sendButton.addEventListener('click', () => this.onSendButton(chatBox));

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox);
            }
        });

        this.checkChatbotStatus();
        this.loadFAQs();
    }

    toggleState(chatbox) {
        this.state = !this.state;

        if (this.state) {
            chatbox.classList.add('chatbox--active');
        } else {
            chatbox.classList.remove('chatbox--active');
        }
    }

    getCurrentTimestamp() {
        const now = new Date();
        return now.toLocaleString();
    }

    onSendButton(chatbox) {
        const textField = chatbox.querySelector('input');
        let text1 = textField.value;
        if (text1 === "") {
            return;
        }

        // Hide FAQ section when the user starts the conversation
        document.getElementById('faq-section').style.display = 'none';

        let msg1 = { name: "User", message: text1, timestamp: this.getCurrentTimestamp() };
        this.messages.push(msg1);
        this.updateChatText(chatbox); // Update chat text immediately to show user's message

        fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(r => {
            if (!r.ok) {
                throw new Error('Network response was not ok');
            }
            return r.json();
        })
        .then(r => {
            let msg2 = { name: "University Chatbot", message: r.answer, timestamp: this.getCurrentTimestamp() };
            this.messages.push(msg2);
            this.updateChatText(chatbox);
            textField.value = '';
            this.loadFAQs(); // Reload FAQs after each interaction
        })
        .catch((error) => {
            console.error('Error:', error);
            // Keep the chat active even if there's an error
            this.updateChatText(chatbox);
            textField.value = '';
        });
    }

    updateChatText(chatbox) {
        var html = '';
        this.messages.forEach(function(item) {
            if (item.name === "University Chatbot") {
                // Convert URLs in the message to clickable links
                const messageWithLinks = item.message.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
                // Convert numbered lists
                const messageWithLists = messageWithLinks.replace(/(\d+\.\s)/g, '<br>$1');
                html += '<div class="message-container operator"><div class="messages__item messages__item--operator">' + messageWithLists + '</div>';
                html += '<div class="messages__timestamp operator-timestamp">' + item.timestamp + '</div></div>';
            } else if (item.name === "User") {
                html += '<div class="message-container visitor"><div class="messages__item messages__item--visitor">' + item.message + '</div>';
                html += '<div class="messages__timestamp visitor-timestamp">' + item.timestamp + '</div></div>';
            }
        });
    
        const chatmessage = chatbox.querySelector('#chat-messages');
        chatmessage.innerHTML = html;
        chatmessage.scrollTop = chatmessage.scrollHeight; // Scroll to the bottom
    }
    
    checkChatbotStatus() {
        fetch('http://127.0.0.1:5000/predict', {
            method: 'OPTIONS',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
        .then(r => {
            if (r.ok) {
                this.args.statusIndicator.textContent = 'Online';
                this.args.statusIndicator.classList.remove('offline');
                this.args.statusIndicator.classList.add('online');
            } else {
                throw new Error('Chatbot is offline');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            this.args.statusIndicator.textContent = 'Offline';
            this.args.statusIndicator.classList.remove('online');
            this.args.statusIndicator.classList.add('offline');
        });
    }
    loadFAQs() {
        fetch('http://127.0.0.1:5000/faqs')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (!Array.isArray(data)) {
                    throw new Error('Invalid data format');
                }
                const faqList = document.getElementById('faq-list');
                faqList.innerHTML = ''; // Clear existing FAQs
                const excludedTags = ["greeting", "thanks", "goodbye"];
                let faqCount = 0;

                // Filter out excluded tags and shuffle the intents
                const filteredIntents = data.filter(intent => intent && intent.tag && intent.patterns && !excludedTags.includes(intent.tag));
                const shuffledIntents = filteredIntents.sort(() => 0.5 - Math.random());

                shuffledIntents.forEach(intent => {
                    if (faqCount < 6) {
                        intent.patterns.forEach(pattern => {
                            if (faqCount < 6) {
                                const li = document.createElement('li');
                                li.classList.add('faq-item');
                                li.textContent = pattern;
                                li.addEventListener('click', () => {
                                    const textField = document.querySelector('.chatbox__support input');
                                    textField.value = pattern;
                                    this.onSendButton(document.querySelector('.chatbox__support'));
                                });
                                faqList.appendChild(li);
                                faqCount++;
                            }
                        });
                    }
                });
            })
            .catch(error => console.error('Error loading FAQs:', error));
    }

}

const chatbox = new Chatbox();
chatbox.display();