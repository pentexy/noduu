/**
 * Farm Bot with Wood Collection, Boat Crafting & Swimming
 * Server: 54.169.77.84:25565
 * Author: RareAura Automation Setup
 */

const mineflayer = require('mineflayer');
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder');
const collectBlock = require('mineflayer-collectblock').plugin;
const Vec3 = require('vec3');

const bot = mineflayer.createBot({
  host: '54.169.77.84',
  port: 25565,
  username: 'FarmBot1', // Replace with bot username
});

bot.loadPlugin(pathfinder);
bot.loadPlugin(collectBlock);

// ====== Bot Spawn ======
bot.on('spawn', async () => {
  const mcData = require('minecraft-data')(bot.version);
  const defaultMove = new Movements(bot, mcData);

  defaultMove.allowSprinting = true;
  defaultMove.canSwim = true;
  defaultMove.liquidCost = 1;

  bot.chat('Bot online. Starting wood collection...');

  await collectWoodAndCraftBoat(defaultMove);

  // ====== Move to farm after crafting ======
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

  const mcData = require('minecraft-data')(bot.version);
  const defaultMove = new Movements(bot, mcData);
  defaultMove.allowSprinting = true;
  defaultMove.canSwim = true;
  defaultMove.liquidCost = 1;

  if (message === 'follow') {
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

  if (message === 'stop') {
    bot.chat('Stopping here.');
    bot.pathfinder.setGoal(null);
  }

  if (message === 'eat') {
    eatFood();
  }

  if (message === 'tcords') {
    const pos = bot.entity.position;
    const dist = pos.distanceTo({ x: -422, y: 64, z: -1480 });
    bot.chat(`I am at X:${pos.x.toFixed(1)} Y:${pos.y.toFixed(1)} Z:${pos.z.toFixed(1)} | ${dist.toFixed(1)} blocks from farm.`);
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

// ====== Collect Wood & Craft Boat ======
async function collectWoodAndCraftBoat(defaultMove) {
  try {
    const mcData = require('minecraft-data')(bot.version);

    // Find and collect log block
    const logBlock = bot.findBlock({
      matching: block => block.name.includes('log'),
      maxDistance: 32
    });

    if (!logBlock) {
      bot.chat('No logs nearby to make a boat.');
      return;
    }

    bot.chat('Collecting wood...');
    await bot.collectBlock.collect(logBlock);

    // Craft planks from logs
    const plankRecipe = bot.recipesFor(mcData.itemsByName.oak_planks.id, null, 1)[0];
    if (plankRecipe) {
      await bot.craft(plankRecipe, 1, null);
      bot.chat('Crafted planks.');
    }

    // Craft crafting table
    const craftingTableRecipe = bot.recipesFor(mcData.itemsByName.crafting_table.id, null, 1)[0];
    if (craftingTableRecipe) {
      await bot.craft(craftingTableRecipe, 1, null);
      bot.chat('Crafted crafting table.');
    }

    // Place crafting table
    const craftingTableItem = bot.inventory.items().find(i => i.name.includes('crafting_table'));
    if (craftingTableItem) {
      const targetPos = bot.entity.position.offset(1, -1, 0);
      await bot.equip(craftingTableItem, 'hand');
      await bot.placeBlock(bot.blockAt(targetPos), new Vec3(1, 0, 0));
      bot.chat('Placed crafting table.');
    }

    // Craft boat using placed crafting table
    const boatRecipe = bot.recipesFor(mcData.itemsByName.oak_boat.id, null, 1)[0];
    if (boatRecipe) {
      const craftingTableBlock = bot.findBlock({
        matching: mcData.blocksByName.crafting_table.id,
        maxDistance: 5
      });
      await bot.craft(boatRecipe, 1, craftingTableBlock);
      bot.chat('Crafted boat.');
    }
  } catch (err) {
    bot.chat('Error crafting boat: ' + err.message);
  }
}

// ====== Error Handling ======
bot.on('error', err => console.log('Bot Error:', err));
bot.on('kicked', reason => console.log('Bot Kicked:', reason));
