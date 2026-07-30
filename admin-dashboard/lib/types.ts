// TypeScript types mirroring backend Pydantic models.
// Update this whenever the backend response shapes change.

// --- Auth ---
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// --- User ---
export interface UserProfile {
  user_id: string;
  google_id: string | null;
  email: string | null;
  name: string;
  avatar_url: string;
  role: "user" | "premium" | "admin" | "banned";
  is_banned: boolean;
  ban_reason: string | null;
  banned_at: string | null;
  banned_by: string | null;
  email_verified: boolean;
  last_login_at: string | null;
  last_login_ip: string | null;
  login_count: number;
  created_at: string;
  updated_at: string;
}

// --- Purchase ---
export interface Purchase {
  id: number;
  user_id: string;
  order_id: string;
  plan: "monthly" | "yearly" | "lifetime";
  price_usd: number;
  currency_paid: string;
  amount_paid: number;
  status: "pending" | "paid" | "expired" | "failed";
  np_invoice_id: string | null;
  license_key: string | null;
  created_at: string;
  paid_at: string | null;
}

export interface PurchaseListResponse {
  purchases: Purchase[];
  total: number;
}

export interface CreateInvoiceRequest {
  plan: "monthly" | "yearly" | "lifetime";
  hcaptcha_token: string;
}

export interface CreateInvoiceResponse {
  invoice_url: string;
  order_id: string;
}

// --- Accounts ---
export interface AccountResponse {
  uid: string;
  username: string;
  email: string | null;
  networth: number | null;
  created_at: string;
}

export interface AccountListResponse {
  accounts: AccountResponse[];
  total: number;
  page: number;
  pages: number;
}

export interface AccountCreateRequest {
  uid: string;
  username: string;
  email?: string | null;
  recovery_code?: string | null;
}

// --- Bots ---
export interface BotResponse {
  id: number;
  user_id: string;
  botnumber: number;
  status: string;
  created_at: string | null;
}

export interface BotDetailResponse extends BotResponse {
  domain: string;
  verified: boolean;
  dmmode: boolean;
  activity: Record<string, unknown> | null;
}

export interface BotCreateRequest {
  token: string;
}

export interface BotUpdateRequest {
  domain?: string;
  activity?: Record<string, unknown> | null;
  dmmode?: boolean;
}

export interface BotRestartResponse {
  success: boolean;
  message: string;
}

// --- Licenses ---
export interface LicenseResponse {
  license_key: string;
  user_id: string;
  expires_at: string;
  is_active: boolean;
}

export interface LicenseRedeemRequest {
  license_key: string;
}

export interface LicenseTransferRequest {
  new_user_id: string;
}

export interface AdminLicenseResponse {
  license_key: string;
  user_id: string | null;
  expires_at: string;
  is_used: boolean;
}

export interface AdminLicenseListResponse {
  licenses: AdminLicenseResponse[];
  total: number;
}

export interface LicenseGenerateRequest {
  count: number;
  expiry: string;
}

export interface LicenseGenerateResponse {
  licenses: string[];
  count: number;
}

// --- Emails ---
export interface EmailMessage {
  id: number;
  sender: string;
  subject: string;
  description: string;
  time: number;
}

export interface EmailListResponse {
  emails: EmailMessage[];
  total: number;
}

export interface WatchRequest {
  email: string;
}

export interface WatchResponse {
  success: boolean;
  message: string;
}

export interface WatchedAddress {
  email: string;
}

export interface WatchedListResponse {
  addresses: WatchedAddress[];
  total: number;
}

// --- Users ---
export interface UserProfileResponse {
  user_id: string;
  permissions: Record<string, unknown>;
  claiming: string;
  rest_split: number;
}

export interface UserSettingsResponse {
  user_id: string;
  showleaderboard: boolean;
}

export interface UserSettingsUpdate {
  showleaderboard?: boolean;
}

export interface PasswordChangeResponse {
  success: boolean;
  message: string;
}

export interface AdminUserResponse {
  user_id: string;
  permissions: Record<string, unknown>;
  claiming: string;
  rest_split: number;
}

export interface AdminUserListResponse {
  users: AdminUserResponse[];
  total: number;
}

// --- Webhooks ---
export interface WebhookResponse {
  id: number;
  url: string;
  events: string[];
  active: boolean;
}

export interface WebhookListResponse {
  webhooks: WebhookResponse[];
  total: number;
}

export interface WebhookCreateRequest {
  url: string;
  events: string[];
  secret?: string | null;
}

// --- Health ---
export interface HealthResponse {
  status: string;
  checks: Record<string, boolean>;
  uptime: number;
}

// --- Dashboard ---
export interface DashboardStats {
  total_accounts: number;
  total_bots: number;
  active_bots: number;
  total_licenses: number;
  active_licenses: number;
  total_users: number;
  uptime_seconds: number;
  health: Record<string, boolean>;
  recent_activity: Array<{
    action?: string;
    target?: string;
    timestamp?: string;
  }>;
}

// --- Audit Log ---
export interface AuditLogEntry {
  id: number;
  timestamp: string;
  actor_id: string;
  action: string;
  target_type: string | null;
  target_id: string | null;
  details: Record<string, unknown> | null;
  success: boolean;
  ip_address: string | null;
}

export interface AuditLogListResponse {
  logs: AuditLogEntry[];
  total: number;
  page: number;
  pages: number;
}
