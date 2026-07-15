# 🌱 E-Waste Management System

A comprehensive web application for managing electronic waste with AI-powered waste classification, community features, and email verification.

## 👋 About This Project

This project was created to help people properly dispose of electronic waste while tracking their environmental impact. It combines modern web technologies with AI to make e-waste recycling easy and accessible.

**What makes this special:**
- 🔒 Secure authentication with email verification
- 🤖 AI-powered waste classification
- 📊 Track your environmental impact (CO₂, energy, water savings)
- 👥 Community features to connect with eco-conscious users
- 📱 Progressive Web App - works offline and installable on mobile

### 💡 Why I Built This

I created this project because I noticed how difficult it was for people to properly dispose of their old electronics. Most people don't know where to take their e-waste, and many end up throwing it in regular trash, which harms the environment.

This application solves that problem by:
- Making it easy to register and track your e-waste items
- Providing a community platform to share eco-tips
- Using AI to help classify waste types automatically
- Showing the real environmental impact of proper recycling

### 🎮 Gamification & Rewards
- **Points System**: Earn points for registering items and completing actions
- **Badges & Achievements**: Unlock badges for reaching milestones
- **Rewards Redemption**: Redeem points for discounts and special offers
- **Leaderboard**: Compete with other users on the global leaderboard
- **Referral System**: Earn bonus points for inviting friends

### 📜 Certificates of Recycling
- **Individual Certificates**: Generate PDF certificates for each recycled item
- **Annual Summaries**: Download yearly recycling reports
- **Environmental Impact**: Track your contribution to sustainability
- **Proof of Disposal**: Official documentation for proper e-waste disposal

### 🔔 Notifications & Preferences
- **Customizable Notifications**: Control email and SMS preferences
- **Collection Reminders**: Get notified before scheduled pickups
- **Achievement Alerts**: Celebrate when you earn badges and points
- **Notification Settings**: Fine-tune what you want to receive

### 📅 Pickup Management
- **Reschedule Pickups**: Change collection dates up to 3 times
- **Cancel Collections**: Cancel scheduled pickups if needed
- **Reschedule History**: Track all rescheduling activity
- **Reminder Notifications**: Get SMS/email reminders before collections

## ✨ Features

### 🔐 Authentication & Security
- **Email OTP Verification**: Secure account registration with email verification
- **JWT-based Authentication**: Secure token-based authentication
- **Password Encryption**: Bcrypt hashing for secure password storage
- **Role-based Access**: User, Admin, and Collector roles

### 📱 Core Functionality
- **E-Waste Item Management**: Add, edit, and track electronic waste items
- **Collection Scheduling**: Schedule and track waste collection pickups
- **AI Waste Scanner**: Upload images for automatic waste classification
- **Community Feed**: Share eco-tips and connect with other users
- **Analytics Dashboard**: Track personal and system-wide statistics
- **Profile Management**: Update personal information and settings

### 🤖 AI Features
- **Waste Classification**: TensorFlow-powered image recognition
- **Environmental Impact**: Calculate CO₂, energy, and water savings
- **Smart Recommendations**: Suggest appropriate disposal methods

### 📧 Email System
- **OTP Verification**: 6-digit codes sent via email
- **Welcome Emails**: Automated welcome messages for new users
- **Email Templates**: Beautiful HTML email templates

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd e-waste
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment (optional)**
   ```bash
   # Copy the example environment file
   cp env_example.txt .env
   
   # Edit .env with your email settings for OTP functionality
   # If not configured, OTP codes will be logged to console
   ```

4. **Initialize the database**
   ```bash
   # From project root (Windows PowerShell)
   python backend\init_sample_data.py
   ```

5. **Start the application**
   ```bash
   # From project root (Windows PowerShell)
   python .\start.py
   ```

6. **Access the application**
   - Open your browser and go to: `http://localhost:5000`
   - Register a new account with email verification
   - Or use sample credentials: `john_doe` / `password123`

## 📧 Email Configuration

To enable email OTP verification, configure your email settings in the `.env` file:

```env
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@ewaste.com
```

**Note**: For Gmail, you'll need to use an App Password instead of your regular password.

## 🔄 Registration Flow with OTP

### Step 1: Send OTP
```bash
POST /api/auth/send-otp
{
  "email": "user@example.com"
}
```

### Step 2: Verify OTP and Register
```bash
POST /api/auth/verify-otp
{
  "email": "user@example.com",
  "otp_code": "123456",
  "username": "johndoe",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "address": "123 Main St, City, State"
}
```

### Step 3: Resend OTP (if needed)
```bash
POST /api/auth/resend-otp
{
  "email": "user@example.com"
}
```

## 🗄️ Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Encrypted password
- `first_name`, `last_name`: User's name
- `phone`, `address`: Contact information
- `role`: User role (user/admin/collector)
- `is_active`: Account status
- `is_verified`: Email verification status
- `created_at`: Registration timestamp

### OTP Table
- `id`: Primary key
- `email`: Email address
- `otp_code`: 6-digit verification code
- `purpose`: OTP purpose (registration/password_reset)
- `is_used`: Usage status
- `created_at`: Generation timestamp
- `expires_at`: Expiration timestamp

