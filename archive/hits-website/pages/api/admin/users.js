import { requireAdmin } from "../../../lib/adminAuth";
import database from "../../../lib/database";

export default requireAdmin(async function handler(req, res) {
  if (req.method !== "GET") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  try {
    const users = await database.getAllUsers();
    return res.status(200).json(users);
  } catch (error) {
    console.error("Error fetching users:", error);
    return res.status(500).json({ message: "Internal server error" });
  }
});

