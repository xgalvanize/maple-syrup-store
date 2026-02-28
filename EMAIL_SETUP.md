# Email Notifications Setup Guide

Email notifications are now configured. Here's how to set them up:

## Using Gmail (Free - Recommended for Testing)

1. **Enable 2-Factor Authentication** on your Gmail account
   - Go to Google Account → Security → 2-Step Verification

2. **Generate App Password**
   - Go to Google Account → Security → App passwords
   - Select "Mail" and "Other (Custom name)"
   - Name it "Maple Syrup Store"
   - Copy the 16-character password

3. **Update helm-chart/secrets.yaml**
   ```yaml
   backend:
     secrets:
       EMAIL_HOST_USER: "youremail@gmail.com"
       EMAIL_HOST_PASSWORD: "your-16-char-app-password"
       ADMIN_EMAIL: "admin@maplesyrup.co"
   ```

4. **Redeploy**
   ```bash
   ./scripts/rebuild.sh
   ```

## Using SendGrid (Free Tier - 100 emails/day)

1. **Sign up** at sendgrid.com (free tier available)

2. **Create API Key**
   - Settings → API Keys → Create API Key
   - Choose "Restricted Access" → Mail Send (Full Access)

3. **Update helm-chart/secrets.yaml**
   ```yaml
   backend:
     secrets:
       EMAIL_HOST: "smtp.sendgrid.net"
       EMAIL_PORT: "587"
       EMAIL_HOST_USER: "apikey"
       EMAIL_HOST_PASSWORD: "SG.your-api-key-here"
       ADMIN_EMAIL: "admin@maplesyrup.co"
   ```

## Email Notifications Configured

### When Order is Placed:
- **Customer** receives: Order confirmation with details, payment reference, next steps
- **Admin** receives: New order notification with payment info, customer details, fulfillment instructions

### When Order Status → SHIPPED:
- **Customer** receives: Shipment notification with estimated delivery times

## Testing Emails Locally

```bash
# Option 1: Use Django console backend (prints to terminal)
export EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Option 2: Use a test SMTP server
python -m smtpd -n -c DebuggingServer localhost:1025
# Then set EMAIL_HOST=localhost, EMAIL_PORT=1025 in secrets.yaml
```

## Troubleshooting

**Emails not sending?**
- Check logs: `kubectl logs -l app=backend`
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in secrets
- Gmail: Make sure you're using an App Password, not your regular password
- SendGrid: Check API key has Mail Send permissions

**Gmail blocking?**
- Use App Passwords (not regular password)
- Check "Less secure app access" is OFF (use App Passwords instead)

**Email going to spam?**
- Add SPF/DKIM records to your domain (when you buy one)
- For now, ask recipients to whitelist your email

## Production Recommendations

1. **Buy a domain** and use a professional email address
2. **Use SendGrid, Mailgun, or Amazon SES** for better deliverability
3. **Add HTML email templates** for better formatting
4. **Track email delivery** with webhook notifications

## Current Email Flow

```
Order Placed → Customer Email + Admin Email
     ↓
Admin Marks PAID (no email yet)
     ↓
Admin Marks SHIPPED → Customer Email
```

## Cost

- **Gmail**: Free (up to 500/day)
- **SendGrid Free**: 100 emails/day
- **SendGrid Paid**: $15/month for 40k emails
- **Mailgun**: Pay as you go ($0.80/1000)
