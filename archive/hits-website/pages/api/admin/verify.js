import { verifyAdminToken } from "../../../lib/adminAuth";

export default function handler(req, res) {
  if (req.method !== "GET") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  const admin = verifyAdminToken(req);

  if (admin) {
    return res.status(200).json({ 
      admin: {
        id: admin.adminId,
        username: admin.username
      }
    });
  } else {
    return res.status(401).json({ message: "Not authenticated" });
  }
}

