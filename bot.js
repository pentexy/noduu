/**
 * Farm Bot with Terminal Command Input
 * Author: RareAura Automation Setup
 */

const mineflayer = require('mineflayer');
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder');
const readline = require('readline');

const bot = mineflayer.createBot({
  host: '54.169.77.84',
  port: 25565,
  username: 'FarmBot1',
});

bot.loadPlugin(pathfinder);

// ====== Terminal Command Setup ======
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

rl.on('line', handleTerminalCommand);

// ====== Bot Ready ======
bot.on('spawn', () => {
  const mcData = require('minecraft-data')(bot.version);
  const defaultMove = new Movements(bot, mcData);

  defaultMove.allowSprinting = true;
  defaultMove.canSwim = true;
  defaultMove.liquidCost = 1;

  bot.chat('Bot online. Going to farm coords...');

  const farmGoal = new goals.GoalBlock(-422, 64, -1480);
  bot.pathfinder.setMovements(defaultMove);
  bot.pathfinder.setGoal(farmGoal);

  setInterval(() => {
    if (bot.food < 15) eatFood();
  }, 5000);
});

// ====== Terminal Command Handler ======
function handleTerminalCommand(input) {
  const command = input.trim().toLowerCase();
  const mcData = require('minecraft-data')(bot.version);
  const defaultMove = new Movements(bot, mcData);
  defaultMove.allowSprinting = true;
  defaultMove.canSwim = true;
  defaultMove.liquidCost = 1;

  if (command === '!follow') {
    const target = bot.players['RareAura']?.entity;
    if (!target) {
      console.log("Can't see RareAura!");
      bot.chat("Can't see RareAura!");
      return;
    }
    console.log('Following RareAura...');
    bot.chat('Following RareAura...');
    bot.pathfinder.setMovements(defaultMove);
    const goal = new goals.GoalFollow(target, 1);
    bot.pathfinder.setGoal(goal, true);
  }

  else if (command === '!stop') {
    console.log('Stopping bot.');
    bot.chat('Stopping here.');
    bot.pathfinder.setGoal(null);
  }

  else if (command === '!eat') {
    console.log('Bot eating food if available.');
    eatFood();
  }

  else if (command === '!tcords') {
    const pos = bot.entity.position;
    const msg = `I am at X:${pos.x.toFixed(1)} Y:${pos.y.toFixed(1)} Z:${pos.z.toFixed(1)}`;
    console.log(msg);
    bot.chat(msg);
  }

  else if (command === '!goto') {
    console.log('Going to farm coords.');
    bot.chat('Going to farm coords...');
    const farmGoal = new goals.GoalBlock(-422, 64, -1480);
    bot.pathfinder.setMovements(defaultMove);
    bot.pathfinder.setGoal(farmGoal);
  }

  else if (command === '!alive') {
    console.log('Bot is alive.');
    bot.chat('I am alive.');
  }

  else {
    console.log('Unknown command.');
  }
}

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
        console.log("Couldn't equip food.");
        return;
      }
      bot.consume((err) => {
        if (err) {
          bot.chat("Couldn't eat food.");
          console.log("Couldn't eat food.");
        }
        else {
          bot.chat('Eating food.');
          console.log('Eating food.');
        }
      });
    });
  } else {
    bot.chat('No food found!');
    console.log('No food found!');
  }
}

// ====== Bot Events ======
bot.on('error', err => console.log('Bot Error:', err));
bot.on('kicked', reason => console.log('Bot Kicked:', reason));
