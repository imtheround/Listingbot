import database from "../../../lib/database";
import jwt from "jsonwebtoken";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ message: "Username and password required" });
  }

  try {
    const admin = await database.validateAdmin(username, password);
    
    if (admin) {
      // Create JWT token for admin session
      const token = jwt.sign(
        { 
          adminId: admin.id, 
          username: admin.username,
          isAdmin: true 
        },
        process.env.NEXTAUTH_SECRET,
        { expiresIn: "24h" }
      );

      // Set HTTP-only cookie
      res.setHeader("Set-Cookie", [
        `admin-token=${token}; HttpOnly; Path=/; Max-Age=86400; SameSite=Strict${
          process.env.NODE_ENV === "production" ? "; Secure" : ""
        }`
      ]);

      return res.status(200).json({ 
        message: "Login successful",
        admin: {
          id: admin.id,
          username: admin.username
        }
      });
    } else {
      return res.status(401).json({ message: "Invalid credentials" });
    }
  } catch (error) {
    console.error("Admin login error:", error);
    return res.status(500).json({ message: "Internal server error" });
  }
}

