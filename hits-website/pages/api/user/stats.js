import { getServerSession } from "next-auth/next";
import { authOptions } from "../auth/[...nextauth]";
import database from "../../../lib/database";

export default async function handler(req, res) {
  if (req.method !== "GET") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  const session = await getServerSession(req, res, authOptions);

  if (!session) {
    return res.status(401).json({ message: "Unauthorized" });
  }

  try {
    const stats = await database.getUserStats(session.user.id);
    return res.status(200).json(stats);
  } catch (error) {
    console.error("Error fetching user stats:", error);
    return res.status(500).json({ message: "Internal server error" });
  }
}

