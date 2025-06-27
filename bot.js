/**
 * Farm Bot with Auto-Go, Prefix Commands, and Alive Check
 * Author: RareAura Automation Setup
 */

const mineflayer = require('mineflayer');
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder');
const Vec3 = require('vec3');

const bot = mineflayer.createBot({
  host: '54.169.77.84',
  port: 25565,
  username: 'FarmBot1',
});

bot.loadPlugin(pathfinder);

bot.on('spawn', () => {
  const mcData = require('minecraft-data')(bot.version);
  const defaultMove = new Movements(bot, mcData);

  defaultMove.allowSprinting = true;
  defaultMove.canSwim = true;
  defaultMove.liquidCost = 1;

  bot.chat('Bot online. Going to farm coords...');

  // Go directly to farm coords on spawn
  const farmGoal = new goals.GoalBlock(-422, 64, -1480);
  bot.pathfinder.setMovements(defaultMove);
  bot.pathfinder.setGoal(farmGoal);

  setInterval(() => {
    if (bot.food < 15) eatFood();
  }, 5000);
});

// ====== Chat Commands ======
bot.on('chat', async (username, message) => {
  if (username !== 'RareAura') return;
  if (!message.startsWith('!')) return;

  const command = message.slice(1).trim().toLowerCase();

  const mcData = require('minecraft-data')(bot.version);
  const defaultMove = new Movements(bot, mcData);
  defaultMove.allowSprinting = true;
  defaultMove.canSwim = true;
  defaultMove.liquidCost = 1;

  if (command === 'follow') {
    const target = bot.players['RareAura']?.entity;
    if (!target) {
      bot.chat("Can't see you, RareAura!");
      return;
    }
    bot.chat('Following you...');
    bot.pathfinder.setMovements(defaultMove);
    const goal = new goals.GoalFollow(target, 1);
    bot.pathfinder.setGoal(goal, true);
  }

  if (command === 'stop') {
    bot.chat('Stopping here.');
    bot.pathfinder.setGoal(null);
  }

  if (command === 'eat') {
    eatFood();
  }

  if (command === 'tcords') {
    const pos = bot.entity.position;
    bot.chat(`I am at X:${pos.x.toFixed(1)} Y:${pos.y.toFixed(1)} Z:${pos.z.toFixed(1)}`);
  }

  if (command === 'goto') {
    bot.chat('Going to farm coordinates...');
    const farmGoal = new goals.GoalBlock(-422, 64, -1480);
    bot.pathfinder.setMovements(defaultMove);
    bot.pathfinder.setGoal(farmGoal);
  }

  if (command === 'alive') {
    bot.chat('I am alive.');
  }
});

// ====== Eat Food ======
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
        else bot.chat('Eating food.');
      });
    });
  } else {
    bot.chat('No food found!');
  }
}

// ====== Error Handling ======
bot.on('error', err => console.log('Bot Error:', err));
bot.on('kicked', reason => console.log('Bot Kicked:', reason));
