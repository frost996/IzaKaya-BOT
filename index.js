const { Client, GatewayIntentBits, EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, PermissionsBitField } = require('discord.js');
const express = require('express');
const app = express();
app.get('/', (req, res) => res.send('IzaKaya Online! 🏮'));
app.listen(process.env.PORT || 3000);

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers
    ]
});

const PREFIX = "!";

client.on('ready', () => { console.log(`${client.user.tag} hazır!`); });

client.on('messageCreate', async (message) => {
    if (message.author.bot) return;

    // Basit test komutu
    if (message.content === "!ping") return message.reply("Pong! 🏮");

    // Yeni Ticket Komutu
    if (message.content === "!kur") {
        if (!message.member.permissions.has(PermissionsBitField.Flags.Administrator)) return;

        const embed = new EmbedBuilder()
            .setTitle("🏮 IzaKaya Destek")
            .setDescription("Oda açmak için aşağıdaki butona tıkla senpai!")
            .setColor("#ffb7c5");

        const btn = new ActionRowBuilder().addComponents(
            new ButtonBuilder()
                .setCustomId('ac')
                .setLabel('Talep Aç')
                .setStyle(ButtonStyle.Success)
        );

        try {
            await message.channel.send({ embeds: [embed], components: [btn] });
            console.log("Mesaj gönderildi!");
        } catch (e) {
            console.log("HATA: Mesaj atılamadı ->", e.message);
            message.reply("Mesaj atarken hata oluştu, loglara bak!");
        }
    }
});

client.on('interactionCreate', async (i) => {
    if (!i.isButton()) return;
    if (i.customId === 'ac') {
        await i.reply({ content: "🏮 Yolun açılıyor, bekle ...", ephemeral: true });
        
        const channel = await i.guild.channels.create({
            name: `oda-${i.user.username}`,
            type: 0,
            permissionOverwrites: [
                { id: i.guild.id, deny: [PermissionsBitField.Flags.ViewChannel] },
                { id: i.user.id, allow: [PermissionsBitField.Flags.ViewChannel, PermissionsBitField.Flags.SendMessages] }
            ]
        });
        
        await channel.send(`${i.user} Hoş geldin! Kapatmak için \`!kapat\` yazabilirsin.`);
    }
});

client.login(process.env.TOKEN);
