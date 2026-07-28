import { getServerSession } from "next-auth/next";
import { authOptions } from "../auth/[...nextauth]";
import database from "../../../lib/database";

export default async function handler(req, res) {
  const session = await getServerSession(req, res, authOptions);

  if (!session) {
    return res.status(401).json({ message: "Unauthorized" });
  }

  if (req.method === "GET") {
    try {
      const hits = await database.getUserHits(session.user.id);
      return res.status(200).json(hits);
    } catch (error) {
      console.error("Error fetching user hits:", error);
      return res.status(500).json({ message: "Internal server error" });
    }
  }

  if (req.method === "POST") {
    const { target, hit_type, notes } = req.body;

    if (!target || !hit_type) {
      return res.status(400).json({ message: "Target and hit type are required" });
    }

    try {
      await database.createHit(session.user.id, target, hit_type, notes || "");
      return res.status(201).json({ message: "Hit created successfully" });
    } catch (error) {
      console.error("Error creating hit:", error);
      return res.status(500).json({ message: "Internal server error" });
    }
  }

  return res.status(405).json({ message: "Method not allowed" });
}

