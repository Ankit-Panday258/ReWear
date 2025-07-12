# ReWear - Sustainable Fashion Exchange Platform

![ReWear Logo](https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=500&auto=format&fit=crop&q=60)

## 🌍 About ReWear

**ReWear** is a sustainable fashion exchange platform that allows users to swap their unused clothing items through two innovative methods:
- **Direct Item Swaps**: Exchange your items directly with other users
- **Point-Based Redemption System**: Earn and spend points to acquire desired items

Our platform promotes environmental sustainability by giving fashion a second life and building a trusted community of eco-conscious users.

## ✨ Key Features

### 🔐 User Authentication & Management
- Secure user registration and login system
- Profile management with user statistics
- Admin panel for platform management
- Role-based access control

### 👕 Listing Management
- Create detailed clothing listings with images
- Categorize items (Men, Women, Kids)
- Specify item types (Shirt, Pants, Dress, Others)
- Size selection (S, M, L, XL)
- Condition tracking (New, Like New, Good, Acceptable)
- Tag system for better searchability
- Admin approval workflow

### 🔄 Swap System
- **Direct Swaps**: Exchange your item for another user's item
- **Point Redemption**: Use earned points to acquire items without offering your own
- Swap request management (Accept, Reject, Cancel)
- Real-time swap status tracking
- Points earning system for successful swaps

### 💰 Points System
- Users start with 100 points
- Earn points by completing successful swaps
- Spend points to redeem items without direct exchange
- Track points balance in user profile

### 🛡️ Admin Features
- Dashboard with platform statistics
- User management (view, activate, deactivate)
- Listing approval/rejection system
- Swap request monitoring
- Content moderation tools

### 📱 Modern UI/UX
- Responsive design for all devices
- Bootstrap-powered interface
- Interactive image galleries
- Real-time notifications
- Smooth animations and transitions

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Session-based with Werkzeug security
- **Migrations**: Flask-Migrate with Alembic

### Frontend
- **Template Engine**: Jinja2
- **CSS Framework**: Bootstrap 5
- **Icons**: Font Awesome & Bootstrap Icons
- **JavaScript**: Vanilla JS for interactivity

