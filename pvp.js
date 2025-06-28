/**
 * RareAura Beast PvP + Mob Killer Bot - No Escape Mode + Clutch Trainer
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
let pvpInterval = null;

// ====== Go to spawn point when spawned ======
bot.once('spawn', async () => {
  const spawnPos = new Vec3(84, 63, 442);
  bot.pathfinder.setMovements(defaultMove);
  await bot.pathfinder.goto(new goals.GoalBlock(spawnPos.x, spawnPos.y, spawnPos.z));
  bot.chat('✅ Reached spawn point.');
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

  // ====== !testcl command to build tower, jump, and clutch ======
  if (message === '!testcl') {
    const stone = bot.inventory.items().find(i => i.name.includes('stone') || i.name.includes('dirt') || i.name.includes('block'));
    if (!stone) {
      bot.chat('❌ No blocks in inventory to build tower.');
      return;
    }

    try {
      bot.chat('🧱 Building 10-block tower for clutch test...');
      await bot.equip(stone, 'hand');

      // Build tower of 10 blocks
      for (let i = 0; i < 10; i++) {
        const below = bot.blockAt(bot.entity.position.offset(0, -1, 0));
        await bot.placeBlock(below, new Vec3(0, 1, 0));
        await bot.look(bot.entity.yaw, 0);
        await bot.setControlState('jump', true);
        await bot.waitForTicks(10);
        await bot.setControlState('jump', false);
      }

      bot.chat('⛏️ Tower done, jumping off...');
      bot.setControlState('forward', true);
      setTimeout(() => bot.setControlState('forward', false), 500);

    } catch (err) {
      bot.chat(`❌ Failed tower build: ${err.message}`);
    }
  }
});

// ====== Water Clutch Helper Function ======
async function performWaterClutch() {
  const waterBucket = bot.inventory.items().find(i => i.name.includes('bucket'));
  if (!waterBucket) {
    bot.chat('❌ No water bucket in inventory!');
    return;
  }

  try {
    await bot.equip(waterBucket, 'hand');

    const posBelow = bot.entity.position.offset(0, -1, 0);
    await bot.look(bot.entity.yaw, Math.PI / 2, true); // look straight down
    await bot.placeBlock(bot.blockAt(posBelow), new Vec3(0, 1, 0));

    bot.chat('💧 Water Clutch Successful!');
  } catch (err) {
    bot.chat(`❌ Failed clutch: ${err.message}`);
  }
}

// ====== Auto clutch when falling fast (≥4 block fall) ======
bot.on('physicsTick', async () => {
  if (bot.entity.velocity.y < -0.5 && bot.entity.position.y < bot.entity.previousPosition.y - 4) {
    await performWaterClutch();
  }
});

// ====== When Bot is Hurt (Players & Mobs) ======
bot.on('entityHurt', (entity) => {
  // Check if the bot itself was hurt by an attacker
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

  pvpInterval = setInterval(() => {
    if (!target || !target.isValid) {
      clearInterval(pvpInterval);
      target = null;
      bot.chat('✅ Target slain. Beast mode off.');
      pvpExperience.kills += 1;
      fs.writeFileSync(expFile, JSON.stringify(pvpExperience, null, 2));
      return;
    }

    const dist = bot.entity.position.distanceTo(target.position);

    if (dist > 4) {
      // Sprint to catch up
      bot.setControlState('sprint', true);
      bot.pathfinder.setGoal(new goals.GoalFollow(target, 1), true);
    } else {
      // Stop sprinting, attack
      bot.clearControlStates();
      bot.pathfinder.setGoal(new goals.GoalFollow(target, 0.5), true);

      // Critical jump hits
      if (bot.entity.onGround) {
        bot.setControlState('jump', true);
        setTimeout(() => bot.setControlState('jump', false), 150);
      }

      // Attack with simulated 100 CPS
      for (let i = 0; i < 10; i++) {
        bot.attack(target);
      }
    }

  }, 10); // every 10ms for 100 CPS
}

// ====== Error Handling ======
bot.on('kicked', console.log);
bot.on('error', console.log);
