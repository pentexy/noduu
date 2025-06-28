/**
 * RareAura Beast PvP + Mob Killer Bot - No Escape Mode + Auto Tower Heal Clutch
 * Author: RareAura
 */

const mineflayer = require('mineflayer');
const fs = require('fs');
const path = require('path');
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder');
const Vec3 = require('vec3');

const bot = mineflayer.createBot({
  host: '51.20.105.167',
  port: 25565,
  username: 'RareAuraNoEscape',
  version: '1.21'
});

bot.loadPlugin(pathfinder);

const mcData = require('minecraft-data')(bot.version);
const defaultMove = new Movements(bot, mcData);

const expFile = path.join(__dirname, 'pvp_experience.json');
let pvpExperience = { kills: 0 };
if (fs.existsSync(expFile)) {
  pvpExperience = JSON.parse(fs.readFileSync(expFile));
}

let target = null;
let beastInterval = null;
let lastY = 0;

// ====== Go to specific spawn point when spawned ======
bot.once('spawn', async () => {
  const spawnPos = new Vec3(84, 63, 442);
  bot.pathfinder.setMovements(defaultMove);
  bot.pathfinder.setGoal(new goals.GoalBlock(spawnPos.x, spawnPos.y, spawnPos.z));
  bot.chat('✅ Arrived at spawn position.');
  lastY = bot.entity.position.y;
});

// ====== Auto Eat + Tower Heal Clutch ======
setInterval(async () => {
  const food = bot.inventory.items().find(i =>
    i.name.includes('bread') ||
    i.name.includes('apple') ||
    i.name.includes('cooked')
  );

  if (bot.food < 4) {
    if (target) {
      // PvP ongoing, tower heal clutch
      bot.chat('🍗 Low food during PvP, building tower to heal + clutch!');
      await buildTowerAndClutch(6);
    } else if (food) {
      try {
        await bot.equip(food, 'hand');
        await bot.consume();
        bot.chat(`🍗 Auto ate ${food.name}`);
      } catch (err) {
        bot.chat("Couldn't auto eat: " + err.message);
      }
    }
  }
}, 5000);

// ====== Equip Axe + Commands ======
bot.on('chat', async (username, message) => {
  if (message === '!take') {
    const axe = bot.inventory.items().find(i => i.name.includes('axe'));
    if (axe) {
      await bot.equip(axe, 'hand');
      bot.chat(`🪓 Axe equipped: ${axe.name}`);
    } else {
      bot.chat('No axe found in inventory.');
    }
  }

  if (message === '!tclu') {
    await buildTowerAndClutch(10);
  }

  if (message === '!set') {
    const bed = bot.findBlock({
      matching: block => block.name.includes('bed'),
      maxDistance: 6
    });
    if (bed) {
      try {
        await bot.activateBlock(bed);
        bot.chat('🛏️ Bed set as spawn point!');
      } catch (err) {
        bot.chat('❌ Failed to set bed spawn: ' + err.message);
      }
    } else {
      bot.chat('No bed found nearby.');
    }
  }
});

// ====== When Bot is Hurt (Players & Mobs) ======
bot.on('entityHurt', (entity) => {
  if (!entity || entity.id !== bot.entity.id) return;

  const attackers = Object.values(bot.entities).filter(e =>
    (e.type === 'player' || e.type === 'mob') &&
    e.position.distanceTo(bot.entity.position) < 4
  );

  if (attackers.length > 0 && !target) {
    target = attackers[0];
    bot.chat(`🔥 New Target Acquired: ${target.username || target.name}`);
    engageBeastMode();
  }
});

// ====== Engage Beast Mode PvP ======
async function engageBeastMode() {
  if (!target) return;

  const axe = bot.inventory.items().find(i => i.name.includes('axe'));
  if (axe) await bot.equip(axe, 'hand');
  else bot.chat('⚠️ No axe equipped, attacking barehanded.');

  beastInterval = setInterval(() => {
    if (!target || !target.isValid) {
      clearInterval(beastInterval);
      target = null;
      bot.setControlState('sprint', false);
      bot.setControlState('forward', false);
      bot.chat('✅ Target slain. Beast mode off.');
      pvpExperience.kills += 1;
      fs.writeFileSync(expFile, JSON.stringify(pvpExperience, null, 2));
      return;
    }

    const dist = bot.entity.position.distanceTo(target.position);

    if (dist > 4) {
      // Chase mode
      bot.pathfinder.setMovements(defaultMove);
      bot.pathfinder.setGoal(new goals.GoalFollow(target, 0.5), true);
      bot.setControlState('sprint', true);
      bot.setControlState('forward', true);
    } else {
      // Attack mode
      bot.setControlState('sprint', false);
      bot.setControlState('forward', false);

      if (bot.entity.onGround) {
        bot.setControlState('jump', true);
        setTimeout(() => bot.setControlState('jump', false), 150);
      }

      for (let i = 0; i < 10; i++) {
        bot.attack(target);
      }
    }

  }, 10);
}

// ====== Accurate Water Bucket Clutch ======
bot.on('physicsTick', async () => {
  if (bot.entity.velocity.y < -0.5 && (lastY - bot.entity.position.y) >= 4) {
    await performWaterClutch();
  }
  lastY = bot.entity.position.y;
});

async function performWaterClutch() {
  const waterBucket = bot.inventory.items().find(i => i.name.includes('bucket'));
  if (waterBucket) {
    try {
      await bot.equip(waterBucket, 'hand');
      const below = bot.entity.position.offset(0, -1, 0);
      await bot.placeBlock(bot.blockAt(below), new Vec3(0, 1, 0));
      bot.chat('💧 MLG Clutch!');
    } catch (err) {
      bot.chat("❌ Failed MLG: " + err.message);
    }
  }
}

// ====== Build Tower and Clutch Function ======
async function buildTowerAndClutch(height) {
  const block = bot.inventory.items().find(i =>
    i.name.includes('stone') || i.name.includes('dirt') || i.name.includes('planks')
  );

  if (!block) {
    bot.chat("❌ No blocks to build tower.");
    return;
  }

  try {
    await bot.equip(block, 'hand');
    for (let i = 0; i < height; i++) {
      const below = bot.blockAt(bot.entity.position.offset(0, -1, 0));
      if (below) await bot.placeBlock(below, new Vec3(0, 1, 0));
      await bot.setControlState('jump', true);
      await bot.waitForTicks(10);
      await bot.setControlState('jump', false);
    }
    bot.chat(`🗼 Built ${height}-block tower, jumping to clutch.`);
    bot.setControlState('sprint', true);
    bot.setControlState('jump', true);
    setTimeout(() => {
      bot.clearControlStates();
    }, 1000);
  } catch (err) {
    bot.chat("❌ Tower build error: " + err.message);
  }
}

// ====== Error Handling ======
bot.on('kicked', console.log);
bot.on('error', console.log);
