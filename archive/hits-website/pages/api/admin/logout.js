export default function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Method not allowed" });
  }

  // Clear the admin token cookie
  res.setHeader("Set-Cookie", [
    `admin-token=; HttpOnly; Path=/; Max-Age=0; SameSite=Strict${
      process.env.NODE_ENV === "production" ? "; Secure" : ""
    }`
  ]);

  return res.status(200).json({ message: "Logged out successfully" });
}

