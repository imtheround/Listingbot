import jwt from "jsonwebtoken";

export function verifyAdminToken(req) {
  const token = req.cookies["admin-token"];
  
  if (!token) {
    return null;
  }

  try {
    const decoded = jwt.verify(token, process.env.NEXTAUTH_SECRET);
    return decoded.isAdmin ? decoded : null;
  } catch (error) {
    return null;
  }
}

export function requireAdmin(handler) {
  return async (req, res) => {
    const admin = verifyAdminToken(req);
    
    if (!admin) {
      return res.status(401).json({ message: "Admin authentication required" });
    }
    
    req.admin = admin;
    return handler(req, res);
  };
}

