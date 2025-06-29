/**
 * RareAura Beast PvP + Mob Killer Bot - Stable Final Fixed
 * Author: RareAura God Mode Fix + ChatGPT Integration
 */

const mineflayer = require('mineflayer');
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

let masterName = 'RareAura';
let attackTarget = null;
let playerHitCount = {};
let beastLoop = null;

bot.once('spawn', () => {
  bot.chat('✅ RareAura God Mode Bot Spawned.');
  bot.pathfinder.setMovements(defaultMove);
});

// ====== !come command ======
bot.on('chat', (username, message) => {
  if (message.startsWith('!come ')) {
    const args = message.split(' ');
    if (args.length === 4) {
      const x = parseFloat(args[1]);
      const y = parseFloat(args[2]);
      const z = parseFloat(args[3]);
      if (!isNaN(x) && !isNaN(y) && !isNaN(z)) {
        bot.chat(`🚶 Moving to (${x},${y},${z})`);
        bot.pathfinder.setGoal(new goals.GoalBlock(x, y, z));
      } else {
        bot.chat('❌ Invalid coordinates.');
      }
    } else {
      bot.chat('❌ Usage: !come <x> <y> <z>');
    }
  }
});

// ====== MAIN LOOP ======
setInterval(() => {
  const master = bot.players[masterName]?.entity;
  if (!master) {
    // Only warn once every 10s to avoid spam (optional improvement)
    // bot.chat('❌ Cannot find RareAura.');
    return;
  }

  // FOLLOW LOGIC
  const dist = bot.entity.position.distanceTo(master.position);
  if (dist > 5) {
    bot.pathfinder.setGoal(new goals.GoalFollow(master, 2));
  }

  // MOB PROTECTION LOGIC
  const nearbyMobs = Object.values(bot.entities).filter(e =>
    e.type === 'mob' && e.position.distanceTo(master.position) < 4
  );

  if (nearbyMobs.length > 0) {
    attackTarget = nearbyMobs[0];
    engageNoEscapeMode();
  }

}, 500); // every 0.5s

// ====== PLAYER ATTACK DETECTION ======
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

// ====== NO ESCAPE MODE (100 CPS) ======
function engageNoEscapeMode() {
  if (!attackTarget) return;
  if (beastLoop) return; // prevent overlapping

  const axe = bot.inventory.items().find(i => i.name.includes('axe'));
  if (axe) {
    bot.equip(axe, 'hand');
  } else {
    bot.chat('⚠️ No axe equipped, attacking barehanded.');
  }

  beastLoop = setInterval(() => {
    if (!attackTarget || !attackTarget.position) {
      clearInterval(beastLoop);
      beastLoop = null;
      attackTarget = null;
      bot.setControlState('sprint', false);
      bot.setControlState('forward', false);
      bot.chat('✅ Target eliminated.');
      return;
    }

    const dist = bot.entity.position.distanceTo(attackTarget.position);

    if (dist > 3) {
      bot.pathfinder.setGoal(new goals.GoalFollow(attackTarget, 1), true);
      bot.setControlState('sprint', true);
      bot.setControlState('forward', true);
    } else {
      bot.pathfinder.setGoal(null); // stop pathfinder movement
      bot.setControlState('sprint', false);
      bot.setControlState('forward', false);

      if (bot.entity.onGround) {
        bot.setControlState('jump', true);
        setTimeout(() => bot.setControlState('jump', false), 150);
      }

      // Attack target rapidly (simulate ~100 CPS)
      for (let i = 0; i < 10; i++) {
        bot.attack(attackTarget);
      }
    }

  }, 10); // every 10ms for high CPS
}

// ====== ERROR HANDLING ======
bot.on('kicked', console.log);
bot.on('error', console.log);
