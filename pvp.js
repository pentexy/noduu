/**
 * RareAura Beast PvP + Mob Killer Bot - No Escape Mode + Accurate Clutch
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
let previousY = null;

// ====== Go to specific spawn point when spawned ======
bot.once('spawn', async () => {
  const spawnPos = new Vec3(84, 63, 442);
  bot.pathfinder.setMovements(defaultMove);
  bot.pathfinder.setGoal(new goals.GoalBlock(spawnPos.x, spawnPos.y, spawnPos.z));
  bot.chat('✅ Arrived at spawn position.');
});

// ====== Auto Eat Loop ======
setInterval(async () => {
  if (bot.food < 15) {
    const food = bot.inventory.items().find(i =>
      i.name.includes('bread') ||
      i.name.includes('apple') ||
      i.name.includes('cooked')
    );
    if (food) {
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

// ====== Equip Axe Command ======
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

  // ====== !set command to right-click nearest bed ======
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

  // ====== !tclu command to test clutch ======
  if (message === '!tclu') {
    const stone = bot.inventory.items().find(i => i.name.includes('stone') || i.name.includes('dirt'));
    if (!stone) {
      bot.chat('No blocks to build a tower for clutch test.');
      return;
    }

    // Build up 10 blocks
    bot.chat('🧪 Starting clutch test...');
    for (let i = 0; i < 10; i++) {
      const below = bot.entity.position.offset(0, -1, 0);
      try {
        await bot.equip(stone, 'hand');
        await bot.placeBlock(bot.blockAt(below), new Vec3(0, 1, 0));
        await bot.look(bot.entity.yaw, -Math.PI / 2, true);
      } catch (err) {
        bot.chat('❌ Tower build failed: ' + err.message);
        return;
      }
    }

    // Jump down for clutch
    bot.setControlState('jump', true);
    setTimeout(() => bot.setControlState('jump', false), 500);
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
      bot.pathfinder.setMovements(defaultMove);
      bot.pathfinder.setGoal(new goals.GoalFollow(target, 0.5), true);
      bot.setControlState('sprint', true);
      bot.setControlState('forward', true);
    } else {
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

// ====== MLG Clutch with accurate previousY tracking ======
bot.on('physicsTick', async () => {
  if (previousY === null) previousY = bot.entity.position.y;

  if (bot.entity.velocity.y < -0.5 && bot.entity.position.y < previousY - 4) {
    const waterBucket = bot.inventory.items().find(i => i.name.includes('bucket'));
    if (waterBucket) {
      try {
        await bot.equip(waterBucket, 'hand');
        const below = bot.entity.position.offset(0, -1, 0);
        await bot.placeBlock(bot.blockAt(below), new Vec3(0, 1, 0));
        bot.chat('💧 MLG Clutch!');
      } catch (err) {
        // Silent fail if cannot clutch
      }
    }
  }

  previousY = bot.entity.position.y;
});

// ====== Error Handling ======
bot.on('kicked', console.log);
bot.on('error', console.log);
