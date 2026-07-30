export default function PrivacyPage() {
  return (
    <div className="py-20">
      <div className="mx-auto max-w-3xl px-6">
        <h1 className="text-3xl font-bold mb-8">Privacy Policy</h1>
        <div className="prose prose-sm prose-invert max-w-none space-y-6 text-xs text-muted-foreground leading-relaxed">
          <p><strong className="text-foreground">Last Updated:</strong> July 29, 2026</p>

          <section>
            <h2 className="text-sm font-semibold text-foreground mb-2">1. Information We Collect</h2>
            <p>We collect: your Google account information (name, email, profile picture) for authentication; account metadata you add to the Service; usage analytics and logs; payment transaction records.</p>
          </section>

          <section>
            <h2 className="text-sm font-semibold text-foreground mb-2">2. How We Use Your Information</h2>
            <p>We use your information to: provide and improve the Service; send security alerts and notifications; process payments; prevent fraud and abuse; comply with legal obligations.</p>
          </section>

          <section>
            <h2 className="text-sm font-semibold text-foreground mb-2">3. Data Storage and Security</h2>
            <p>All sensitive data is encrypted at rest using Fernet encryption. Database access is restricted and logged. We use Redis for caching and session management. Regular backups are performed.</p>
          </section>

          <section>
            <h2 className="text-sm font-semibold text-foreground mb-2">4. Third-Party Services</h2>
            <p>We use: Google OAuth for authentication; NOWPayments for payment processing; Redis for caching; PostgreSQL for data storage. Each third party has their own privacy policy governing their use of your data.</p>
          </section>

          <section>
            <h2 className="text-sm font-semibold text-foreground mb-2">5. Data Sharing</h2>
            <p>We do not sell your personal data. We may share data with: payment processors for transaction completion; law enforcement when required by law; service providers who assist in operating the Service.</p>
          </section>

          <section>
            <h2 className="text-sm font-semibold text-foreground mb-2">6. Data Retention</h2>
            <p>We retain your data for as long as your account is active. Upon account deletion, we remove your personal data within 30 days, except where required by law.</p>
          </section>

          <section>
            <h2 className="text-sm font-semibold text-foreground mb-2">7. Your Rights</h2>
            <p>You have the right to: access your personal data; correct inaccurate data; request deletion of your data; export your data; object to data processing.</p>
          </section>

          <section>
            <h2 className="text-sm font-semibold text-foreground mb-2">8. Cookies</h2>
            <p>We use essential cookies for authentication and session management. We do not use tracking cookies or third-party analytics.</p>
          </section>

          <section>
            <h2 className="text-sm font-semibold text-foreground mb-2">9. Children&apos;s Privacy</h2>
            <p>The Service is not intended for children under 13. We do not knowingly collect data from children under 13.</p>
          </section>

          <section>
            <h2 className="text-sm font-semibold text-foreground mb-2">10. Contact</h2>
            <p>For privacy-related inquiries, contact us via Discord or email at privacy@autosecure.me.</p>
          </section>
        </div>
      </div>
    </div>
  );
}
