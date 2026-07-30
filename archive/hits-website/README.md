# Hits Manager

A Discord-integrated hits management platform built with Next.js, featuring user authentication, hit tracking, and an admin panel.

## Features

### User Features
- **Discord OAuth Authentication**: Secure login using Discord accounts
- **Hit Management**: Create, track, and manage hits with different types and statuses
- **Personal Dashboard**: View personal statistics and hit history
- **Real-time Stats**: Track completed, pending, and failed hits
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### Admin Features
- **Admin Panel**: Secure password-based admin authentication
- **User Management**: View all users, manage premium status
- **Hit Oversight**: Monitor all hits across the platform
- **Global Statistics**: View platform-wide metrics and analytics
- **Database Integration**: Shares data with existing Discord bot

## Technology Stack

- **Frontend**: Next.js 15, React 19, Tailwind CSS
- **Authentication**: NextAuth.js with Discord provider, JWT for admin sessions
- **Database**: SQLite3 (shared with Discord bot)
- **Styling**: Custom black theme with animations and responsive design
- **Deployment**: Ready for production deployment

## Setup Instructions

### Prerequisites
- Node.js 20+
- Discord Application with OAuth2 configured
- Existing Discord bot database (optional)

### Installation

1. **Clone and install dependencies**:
   ```bash
   cd hits-website
   npm install
   ```

2. **Configure environment variables**:
   Create `.env.local` file:
   ```env
   # Discord OAuth Configuration
   DISCORD_CLIENT_ID=your_discord_client_id_here
   DISCORD_CLIENT_SECRET=your_discord_client_secret_here

   # NextAuth Configuration
   NEXTAUTH_URL=http://localhost:3000
   NEXTAUTH_SECRET=your_nextauth_secret_here

   # Admin Configuration
   ADMIN_PASSWORD_SALT=your_admin_salt_here
   ```

3. **Discord Application Setup**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application or use existing one
   - Add OAuth2 redirect URI: `http://localhost:3000/api/auth/callback/discord`
   - Copy Client ID and Client Secret to `.env.local`

4. **Database Setup**:
   - The application will automatically create necessary tables
   - Default admin credentials: `admin` / `admin123`
   - To use existing Discord bot database, update the database path in `lib/database.js`

### Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Database Schema

The application extends the existing Discord bot database with additional tables:

- **website_admins**: Admin user credentials
- **hits**: Hit tracking and management
- **user_sessions**: User session management
- **website_settings**: Application configuration

Existing bot tables are preserved and shared:
- **autosecure**: User data and settings
- **profiles**: User profiles
- **embeds**: Custom embeds
- And other bot-specific tables

## Usage

### User Access
1. Visit the website
2. Click "Login with Discord"
3. Authorize the application
4. Access dashboard to manage hits and view stats

### Admin Access
1. Visit `/admin/login`
2. Login with admin credentials (default: admin/admin123)
3. Access admin panel for user and hit management

### API Endpoints

#### User APIs
- `GET /api/user/stats` - Get user statistics
- `GET /api/user/hits` - Get user hits
- `POST /api/user/hits` - Create new hit
- `PATCH /api/hits/[id]` - Update hit status
- `DELETE /api/hits/[id]` - Delete hit

#### Admin APIs
- `POST /api/admin/login` - Admin authentication
- `GET /api/admin/verify` - Verify admin session
- `GET /api/admin/stats` - Global statistics
- `GET /api/admin/users` - All users
- `GET /api/admin/hits` - All hits
- `PATCH /api/admin/users/[id]` - Update user premium status

## Features in Detail

### Hit Management
- **Hit Types**: Website, API, Database, Server, Application, Network, Other
- **Status Tracking**: Pending, Completed, Failed
- **Notes**: Additional details and comments
- **Timestamps**: Creation and completion tracking

### User Dashboard
- **Statistics Cards**: Total, completed, pending, and failed hits
- **Hit List**: Interactive list with status updates
- **Quick Actions**: Mark hits as completed or failed
- **Responsive Design**: Mobile-friendly interface

### Admin Panel
- **Overview Tab**: Global statistics and recent activity
- **Users Tab**: User management with premium status control
- **Hits Tab**: Complete hit oversight and monitoring
- **Real-time Data**: Live updates from shared database

### Security Features
- **Discord OAuth**: Secure authentication via Discord
- **JWT Tokens**: Secure admin session management
- **Password Hashing**: bcrypt for admin password security
- **Session Management**: Automatic session expiration
- **CORS Protection**: Secure API endpoints

## Customization

### Styling
- Black theme with blue accents
- Tailwind CSS for responsive design
- Custom animations and transitions
- Hover effects and micro-interactions

### Database
- SQLite3 for development
- Easy migration to PostgreSQL/MySQL for production
- Shared schema with Discord bot
- Automatic table creation and migration

## Deployment

The application is ready for deployment on platforms like:
- Vercel (recommended for Next.js)
- Netlify
- Railway
- Self-hosted servers

### Environment Variables for Production
Update `NEXTAUTH_URL` to your production domain and ensure all secrets are properly configured.

## Support

For issues or questions:
1. Check the console for error messages
2. Verify environment variables are correctly set
3. Ensure Discord application is properly configured
4. Check database connectivity and permissions

## License

This project is provided as-is for educational and development purposes.

