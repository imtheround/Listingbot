import { getServerSession } from "next-auth/next";
import { authOptions } from "../pages/api/auth/[...nextauth]";
import database from "./database";

export async function getSession(req, res) {
  return await getServerSession(req, res, authOptions);
}

export async function requireAuth(req, res) {
  const session = await getSession(req, res);
  
  if (!session) {
    return {
      redirect: {
        destination: "/login",
        permanent: false,
      },
    };
  }
  
  return { session };
}

export async function requireAdmin(req, res) {
  // For admin routes, we'll use a different authentication method
  // This will be implemented in the admin panel
  return true;
}

export async function getUserFromSession(session) {
  if (!session?.user?.id) return null;
  
  try {
    const user = await database.getUserByDiscordId(session.user.id);
    return user;
  } catch (error) {
    console.error("Error fetching user from session:", error);
    return null;
  }
}

