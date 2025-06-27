/**
 * Final FarmBot: Home/Tower Save, Oxygen AI, Sleep, GearUp, DropAll, Realistic PvP
 * Author: RareAura Automation Setup
 */

const mineflayer = require('mineflayer');
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder');
const readline = require('readline');

let bedPosition = null;
let homePosition = { x: -419, y: 67, z: -1448 }; // Default home
let towerPosition = null;
let pvpActive = false;
let pvpInterval = null;

const bot = mineflayer.createBot({
  host: '54.169.77.84',
  port: 25565,
  username: 'FarmBot1',
  version: '1.21'
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
  defaultMove.canDig = false;

  bot.chat('Bot online. Ready for commands.');

  setInterval(async () => {
    // Oxygen AI
    if (bot.entity.isInWater && bot.oxygenLevel < 6) {
      const pos = bot.entity.position.offset(1, 0, 0);
      bot.pathfinder.setGoal(new goals.GoalBlock(pos.x, pos.y, pos.z), true);
      bot.chat('Low oxygen! Moving sideways to breathe.');
    }

    // Auto Eat
    if (bot.food < 15) {
      const hasFood = bot.inventory.items().some(item =>
        item.name.includes('bread') ||
        item.name.includes('apple') ||
        item.name.includes('melon') ||
        item.name.includes('salmon') ||
        item.name.includes('cooked')
      );
      if (hasFood) await eatFood();
    }
  }, 5000);
});

// ====== Chat Command Handler ======
bot.on('chat', async (username, message) => {
  if (username.toLowerCase() !== 'rareaura') return;
  if (!message.startsWith('!') && !message.startsWith('/')) return;

  handleCommand(message.trim().toLowerCase());
});

