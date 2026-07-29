"use client";

import HCaptcha from "@hcaptcha/react-hcaptcha";

interface CaptchaVerificationProps {
  onVerify: (token: string) => void;
  onExpire?: () => void;
  theme?: "light" | "dark";
  className?: string;
}

export function CaptchaVerification({
  onVerify,
  onExpire,
  theme = "dark",
  className,
}: CaptchaVerificationProps) {
  const siteKey = process.env.NEXT_PUBLIC_HCAPTCHA_SITE_KEY;

  if (!siteKey) {
    return null;
  }

  return (
    <div className={className}>
      <HCaptcha
        sitekey={siteKey}
        onVerify={onVerify}
        onExpire={onExpire}
        theme={theme}
      />
    </div>
  );
}
