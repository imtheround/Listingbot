import { requireAdmin } from "../../../lib/adminAuth";
import database from "../../../lib/database";

export default requireAdmin(async function handler(req, res) {
  if (req.method !== "GET") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  try {
    const stats = await database.getGlobalStats();
    return res.status(200).json(stats);
  } catch (error) {
    console.error("Error fetching admin stats:", error);
    return res.status(500).json({ message: "Internal server error" });
  }
});

