import { getServerSession } from "next-auth/next";
import { authOptions } from "../auth/[...nextauth]";
import database from "../../../lib/database";

export default async function handler(req, res) {
  const { id } = req.query;
  const session = await getServerSession(req, res, authOptions);

  if (!session) {
    return res.status(401).json({ message: "Unauthorized" });
  }

  if (req.method === "PATCH") {
    const { status, notes } = req.body;

    if (!status) {
      return res.status(400).json({ message: "Status is required" });
    }

    try {
      await database.updateHitStatus(id, status, notes || "");
      return res.status(200).json({ message: "Hit updated successfully" });
    } catch (error) {
      console.error("Error updating hit:", error);
      return res.status(500).json({ message: "Internal server error" });
    }
  }

  if (req.method === "DELETE") {
    try {
      await database.deleteHit(id);
      return res.status(200).json({ message: "Hit deleted successfully" });
    } catch (error) {
      console.error("Error deleting hit:", error);
      return res.status(500).json({ message: "Internal server error" });
    }
  }

  return res.status(405).json({ message: "Method not allowed" });
}

