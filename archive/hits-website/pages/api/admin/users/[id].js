import { requireAdmin } from "../../../../lib/adminAuth";
import database from "../../../../lib/database";

export default requireAdmin(async function handler(req, res) {
  const { id } = req.query;

  if (req.method === "PATCH") {
    const { premium } = req.body;

    try {
      await database.updateUserPremium(id, premium);
      return res.status(200).json({ message: "User updated successfully" });
    } catch (error) {
      console.error("Error updating user:", error);
      return res.status(500).json({ message: "Internal server error" });
    }
  }

  return res.status(405).json({ message: "Method not allowed" });
});

