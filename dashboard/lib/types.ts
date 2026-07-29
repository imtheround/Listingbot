// TypeScript types mirroring backend Pydantic models.
// Update this whenever the backend response shapes change.

// --- Auth ---
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
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
