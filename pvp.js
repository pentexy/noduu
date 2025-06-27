/**
 * RareAura PvP Bot - Axe Killer AI with AutoEat & MLG Clutch
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
  username: 'RareAuraPVP',
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
});

// ====== When Bot is Hurt by Player ======
bot.on('entityHurt', (entity) => {
  if (!entity || !entity.username || entity.username === bot.username) return;
  if (!target) {
    const attacker = bot.players[entity.username]?.entity;
    if (attacker) {
      target = attacker;
      bot.chat(`🔥 New PvP target: ${entity.username}`);
      engagePvP();
    }
  }
});

// ====== Engage PvP ======
function engagePvP() {
  if (!target) return;

  pvpInterval = setInterval(async () => {
    if (!target || !target.isValid) {
      clearInterval(pvpInterval);
      target = null;
      bot.chat('✅ Target defeated. PvP stopped.');
      pvpExperience.kills += 1;
      fs.writeFileSync(expFile, JSON.stringify(pvpExperience, null, 2));
      return;
    }

    const dist = bot.entity.position.distanceTo(target.position);
    if (dist > 25) {
      bot.chat('❌ Target too far, stopping PvP.');
      clearInterval(pvpInterval);
      target = null;
      return;
    }

    // Move to target
    bot.pathfinder.setMovements(defaultMove);
    bot.pathfinder.setGoal(new goals.GoalFollow(target, 1), true);

    // Jump for critical hit if on ground
    if (bot.entity.onGround) {
      bot.setControlState('jump', true);
      setTimeout(() => bot.setControlState('jump', false), 200);
    }

    // Attack with simulated 100 CPS
    for (let i = 0; i < 10; i++) {
      bot.attack(target);
    }

  }, 10); // 100 CPS (10ms interval)
}

// ====== MLG Clutch ======
bot.on('physicsTick', async () => {
  if (bot.entity.velocity.y < -0.5) { // falling fast
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
});

// ====== Error Handling ======
bot.on('kicked', console.log);
bot.on('error', console.log);
