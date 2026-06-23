const express = require('express');
const { WebhookClient, EmbedBuilder } = require('discord.js');
require('dotenv').config();

const app = express();
app.use(express.json());

// Initialize Discord Webhook Client using environment variables for safety
const webhookClient = new WebhookClient({ url: process.env.DISCORD_WEBHOOK_URL });

app.post('/api/reports', async (req, res) => {
    const { reporter, target, reason } = req.body;

    if (!reporter || !target || !reason) {
        return res.status(400).json({ error: 'Missing report details.' });
    }

    try {
        // Create a clean embed for staff review
        const embed = new EmbedBuilder()
            .setTitle('🚨 New In-Game Report')
            .setColor(0xFF0000)
            .addFields(
                { name: 'Reporter', value: reporter, inline: true },
                { name: 'Suspect', value: target, inline: true },
                { name: 'Reason', value: reason }
            )
            .setTimestamp();

        await webhookClient.send({ embeds: [embed] });
        return res.status(200).json({ status: 'Success', message: 'Report broadcasted to staff Discord.' });
    } catch (error) {
        console.error('Failed to send Discord notification:', error);
        return res.status(500).json({ error: 'Internal server error.' });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Report API listening on port ${PORT}`));
