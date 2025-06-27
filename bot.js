/**
 * Farm Bot with GearUp, DropAll, Respawn Memory & Environment Sense
 * Compatible with Minecraft 1.21
 * Author: RareAura Automation Setup
 */

const mineflayer = require('mineflayer');
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder');
const readline = require('readline');

let bedPosition = null;

const bot = mineflayer.createBot({
  host: '54.169.77.84',
  port: 25565,
  username: 'FarmBot1',
  version: '1.21' // replace if needed
});

bot.loadPlugin(pathfinder);

// ====== Terminal Command Setup ======
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

rl.on('line', input => handleCommand(input.trim().toLowerCase()));

// ====== Bot Ready ======
bot.on('spawn', () => {
  const mcData = require('minecraft-data')(bot.version);
  const defaultMove = new Movements(bot, mcData);
  defaultMove.allowSprinting = true;
  defaultMove.canSwim = true;
  defaultMove.liquidCost = 1;
  defaultMove.canDig = false; // no griefing

  bot.chat('Bot online. Going to farm coords...');
  const farmGoal = new goals.GoalBlock(-422, 64, -1480);
  bot.pathfinder.setMovements(defaultMove);
  bot.pathfinder.setGoal(farmGoal);

  setInterval(async () => {
    if (bot.food < 15) {
      const hasFood = bot.inventory.items().some(item =>
        item.name.includes('bread') ||
        item.name.includes('apple') ||
        item.name.includes('cooked')
      );
      if (hasFood) await eatFood();
    }
  }, 5000);
});

// ====== Chat Command Handler ======
bot.on('chat', async (username, message) => {
  if (username.toLowerCase() !== 'rareaura') return;
  if (!message.startsWith('!')) return;

  handleCommand(message.trim().toLowerCase());
});

// ====== Unified Command Handler ======
async function handleCommand(command) {
  const mcData = require('minecraft-data')(bot.version);
  const defaultMove = new Movements(bot, mcData);
  defaultMove.allowSprinting = true;
  defaultMove.canSwim = true;
  defaultMove.liquidCost = 1;
  defaultMove.canDig = false;

  if (command === '!follow') {
    const target = bot.players['RAREAURA']?.entity;
    if (!target) {
      bot.chat("Can't see RAREAURA!");
      return;
    }
    bot.chat('Following you...');
    bot.pathfinder.setMovements(defaultMove);
    const goal = new goals.GoalFollow(target, 1);
    bot.pathfinder.setGoal(goal, true);
  }

  else if (command === '!stop') {
    bot.chat('Stopping here.');
    bot.pathfinder.setGoal(null);
  }

  else if (command === '!eat') {
    await eatFood();
  }

  else if (command === '!tcords') {
    const pos = bot.entity.position;
    bot.chat(`I am at X:${pos.x.toFixed(1)} Y:${pos.y.toFixed(1)} Z:${pos.z.toFixed(1)}`);
  }

  else if (command === '!goto') {
    bot.chat('Going to farm coords...');
    const farmGoal = new goals.GoalBlock(-422, 64, -1480);
    bot.pathfinder.setMovements(defaultMove);
    bot.pathfinder.setGoal(farmGoal);
  }

  else if (command === '!setrespawn') {
    const pos = bot.entity.position;
    bedPosition = { x: Math.floor(pos.x), y: Math.floor(pos.y), z: Math.floor(pos.z) };
    bot.chat(`Respawn bed position set at X:${bedPosition.x} Y:${bedPosition.y} Z:${bedPosition.z}`);
  }

  else if (command === '!gearup') {
    await gearUp();
  }

  else if (command === '!dropall') {
    await dropAll();
  }

  else if (command === '!alive') {
    bot.chat('I am alive.');
  }

  else {
    console.log('Unknown command:', command);
  }
}

// ====== Eat Food ======
async function eatFood() {
  const foodItem = bot.inventory.items().find(item =>
    item.name.includes('bread') ||
    item.name.includes('apple') ||
    item.name.includes('cooked')
  );

  if (foodItem) {
    try {
      await bot.equip(foodItem, 'hand');
      bot.consume((err) => {
        if (err) {
          bot.chat("Couldn't eat food: " + err.message);
        } else {
          bot.chat(`Eating ${foodItem.name}`);
        }
      });
    } catch (err) {
      bot.chat("Couldn't equip food: " + err.message);
    }
  } else {
    bot.chat('No food found!');
  }
}

// ====== Gear Up (equip all armor and tools) ======
async function gearUp() {
  const armorSlots = ['head', 'torso', 'legs', 'feet'];
  const armorTypes = ['helmet', 'chestplate', 'leggings', 'boots'];
  const hotbarTools = ['sword', 'pickaxe', 'axe', 'shovel'];

  try {
    for (let i = 0; i < armorSlots.length; i++) {
      const slot = armorSlots[i];
      const type = armorTypes[i];
      const item = bot.inventory.items().find(it => it.name.includes(type));
      if (item) {
        await bot.equip(item, slot);
        bot.chat(`Equipped ${item.name} on ${slot}`);
      }
    }

    for (const tool of hotbarTools) {
      const item = bot.inventory.items().find(it => it.name.includes(tool));
      if (item) {
        await bot.equip(item, 'hand');
        bot.chat(`Holding ${item.name}`);
        break;
      }
    }
  } catch (err) {
    bot.chat("Couldn't gear up: " + err.message);
  }
}

// ====== Drop All Items to RAREAURA ======
async function dropAll() {
  const targetPlayer = bot.players['RAREAURA']?.entity;
  if (!targetPlayer) {
    bot.chat("Can't see RAREAURA!");
    return;
  }

  try {
    for (const item of bot.inventory.items()) {
      await bot.tossStack(item);
      bot.chat(`Dropped ${item.name}`);
    }
  } catch (err) {
    bot.chat("Couldn't drop items: " + err.message);
  }
}

// ====== Auto Sleep when RAREAURA sleeps ======
bot.on('playerSleep', async (player) => {
  if (player.username.toLowerCase() !== 'rareaura') return;
  if (!bedPosition) {
    bot.chat('No bed position set. Use !setrespawn first.');
    return;
  }

  const bedBlock = bot.blockAt(bedPosition);
  if (!bedBlock) {
    bot.chat('Bed not found at saved position.');
    return;
  }

  try {
    await bot.sleep(bedBlock);
    bot.chat('Sleeping...');
  } catch (err) {
    bot.chat("Couldn't sleep: " + err.message);
  }
});

// ====== Error Handling ======
bot.on('error', err => {
  if (err.name !== 'PartialReadError') {
    console.log('Bot Error:', err);
  }
});

bot.on('kicked', reason => console.log('Bot Kicked:', reason));