### E-Waste Items Table
- `id`: Primary key
- `name`: Item name
- `brand`: Manufacturer
- `model`: Model number
- `category_id`: Category reference
- `condition`: Item condition
- `status`: Current status
- `owner_id`: User reference
- `created_at`: Creation timestamp

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/send-otp` - Send OTP for email verification
- `POST /api/auth/verify-otp` - Verify OTP and complete registration
- `POST /api/auth/resend-otp` - Resend OTP code
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile
- `POST /api/auth/change-password` - Change password

### E-Waste Management
- `GET /api/ewaste/items` - Get user's e-waste items
- `POST /api/ewaste/items` - Add new e-waste item
- `PUT /api/ewaste/items/<id>` - Update e-waste item
- `DELETE /api/ewaste/items/<id>` - Delete e-waste item
- `GET /api/ewaste/categories` - Get e-waste categories

### AI Scanner
- `POST /api/scanner/classify` - Classify waste image
- `GET /api/scanner/history` - Get scan history

### Community
- `GET /api/community/posts` - Get community posts
- `POST /api/community/posts` - Create new post
- `POST /api/community/posts/<id>/like` - Like a post
- `POST /api/community/posts/<id>/comment` - Comment on post

### Analytics
- `GET /api/analytics/dashboard` - Get dashboard statistics
- `GET /api/analytics/personal` - Get personal analytics
- `GET /api/analytics/community` - Get community analytics

### Rewards & Gamification
- `GET /api/rewards/points` - Get user's points balance
- `GET /api/rewards/points/transactions` - Get points transaction history
- `GET /api/rewards/badges` - Get user's earned badges
- `GET /api/rewards/rewards` - Get available rewards
- `POST /api/rewards/rewards/<id>/redeem` - Redeem a reward
- `GET /api/rewards/leaderboard` - Get global leaderboard
- `GET /api/rewards/leaderboard/my-rank` - Get user's rank

### Referral System
- `GET /api/referral/code` - Get or create referral code
- `POST /api/referral/code` - Regenerate referral code
- `GET /api/referral/history` - Get referral history
- `GET /api/referral/validate/<code>` - Validate referral code
- `POST /api/referral/apply/<code>` - Apply referral code
- `GET /api/referral/stats` - Get referral statistics

### Certificates
- `POST /api/certificates/generate/<item_id>` - Generate certificate for item
- `GET /api/certificates/download/<certificate_id>` - Download certificate PDF
- `GET /api/certificates/list` - List user's certificates
- `POST /api/certificates/summary` - Generate annual summary certificate

### Notifications
- `GET /api/notifications/preferences` - Get notification preferences
- `PUT /api/notifications/preferences` - Update notification preferences

### Pickup Rescheduling
- `POST /api/reschedule/collections/<id>/reschedule` - Reschedule collection
- `POST /api/reschedule/collections/<id>/cancel` - Cancel collection
- `GET /api/reschedule/collections/<id>/history` - Get reschedule history

## 🛠️ Development

### Project Structure
```
e-waste/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API routes
│   │   ├── utils/           # Utility functions
│   │   └── config.py        # Configuration
│   ├── uploads/             # File uploads
│   ├── instance/            # Database files
│   ├── requirements.txt     # Python dependencies
│   └── run.py              # Development server
├── frontend/
│   ├── templates/           # HTML templates
│   ├── static/              # CSS, JS, images
│   └── manifest.json        # PWA manifest
├── start.py                 # Application starter
└── README.md               # This file
```

### Running Tests
```bash
python test_features.py
```

### Database Management
```bash
# Reset database
rm backend/instance/ewaste.db
python backend/run.py
python backend/init_sample_data.py
```

## 🔒 Security Features

- **Email Verification**: Prevents fake account creation
- **OTP Expiration**: Codes expire after 10 minutes
- **Password Hashing**: Bcrypt encryption
- **JWT Tokens**: Secure authentication
- **Input Validation**: Server-side validation
- **CORS Protection**: Cross-origin request security

## 📱 Progressive Web App (PWA)

The application includes PWA features:
- **Offline Support**: Service worker for offline functionality
- **Installable**: Add to home screen on mobile devices
- **Responsive Design**: Works on all device sizes
- **Push Notifications**: Real-time updates (coming soon)

## 🌍 Environmental Impact

Track your environmental contribution:
- **CO₂ Reduction**: Calculate carbon footprint reduction
- **Energy Savings**: Track energy conservation
- **Water Conservation**: Monitor water usage reduction
- **Waste Diversion**: Measure waste diverted from landfills

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**1. Module Import Errors**
```bash
# Preferred: Run from project root so imports resolve
python .\start.py

# Or run directly inside backend for dev server
cd backend
python run.py
```

**2. Email Not Working**
- Check email credentials in `.env` file
- Verify SMTP settings
- Check firewall/network restrictions
- OTP codes will be logged to console if email fails

**3. Database Issues**
```bash
# Reset database
rm backend/instance/ewaste.db
python backend/run.py
python backend/init_sample_data.py
```

**4. Port Already in Use**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill
```

## 📞 Support

For support and questions:
- Check the troubleshooting section above
- Review the API documentation
- Run `python test_features.py` to identify issues
- Ensure all dependencies are installed correctly

## 🎯 Roadmap

- [ ] Push notifications
- [ ] Mobile app (React Native)
- [ ] Advanced analytics
- [ ] Multi-language support
- [ ] Integration with waste management companies
- [ ] Blockchain-based tracking
- [ ] IoT device integration

---

**Happy Recycling! 🌱♻️**