### Database Schema
- **Users**: User accounts, points, admin roles
- **Listings**: Clothing items with detailed metadata
- **Swap Requests**: Exchange proposals and status tracking

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### 1. Clone the Repository
```bash
git clone https://github.com/Anuraj-dev/ReWear.git
cd ReWear
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Initialize Database
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. (Optional) Populate Sample Data
```bash
python sampledata.py
```

### 7. Run the Application
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## 📋 Usage Guide

### For Regular Users

1. **Registration**: Create an account with email and username
2. **Profile Setup**: Complete your profile with personal information
3. **List Items**: Add your unused clothing items with photos and descriptions
4. **Browse Listings**: Explore available items from other users
5. **Make Swap Requests**: 
   - Offer your item for direct swap
   - Use points for redemption without offering items
6. **Manage Swaps**: Accept, reject, or cancel swap requests
7. **Track Points**: Monitor your points balance and transaction history

### For Administrators

1. **Admin Dashboard**: Access comprehensive platform statistics
2. **User Management**: View and manage user accounts
3. **Content Moderation**: Approve or reject listing submissions
4. **Swap Monitoring**: Oversee swap requests and transactions
5. **Platform Analytics**: Track growth metrics and user engagement

## 🗄️ Database Models

### User Model
```python
- user_id (UUID, Primary Key)
- username (String, Unique)
- email (String, Unique)
- password (Hashed String)
- points (Integer, Default: 100)
- is_admin (Boolean, Default: False)
- created_at (DateTime)
```

### Listing Model
```python
- id (UUID, Primary Key)
- uploader_id (Foreign Key to User)
- title (String)
- description (Text)
- category (String: Men/Women/Kids)
- type (String: Shirt/Pants/Dress/Others)
- size (String: S/M/L/XL)
- condition (String: New/Like New/Good/Acceptable)
- tags (Text, Comma-separated)
- image_url (String)
- point_value (Integer, Default: 100)
- is_approved (Boolean, Default: False)
- is_available (Boolean, Default: True)
- status (String: Available/Swapped/Redeemed)
- created_at (DateTime)
```

### SwapRequest Model
```python
- id (UUID, Primary Key)
- requester_id (Foreign Key to User)
- requested_item_id (Foreign Key to Listing)
- offered_item_id (Foreign Key to Listing, Nullable)
- status (String: Pending/Accepted/Rejected/Cancelled)
- swap_type (String: direct_swap/point_redemption)
- points_used (Integer, Default: 0)
- created_at (DateTime)
- updated_at (DateTime)
```

## 🌐 API Endpoints

### Authentication Routes (`/auth`)
- `GET /register` - User registration page
- `POST /register` - Process registration
- `GET /login` - User login page
- `POST /login` - Process login
- `POST /logout` - User logout

### User Routes (`/user`)
- `GET /profile` - User profile page
- `GET /my-listings` - User's listings with filters
- `GET /my-swaps` - User's swap history
- `GET /swap-requests` - Incoming swap requests
- `POST /api/swaps/<id>/accept` - Accept swap request
- `POST /api/swaps/<id>/reject` - Reject swap request
- `POST /api/swaps/<id>/cancel` - Cancel swap request

### Listing Routes (`/listings`)
- `GET /` - Browse all approved listings
- `GET /new` - Create new listing form
- `POST /` - Submit new listing
- `GET /<id>` - View listing details
- `GET /<id>/edit` - Edit listing form
- `POST /<id>` - Update listing
- `GET /<id>/swap` - Swap request form
- `POST /<id>/swap` - Submit swap request
- `POST /<id>/redeem` - Redeem with points

### Admin Routes (`/admin`)
- `GET /` - Admin dashboard
- `GET /users` - Manage users
- `GET /listings` - Manage listings
- `GET /swaps` - Manage swap requests
- `POST /listings/<id>/approve` - Approve listing
- `POST /listings/<id>/reject` - Reject listing

## 🔒 Security Features

- **Password Hashing**: Werkzeug security for password encryption
- **Session Management**: Secure session handling
- **Input Validation**: Server-side validation for all forms
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **XSS Protection**: Jinja2 template auto-escaping
- **CSRF Protection**: Configurable secret key for session security

## 📱 Responsive Design

The application is fully responsive and optimized for:
- 📱 Mobile devices (320px+)
- 📱 Tablets (768px+)
- 💻 Desktop computers (1024px+)
- 🖥️ Large screens (1200px+)

## 🎨 Color Scheme & Branding

- **Primary Colors**: Green (#01715C) for sustainability theme
- **Secondary Colors**: Purple gradients for modern appeal
- **Typography**: Clean, modern fonts for readability
- **Icons**: Comprehensive icon system for intuitive navigation

## 🧪 Sample Data

The application includes a sample data generator (`sampledata.py`) that creates:
- 6 sample users with varying point balances
- 1 admin account (admin@rewear.com / admin123)
- Multiple clothing listings across different categories
- Sample swap requests demonstrating the system

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Support

For support and questions:
- 📧 Email: support@rewear.com
- 🐛 Issues: [GitHub Issues](https://github.com/Anuraj-dev/ReWear/issues)
- 📖 Documentation: This README file

## 🚀 Future Enhancements

- [ ] Real-time messaging between users
- [ ] Mobile app development
- [ ] AI-powered outfit recommendations
- [ ] Integration with shipping services
- [ ] Advanced search and filtering
- [ ] User rating and review system
- [ ] Social media integration
- [ ] Multi-language support
- [ ] Payment gateway integration
- [ ] Machine learning for personalized recommendations

---

**ReWear** - *Where Fashion Gets a Second Life* 🌱

Made with ❤️ for a sustainable future.
