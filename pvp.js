/**
 * RareAura Beast PvP Protector Bot - Follow & Finish Mode
 * Author: RareAura
 */

const mineflayer = require('mineflayer');
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder');

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
let beastLoop = null;

bot.once('spawn', () => {
  bot.chat('✅ RareAura Protector Bot Spawned.');
  bot.pathfinder.setMovements(defaultMove);
});

// ====== MAIN LOOP ======
setInterval(() => {
  const master = bot.players[masterName]?.entity;
  if (!master) return;

  // FOLLOW RareAura if >5 blocks away
  const dist = bot.entity.position.distanceTo(master.position);
  if (dist > 5) {
    bot.pathfinder.setGoal(new goals.GoalFollow(master, 2));
  }
}, 500);

// ====== Detect if RareAura damages anyone ======
bot.on('entityHurt', (entity) => {
  const master = bot.players[masterName]?.entity;
  if (!master) return;

  // Check if master damaged this entity
  if (entity.hurtByEntity === master.id) {
    attackTarget = entity;
    bot.chat(`🔥 RareAura attacked ${entity.username || entity.name}. Engaging!`);
    engageNoEscapeMode();
  }
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
}, 5000); // checks every 5 seconds

// ====== Engage No Escape Mode ======
function engageNoEscapeMode() {
  if (!attackTarget) return;
  if (beastLoop) return;

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
      bot.pathfinder.setGoal(null);
      bot.setControlState('sprint', false);
      bot.setControlState('forward', false);

      if (bot.entity.onGround) {
        bot.setControlState('jump', true);
        setTimeout(() => bot.setControlState('jump', false), 150);
      }

      for (let i = 0; i < 10; i++) {
        bot.attack(attackTarget);
      }
    }
  }, 10);
}

// ====== ERROR HANDLING ======
bot.on('kicked', console.log);
bot.on('error', console.log);
