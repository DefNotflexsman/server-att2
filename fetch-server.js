// Configuration: Change this to the Minecraft server IP you want to track
const SERVER_IP = 'proctorsadministration.com';
const API_URL = `https://mcsrvstat.us{SERVER_IP}`;

/**
 * Fetches server status data from the API and updates the web page DOM.
 */
async function fetchServerStatus() {
    const statusText = document.getElementById('server-status');
    const playerText = document.getElementById('player-count');
    const versionText = document.getElementById('server-version');

    try {
        // Perform an asynchronous HTTP GET request to the API
        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        // Check if the server is online based on the API response
        if (data.online === true) {
            statusText.innerText = "Online";
            statusText.style.color = "#2ecc71"; // Green color

            // Extract player metrics safely using optional chaining
            const currentPlayers = data.players?.online || 0;
            const maxPlayers = data.players?.max || 0;
            playerText.innerText = `${currentPlayers} / ${maxPlayers}`;

            // Display game version
            versionText.innerText = data.version || "Unknown Version";
        } else {
            // Handle case where server is offline
            statusText.innerText = "Offline";
            statusText.style.color = "#e74c3c"; // Red color
            playerText.innerText = "0 / 0";
            versionText.innerText = "N/A";
        }

    } catch (error) {
        // Gracefully catch and log network errors
        console.error("Failed to retrieve Minecraft server status:", error);
        statusText.innerText = "Error Loading Data";
        statusText.style.color = "#f39c12"; // Orange color
    }
}

// Run the function automatically when the web page finishes loading
document.addEventListener('DOMContentLoaded', fetchServerStatus);

// Optional: Refresh the server data automatically every 60 seconds
setInterval(fetchServerStatus, 60000);
