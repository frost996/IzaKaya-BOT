const { 
    Client, GatewayIntentBits, ActionRowBuilder, ButtonBuilder, 
    ButtonStyle, EmbedBuilder, ChannelType, PermissionFlagsBits, 
    ComponentType 
} = require('discord.js');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds, 
        GatewayIntentBits.GuildMessages, 
        GatewayIntentBits.MessageContent, 
        GatewayIntentBits.GuildMembers
    ]
});

const PREFIX = "!";

client.once('ready', () => {
    console.log(`${client.user.tag} aktif! IzaKaya için hazır.`);
});

// --- 1. TICKET (DESTEK) SİSTEMİ ---
client.on('messageCreate', async (message) => {
    if (message.content === PREFIX + 'ticket-kur') {
        if (!message.member.permissions.has(PermissionFlagsBits.Administrator)) return;

        const embed = new EmbedBuilder()
            .setTitle('🏮 IzaKaya Destek Merkezi')
            .setDescription('Lütfen ihtiyacınız olan kategoriye göre butonlardan birine tıklayın.')
            .setColor(0x5865F2);

        const buttons = new ActionRowBuilder().addComponents(
            new ButtonBuilder().setCustomId('ticket_alim').setLabel('Yetkili Alım').setStyle(ButtonStyle.Primary),
            new ButtonBuilder().setCustomId('ticket_yardim').setLabel('Yardım').setStyle(ButtonStyle.Success),
            new ButtonBuilder().setCustomId('ticket_hata').setLabel('Hata / Öneri').setStyle(ButtonStyle.Danger)
        );

        message.channel.send({ embeds: [embed], components: [buttons] });
    }
});

client.on('interactionCreate', async (interaction) => {
    if (!interaction.isButton()) return;

    if (interaction.customId.startsWith('ticket_')) {
        const type = interaction.customId.split('_')[1];
        const channel = await interaction.guild.channels.create({
            name: `${type}-${interaction.user.username}`,
            type: ChannelType.GuildText,
            permissionOverwrites: [
                { id: interaction.guild.id, deny: [PermissionFlagsBits.ViewChannel] },
                { id: interaction.user.id, allow: [PermissionFlagsBits.ViewChannel, PermissionFlagsBits.SendMessages] },
                { id: process.env.STAFF_ROLE_ID, allow: [PermissionFlagsBits.ViewChannel, PermissionFlagsBits.SendMessages] }
            ]
        });

        await interaction.reply({ content: `Kanalın açıldı: ${channel}`, ephemeral: true });
        channel.send(`Hoş geldin <@${interaction.user.id}>, bir yetkili birazdan ilgilenecektir.`);
    }
});

// --- 2. UYARI SİSTEMİ ---
client.on('messageCreate', async (message) => {
    if (!message.content.startsWith(PREFIX) || message.author.bot) return;
    const args = message.content.slice(PREFIX.length).trim().split(/ +/);
    const command = args.shift().toLowerCase();

    if (command === 'uyar') {
        if (!message.member.permissions.has(PermissionFlagsBits.Administrator)) return;
        const target = message.mentions.members.first();
        if (!target) return message.reply("Lütfen bir yetkiliyi etiketle.");

        const roles = ['Uyarı1', 'Uyarı2', 'Uyarı3'];
        let currentLevel = 0;

        // Mevcut uyarı seviyesini kontrol et
        if (target.roles.cache.find(r => r.name === 'Uyarı1')) currentLevel = 1;
        if (target.roles.cache.find(r => r.name === 'Uyarı2')) currentLevel = 2;

        const nextLevel = currentLevel + 1;
        const roleToAdd = message.guild.roles.cache.find(r => r.name === `Uyarı${nextLevel}`);

        if (!roleToAdd) return message.reply(`Hata: 'Uyarı${nextLevel}' adlı bir rol sunucuda bulunamadı!`);

        try {
            if (nextLevel === 1) {
                await target.roles.add(roleToAdd);
                await target.send("Dikkat et ve bundan sonra daha dikkatli ol.");
                message.channel.send(`${target} kişisine 1. uyarı verildi.`);
            } else if (nextLevel === 2) {
                await target.roles.add(roleToAdd);
                await target.send("Yetkine daha önem ver!");
                message.channel.send(`${target} kişisine 2. uyarı verildi.`);
            } else if (nextLevel === 3) {
                await target.send("3. uyarını aldığın için yetkilerin alındı ve sunucudan uzaklaştırıldın.");
                await target.kick("3 Uyarı Sınırı");
                message.channel.send(`${target} 3 uyarı aldığı için sunucudan atıldı.`);
            }
        } catch (err) {
            message.reply("Mesaj gönderilemedi veya rol verilemedi (Yetki hatası olabilir).");
        }
    }

// --- 3. ÇEKİLİŞ SİSTEMİ ---
    if (command === 'çekiliş') {
        const zaman = parseInt(args[0]); // Saniye cinsinden
        const odul = args.slice(1).join(" ");

        if (!zaman || !odul) return message.reply("Kullanım: `!çekiliş 60 Ödül İsmi` (60 saniye)");

        const cekilisEmbed = new EmbedBuilder()
            .setTitle("🎉 ÇEKİLİŞ BAŞLADI!")
            .setDescription(`Ödül: **${odul}**\nSüre: ${zaman} saniye\nKatılmak için 🎉 tepkisine basın!`)
            .setColor(0xFFA500);

        let msg = await message.channel.send({ embeds: [cekilisEmbed] });
        await msg.react("🎉");

        setTimeout(async () => {
            const reaction = msg.reactions.cache.get("🎉");
            const users = await reaction.users.fetch();
            const winner = users.filter(u => !u.bot).random();

            if (winner) {
                message.channel.send(`Tebrikler ${winner}! **${odul}** kazandın!`);
            } else {
                message.channel.send("Çekilişe kimse katılmadığı için kazanan yok.");
            }
        }, zaman * 1000);
    }
});

client.login(process.env.TOKEN);
