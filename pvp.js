/**
 * RareAura Beast PvP + Mob Killer Bot - 100 CPS Version
 * Author: RareAura Final Drop
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

let masterName = 'RareAura';
let attackTarget = null;
let playerHitCount = {};

// ====== On Spawn ======
bot.once('spawn', () => {
  bot.chat('✅ RareAura Beast Bot Spawned with 100 CPS.');
});

// ====== Auto Eat Loop ======
setInterval(async () => {
  if (bot.food < 15) {
    const food = bot.inventory.items().find(i =>
      i.name.includes('bread') || i.name.includes('apple') || i.name.includes('cooked')
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

// ====== Follow + Protect Loop ======
setInterval(() => {
  const master = bot.players[masterName]?.entity;
  if (!master) return;

  const dist = bot.entity.position.distanceTo(master.position);

  // Follow master if far
  if (dist > 6) {
    bot.pathfinder.setMovements(defaultMove);
    bot.pathfinder.setGoal(new goals.GoalFollow(master, 3));
  }

  // Check for mob attackers near master
  const mobAttackers = Object.values(bot.entities).filter(e =>
    e.type === 'mob' &&
    e.position.distanceTo(master.position) < 4
  );

  if (mobAttackers.length > 0) {
    attackTarget = mobAttackers[0];
    bot.chat(`🛡️ Protecting RareAura from ${attackTarget.name}`);
    engageNoEscapeMode();
  }

}, 1000);

// ====== Player Attack Detection ======
bot.on('entitySwingArm', (entity) => {
  const master = bot.players[masterName]?.entity;
  if (!master || !entity) return;

  if (entity.type === 'player' && entity.username !== bot.username) {
    const dist = entity.position.distanceTo(master.position);
    if (dist < 5) {
      if (!playerHitCount[entity.username]) playerHitCount[entity.username] = 0;
      playerHitCount[entity.username] += 1;

      if (playerHitCount[entity.username] >= 3) {
        attackTarget = entity;
        bot.chat(`⚔️ Player ${entity.username} attacked RareAura 3 times. Engaging!`);
        engageNoEscapeMode();
      }
    }
  }
});

// ====== Engage No Escape Mode (100 CPS) ======
function engageNoEscapeMode() {
  if (!attackTarget) return;

  const axe = bot.inventory.items().find(i => i.name.includes('axe'));
  if (axe) bot.equip(axe, 'hand');
  else bot.chat('⚠️ No axe equipped, attacking barehanded.');

  const beastLoop = setInterval(() => {
    if (!attackTarget || !attackTarget.isValid) {
      clearInterval(beastLoop);
      attackTarget = null;
      bot.setControlState('sprint', false);
      bot.setControlState('forward', false);
      bot.chat('✅ Target eliminated. Returning to RareAura.');
      pvpExperience.kills += 1;
      fs.writeFileSync(expFile, JSON.stringify(pvpExperience, null, 2));
      return;
    }

    const dist = bot.entity.position.distanceTo(attackTarget.position);

    // Chase if far
    if (dist > 3) {
      bot.pathfinder.setMovements(defaultMove);
      bot.pathfinder.setGoal(new goals.GoalFollow(attackTarget, 1), true);
      bot.setControlState('sprint', true);
      bot.setControlState('forward', true);
    } else {
      // Stop moving and attack with 100 CPS
      bot.setControlState('sprint', false);
      bot.setControlState('forward', false);

      // Critical jump hits
      if (bot.entity.onGround) {
        bot.setControlState('jump', true);
        setTimeout(() => bot.setControlState('jump', false), 150);
      }

      // True 100 CPS: attack once every 10ms
      bot.attack(attackTarget);
    }

  }, 10); // every 10ms = 100 CPS
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
        // Silent fail
      }
    }
  }
});

// ====== Error Handling ======
bot.on('kicked', console.log);
bot.on('error', console.log);