// ====== Command Handler ======
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
    bot.pathfinder.setGoal(new goals.GoalFollow(target, 1), true);
  }
    else if (command === '!farmer on') {
  startFarming();
  }

    else if (command === '!farmer off') {
  stopFarming();
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

  else if (command === '!sethome') {
    const pos = bot.entity.position;
    homePosition = { x: Math.floor(pos.x), y: Math.floor(pos.y), z: Math.floor(pos.z) };
    const bed = bot.findBlock({
      matching: block => bot.isABed(block),
      maxDistance: 5
    });
    if (bed) {
      bedPosition = bed.position;
      bot.chat(`Home set at X:${homePosition.x} Y:${homePosition.y} Z:${homePosition.z} with bed saved.`);
    } else {
      bot.chat(`Home set at X:${homePosition.x} Y:${homePosition.y} Z:${homePosition.z} but no bed found nearby.`);
    }
  }

  else if (command === '!settower') {
    const pos = bot.entity.position;
    towerPosition = { x: Math.floor(pos.x), y: Math.floor(pos.y), z: Math.floor(pos.z) };
    bot.chat(`Tower position set at X:${towerPosition.x} Y:${towerPosition.y} Z:${towerPosition.z}`);
  }

  else if (command === '!goto' || command === '/cumbase') {
    bot.chat('Going to home...');
    bot.pathfinder.setMovements(defaultMove);
    bot.pathfinder.setGoal(new goals.GoalBlock(homePosition.x, homePosition.y, homePosition.z));
  }

  else if (command === '!gotower') {
    if (!towerPosition) {
      bot.chat('No tower set yet. Use !settower first.');
      return;
    }
    bot.chat('Going to tower...');
    bot.pathfinder.setMovements(defaultMove);
    bot.pathfinder.setGoal(new goals.GoalBlock(towerPosition.x, towerPosition.y, towerPosition.z));
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

  else if (command === '!pvp') {
    startPVP();
  }

  else if (command === '!pvpop') {
    stopPVP();
  }

  else if (command === '!set') {
    const bed = bot.findBlock({
      matching: block => bot.isABed(block),
      maxDistance: 5
    });

    if (!bed) {
      bot.chat('No bed nearby to set spawn point!');
      return;
    }

    bot.activateBlock(bed).then(() => {
      bot.chat('Respawn point set on bed.');
      bedPosition = bed.position;
    }).catch(err => {
      bot.chat("Couldn't set spawn point: " + err.message);
    });
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
    item.name.includes('melon') ||
    item.name.includes('salmon') ||
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

// ====== Gear Up ======
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

// ====== Drop All Items ======
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


// ====== Farming Module ======
let farmingActive = false;
let farmingInterval = null;

async function startFarming() {
  if (farmingActive) return;
  farmingActive = true;
  bot.chat('🌾 Farming mode enabled.');

  const mcData = require('minecraft-data')(bot.version);
  const wheatID = mcData.blocksByName.wheat.id;
  const seedID = mcData.itemsByName.wheat_seeds.id;
  const craftingTableID = mcData.blocksByName.crafting_table.id;
  const breadRecipe = bot.recipesFor(mcData.itemsByName.bread.id, null, 1, null)[0];

  farmingInterval = setInterval(async () => {
    if (!farmingActive) return;

    // 1. Find grown wheat
    const wheat = bot.findBlock({
      matching: b => b.type === wheatID && b.metadata === 7,
      maxDistance: 6
    });

    if (wheat) {
      await bot.pathfinder.goto(new goals.GoalBlock(wheat.position.x, wheat.position.y, wheat.position.z));
      await bot.dig(wheat);
      bot.chat('🌾 Harvested wheat.');
    }

    // 2. Replant seeds
    const farmland = bot.findBlock({
      matching: block => block.name === 'farmland' && bot.blockAt(block.position.offset(0, 1, 0)).name === 'air',
      maxDistance: 6
    });

    if (farmland) {
      const seeds = bot.inventory.items().find(i => i.type === seedID);
      if (seeds) {
        await bot.equip(seeds, 'hand');
        await bot.placeBlock(farmland, new Vec3(0, 1, 0));
        bot.chat('🌱 Planted seed.');
      }
    }

    // 3. Craft bread if wheat ≥ 3
    const wheatItem = bot.inventory.items().find(i => i.name === 'wheat');
    const table = bot.findBlock({ matching: craftingTableID, maxDistance: 6 });

    if (wheatItem && wheatItem.count >= 3 && breadRecipe && table) {
      await bot.pathfinder.goto(new goals.GoalBlock(table.position.x, table.position.y, table.position.z));
      await bot.craft(breadRecipe, Math.floor(wheatItem.count / 3), table);
      bot.chat('🍞 Crafted bread.');
    }

    // 4. Put bread in nearest chest
    const chestBlock = bot.findBlock({
      matching: block => block.name.includes('chest'),
      maxDistance: 6
    });

    if (chestBlock) {
      const chest = await bot.openChest(chestBlock);
      const bread = bot.inventory.items().find(i => i.name === 'bread');
      if (bread) {
        await chest.deposit(bread.type, null, bread.count);
        bot.chat(`📦 Stored ${bread.count} bread.`);
      }
      chest.close();
    }

  }, 8000); // runs every 8s
}

function stopFarming() {
  if (!farmingActive) return;
  farmingActive = false;
  clearInterval(farmingInterval);
  bot.chat('❌ Farming mode disabled.');
}

// ====== Auto Sleep ======
bot.on('time', () => {
  if ((bot.time.day >= 13000 && bot.time.day <= 23000) && bedPosition) {
    const bedBlock = bot.blockAt(bedPosition);
    if (bedBlock) {
      bot.sleep(bedBlock).then(() => {
        bot.chat('Sleeping...');
      }).catch(err => {
        bot.chat("Couldn't sleep: " + err.message);
      });
    }
  }
});

// ====== Beast Mode PvP ======
function startPVP() {
  if (pvpActive) return;
  pvpActive = true;
  bot.chat('💥 Ultra Beast PvP Activated!');

  pvpInterval = setInterval(async () => {
    if (!pvpActive) return;

    // Heal if low health
    if (bot.health < 15) {
      await eatFood();
    }

    // Find nearest target (mob or player excluding bot itself)
    const target = bot.nearestEntity(entity =>
      (entity.type === 'mob' || entity.type === 'player') &&
      entity.username !== bot.username
    );

    if (target) {
      await bot.lookAt(target.position.offset(0, target.height, 0), true);

      // Jump for critical hit
      if (bot.entity.onGround) {
        bot.setControlState('jump', true);
        setTimeout(() => {
          bot.setControlState('jump', false);
        }, 100);
      }

      bot.attack(target);
      const dist = bot.entity.position.distanceTo(target.position);
      if (dist > 3) {
        const mcData = require('minecraft-data')(bot.version);
        const defaultMove = new Movements(bot, mcData);
        bot.pathfinder.setMovements(defaultMove);
        bot.pathfinder.setGoal(new goals.GoalFollow(target, 1), true);
      }
    }
  }, 10); // near-100 CPS
}

function stopPVP() {
  if (!pvpActive) return;
  pvpActive = false;
  clearInterval(pvpInterval);
  bot.setControlState('jump', false);
  bot.pathfinder.setGoal(null);
  bot.chat('💤 PvP mode deactivated.');
}

// ====== Error Handling ======
bot.on('error', err => {
  if (err.name !== 'PartialReadError') {
    console.log('Bot Error:', err);
  }
});
bot.on('kicked', reason => console.log('Bot Kicked:', reason));
