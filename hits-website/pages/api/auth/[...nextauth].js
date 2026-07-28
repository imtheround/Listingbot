import NextAuth from "next-auth";
import DiscordProvider from "next-auth/providers/discord";
import database from "../../../lib/database";

export const authOptions = {
  providers: [
    DiscordProvider({
      clientId: process.env.DISCORD_CLIENT_ID,
      clientSecret: process.env.DISCORD_CLIENT_SECRET,
      authorization: {
        params: {
          scope: "identify email guilds",
        },
      },
    }),
  ],
  callbacks: {
    async signIn({ user, account, profile }) {
      if (account.provider === "discord") {
        try {
          // Check if user exists in the autosecure table (from Discord bot)
          const existingUser = await database.getUserByDiscordId(user.id);
          
          if (existingUser) {
            // User exists in bot database, allow sign in
            return true;
          } else {
            // User doesn't exist in bot database, create basic entry
            await database.queryParams(
              `INSERT INTO autosecure (user_id, premium, auto_secure, claiming, autosecureEnabled) 
               VALUES (?, ?, ?, ?, ?)`,
              [user.id, "false", 1, 1, 1],
              "run"
            );
            return true;
          }
        } catch (error) {
          console.error("Error during sign in:", error);
          return false;
        }
      }
      return true;
    },
    async jwt({ token, account, profile }) {
      if (account) {
        token.accessToken = account.access_token;
        token.discordId = profile.id;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken;
      session.user.id = token.discordId;
      
      // Get user data from database
      try {
        const userData = await database.getUserByDiscordId(token.discordId);
        if (userData) {
          session.user.premium = userData.premium === "true";
          session.user.autosecureEnabled = userData.autosecureEnabled === 1;
          session.user.domain = userData.domain;
        }
      } catch (error) {
        console.error("Error fetching user data:", error);
      }
      
      return session;
    },
  },
  pages: {
    signIn: "/login",
    error: "/auth/error",
  },
  session: {
    strategy: "jwt",
  },
  secret: process.env.NEXTAUTH_SECRET,
};

export default NextAuth(authOptions);

