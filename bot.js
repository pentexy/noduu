/**
 * XP Farm Bot with Swimming Capability
 * Server: 54.169.77.84:25565
 * Author: RareAura Automation Setup
 */

const mineflayer = require('mineflayer');
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder');

const bot = mineflayer.createBot({
  host: '54.169.77.84',
  port: 25565,
  username: 'FarmBot1', // Replace with bot username (premium or cracked)
});

bot.loadPlugin(pathfinder);

// ====== On Bot Spawn ======
bot.on('spawn', () => {
  const mcData = require('minecraft-data')(bot.version);
  const defaultMove = new Movements(bot, mcData);

  // ====== Movement Configuration ======
  defaultMove.allowSprinting = true;
  defaultMove.canSwim = true; // Enable swimming
  defaultMove.liquidCost = 1; // Treat water as normal terrain
  defaultMove.allow1by1towers = false;
  defaultMove.allowParkour = false;
  defaultMove.scafoldingBlocks = [];

  bot.chat('Bot online. Moving to farm location...');

  // ====== Move to Farm Coordinates ======
  const farmGoal = new goals.GoalBlock(-422, 64, -1480);
  bot.pathfinder.setMovements(defaultMove);
  bot.pathfinder.setGoal(farmGoal);

  // ====== Health Check Loop ======
  setInterval(() => {
    if (bot.food < 15) {
      eatFood();
    }
  }, 5000);
});

// ====== Command Listener (Only RareAura) ======
bot.on('chat', (username, message) => {
  if (username !== 'RareAura') return;

  const mcData = require('minecraft-data')(bot.version);
  const defaultMove = new Movements(bot, mcData);

  // Enable swimming in follow mode too
  defaultMove.allowSprinting = true;
  defaultMove.canSwim = true;
  defaultMove.liquidCost = 1;
  defaultMove.allow1by1towers = false;
  defaultMove.allowParkour = false;
  defaultMove.scafoldingBlocks = [];

  if (message === '/follow') {
    const target = bot.players['RareAura']?.entity;
    if (!target) {
      bot.chat("Can't see you, RareAura!");
      return;
    }
    bot.chat('Following you, RareAura...');
    bot.pathfinder.setMovements(defaultMove);
    const goal = new goals.GoalFollow(target, 1);
    bot.pathfinder.setGoal(goal, true);
  }

  if (message === '/stop') {
    bot.chat('Stopping here, RareAura.');
    bot.pathfinder.setGoal(null);
  }
});

// ====== Eat Food Function ======
function eatFood() {
  const foodItem = bot.inventory.items().find(item =>
    item.name.includes('bread') ||
    item.name.includes('apple') ||
    item.name.includes('cooked')
  );

  if (foodItem) {
    bot.equip(foodItem, 'hand', (err) => {
      if (err) {
        bot.chat("Couldn't equip food.");
        return;
      }
      bot.consume((err) => {
        if (err) bot.chat("Couldn't eat food.");
        else bot.chat('Eating food to regain health.');
      });
    });
  } else {
    bot.chat('No food found in inventory!');
  }
}

// ====== Error Handling ======
bot.on('error', err => console.log('Bot Error:', err));
bot.on('kicked', reason => console.log('Bot Kicked:', reason));
