# 🚀 Quick Start Guide - E-Waste Management System

## Step 1: Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies (this may take a few minutes for TensorFlow)
pip install -r requirements.txt
```

**Note**: TensorFlow is required for the AI Waste Scanner. If you encounter issues or want a lighter setup, you can comment out the TensorFlow-related lines in `requirements.txt`.

## Step 2: Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file if needed (optional for development)
```

## Step 3: Initialize Sample Data

```bash
# Run sample data script to populate database
python init_sample_data.py
```

This creates:
- Sample e-waste categories
- Test users (username: `john_doe`, password: `password123`)
- Sample e-waste items
- Example collections

## Step 4: Start the Application

```bash
# Start Flask development server
python run.py
```

The application will be available at: **http://localhost:5000**

## Step 5: Test All Features

```bash
# In a new terminal, run the test script
python test_features.py
```

This will verify that all dashboard features are working correctly.

## Step 6: Login and Explore

1. **Login** with sample credentials:
   - Username: `john_doe`
   - Password: `password123`

2. **Dashboard Features** - Click each button to test:
   - ✅ **Add E-Waste Item** - Opens modal to add new items
   - ✅ **Schedule Collection** - Navigate to `/collections` page
   - ✅ **View All Items** - Navigate to `/items` page  
   - ✅ **Edit Profile** - Navigate to `/profile` page
   - ✅ **AI Waste Scanner** - Opens scanner modal (upload image)
   - ✅ **Report Issue** - Opens complaint modal

3. **Navigation Menu** - Use top navbar:
   - ✅ **Dashboard** - Main dashboard with stats
   - ✅ **My Items** - Full item management page
   - ✅ **Collections** - Collection scheduling and tracking
   - ✅ **Community** - Community feed with posts
   - ✅ **Analytics** - Personal and system analytics

## 🎯 Feature Testing Checklist

### Items Management (`/items`)
- [ ] View all items in grid/list format
- [ ] Search items by name, brand, model
- [ ] Filter by status and category
- [ ] Edit item details
- [ ] Delete items
- [ ] Schedule collection from item card

### Collections (`/collections`)
- [ ] View scheduled collections
- [ ] Schedule new collection (select item, date, time)
- [ ] Cancel existing collections
- [ ] Track collection status

### Profile (`/profile`)
- [ ] View current profile information
- [ ] Update personal details (name, phone, address)
- [ ] Change password with verification
- [ ] View account statistics

### AI Waste Scanner (Dashboard Modal)
- [ ] Upload image of waste item
- [ ] Get AI classification and confidence score
- [ ] See recommended bin and disposal instructions
- [ ] View environmental impact (CO₂, energy, water)

### Report Issue (Dashboard Modal)  
- [ ] Select complaint type
- [ ] Fill in title and description
- [ ] Add location and priority
- [ ] Attach photo (optional)
- [ ] Submit complaint

### Community Feed (`/community`)
- [ ] View community posts
- [ ] Create new post with image
- [ ] Like and comment on posts
- [ ] Filter by post type
- [ ] Search posts

### Analytics (`/analytics`)
- [ ] View personal statistics
- [ ] See daily activity trends
- [ ] Check category breakdowns
- [ ] View community leaderboards
- [ ] Monitor AI scanner accuracy

## 🔧 Troubleshooting

### Common Issues

**1. TensorFlow Installation Problems**
```bash
# For lighter setup, edit requirements.txt and comment out:
# tensorflow==2.13.0
# Then the AI scanner will show a placeholder message
```

**2. Port Already in Use**
```bash
# Kill existing process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill
```

**3. Database Issues**
```bash
# Reset database
rm ewaste.db
python run.py
python init_sample_data.py
```

**4. Module Import Errors**
```bash
# Make sure you're in the backend directory
cd backend
python run.py
```

## 📱 Mobile Testing

1. **Access on mobile**: Visit `http://your-ip:5000` on mobile device
2. **Install as PWA**: Use browser's "Add to Home Screen" option
3. **Test touch interactions**: All buttons and forms should be touch-friendly
4. **Test camera**: AI Scanner should access device camera for photos

## 🎉 Success Indicators

If everything is working correctly, you should see:

- ✅ All pages load without errors
- ✅ Login works with sample credentials  
- ✅ Dashboard shows statistics and quick actions
- ✅ All navigation links work
- ✅ Forms submit successfully
- ✅ Images upload and display correctly
- ✅ AI Scanner provides classifications (if TensorFlow is installed)
- ✅ Community posts can be created and viewed
- ✅ Analytics show data and trends

## 🚀 Next Steps

1. **Create your own account** via the registration page
2. **Add real e-waste items** to track
3. **Schedule actual collections** 
4. **Try the AI scanner** with photos of real items
5. **Engage with the community** by sharing eco-tips
6. **Monitor your environmental impact** via analytics

## 📞 Need Help?

If you encounter any issues:
1. Check the console for error messages
2. Run `python test_features.py` to identify problems
3. Verify all dependencies are installed correctly
4. Make sure the Flask server is running on port 5000

Happy recycling! 🌱♻️
