# Database Documentation for E-Waste Management System

## Overview
The E-Waste Management System uses **SQLite** as its primary database with **SQLAlchemy ORM** for database operations. The database is configured to store user data, e-waste items, collections, community posts, and various system-related information.

## Database Configuration

### Connection Settings
- **Database Type**: SQLite
- **Database File**: `instance/ewaste.db`
- **ORM**: SQLAlchemy 2.0.21
- **Migration Tool**: Custom migration scripts

### Configuration File
The database configuration is managed through `<mcfile name="config.py" path="backend/app/config.py"></mcfile>`:

```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ewaste.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

## Database Schema

### Core Tables

#### 1. Users Table (`user`)
Stores user account information and authentication data.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| username | VARCHAR(80) | Unique username |
| email | VARCHAR(120) | Unique email address |
| password_hash | VARCHAR(128) | Encrypted password |
| first_name | VARCHAR(50) | User's first name |
| last_name | VARCHAR(50) | User's last name |
| phone | VARCHAR(20) | Contact phone number |
| address | TEXT | Physical address |
| role | VARCHAR(20) | User role (user/admin/collector) |
| created_at | DATETIME | Account creation timestamp |
| is_active | BOOLEAN | Account active status |
| is_verified | BOOLEAN | Email verification status |

#### 2. E-Waste Categories Table (`e_waste_category`)
Stores different categories of electronic waste.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | VARCHAR(100) | Category name |
| description | TEXT | Category description |
| recycling_fee | FLOAT | Recycling fee amount |
| created_at | DATETIME | Creation timestamp |

#### 3. E-Waste Items Table (`e_waste_item`)
Stores individual e-waste items registered by users.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | VARCHAR(100) | Item name |
| brand | VARCHAR(50) | Brand name |
| model | VARCHAR(50) | Model number |
| serial_number | VARCHAR(100) | Serial number |
| condition | VARCHAR(20) | Item condition |
| weight | FLOAT | Weight in kg |
| description | TEXT | Item description |
| status | VARCHAR(20) | Item status |
| estimated_value | FLOAT | Estimated value |
| created_at | DATETIME | Registration timestamp |
| updated_at | DATETIME | Last update timestamp |
| user_id | INTEGER | Foreign key to user |
| category_id | INTEGER | Foreign key to category |

#### 4. Collections Table (`collection`)
Stores scheduled collection requests.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| collection_date | DATETIME | Scheduled collection date |
| status | VARCHAR(20) | Collection status |
| notes | TEXT | Additional notes |
| collector_name | VARCHAR(100) | Collector name |
| collector_phone | VARCHAR(20) | Collector phone |
| created_at | DATETIME | Creation timestamp |
| user_id | INTEGER | Foreign key to user |
| ewaste_item_id | INTEGER | Foreign key to e-waste item |

### Community Tables

#### 5. Community Posts Table (`community_post`)
Stores community feed posts.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to user |
| title | VARCHAR(200) | Post title |
| content | TEXT | Post content |
| post_type | VARCHAR(50) | Type of post |
| image_path | VARCHAR(255) | Image file path |
| tags | VARCHAR(500) | Comma-separated tags |
| likes_count | INTEGER | Number of likes |
| comments_count | INTEGER | Number of comments |
| is_featured | BOOLEAN | Featured post flag |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |

#### 6. Post Comments Table (`post_comment`)
Stores comments on community posts.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| post_id | INTEGER | Foreign key to post |
| user_id | INTEGER | Foreign key to user |
| content | TEXT | Comment content |
| created_at | DATETIME | Creation timestamp |

#### 7. Post Likes Table (`post_like`)
Stores likes on community posts.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| post_id | INTEGER | Foreign key to post |
| user_id | INTEGER | Foreign key to user |
| created_at | DATETIME | Creation timestamp |

### Feedback Tables

#### 8. Complaints Table (`complaint`)
Stores user complaints and issues.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to user |
| complaint_type | VARCHAR(100) | Type of complaint |
| title | VARCHAR(200) | Complaint title |
| description | TEXT | Detailed description |
| location | VARCHAR(500) | Location information |
| image_path | VARCHAR(255) | Image file path |
| priority | VARCHAR(20) | Priority level |
| status | VARCHAR(50) | Complaint status |
| assigned_to | INTEGER | Assigned admin user |
| resolution_notes | TEXT | Resolution notes |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |
| resolved_at | DATETIME | Resolution timestamp |

#### 9. Feedback Table (`feedback`)
Stores general user feedback and suggestions.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to user |
| feedback_type | VARCHAR(50) | Type of feedback |
| subject | VARCHAR(200) | Feedback subject |
| message | TEXT | Feedback message |
| rating | INTEGER | Star rating (1-5) |
| is_anonymous | BOOLEAN | Anonymous flag |
| status | VARCHAR(20) | Feedback status |
| admin_response | TEXT | Admin response |
| created_at | DATETIME | Creation timestamp |

### Scanner Tables

#### 10. Waste Scans Table (`waste_scan`)
Stores AI waste scanning results.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to user |
| image_path | VARCHAR(255) | Image file path |
| predicted_category | VARCHAR(100) | AI predicted category |
| confidence_score | FLOAT | Prediction confidence |
| recommended_bin | VARCHAR(100) | Recommended disposal bin |
| disposal_instructions | TEXT | Disposal instructions |
| scanned_at | DATETIME | Scan timestamp |
| is_correct | BOOLEAN | User feedback on accuracy |

#### 11. Carbon Footprint Table (`carbon_footprint`)
Tracks carbon footprint reduction metrics.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to user |
| item_type | VARCHAR(100) | Type of item |
| weight_kg | FLOAT | Weight in kg |
| carbon_saved_kg | FLOAT | CO2 equivalent saved |
| energy_saved_kwh | FLOAT | Energy saved in kWh |
| water_saved_liters | FLOAT | Water saved in liters |
| recorded_at | DATETIME | Recording timestamp |

### Authentication Tables

#### 12. OTP Table (`otp`)
Stores one-time passwords for authentication.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| email | VARCHAR(120) | Email address |
| otp_code | VARCHAR(6) | OTP code |
| purpose | VARCHAR(20) | OTP purpose |
| is_used | BOOLEAN | Usage status |
| created_at | DATETIME | Creation timestamp |
| expires_at | DATETIME | Expiration timestamp |

## Database Management

### Available Commands

#### Initialize Database
```bash
python run.py
```

#### Database Statistics
```bash
python db_utils.py stats
```

#### Create Backup
```bash
python db_utils.py backup
```

#### Run Migration
```bash
python simple_migrate.py
```

### Database Utilities

The system includes several database management utilities:

1. **`<mcfile name="db_utils.py" path="backend/db_utils.py"></mcfile>`** - Basic database utilities
2. **`<mcfile name="simple_migrate.py" path="backend/simple_migrate.py"></mcfile>`** - Schema migration tool
3. **`<mcfile name="init_sample_data.py" path="backend/init_sample_data.py"></mcfile>`** - Sample data initialization

### Backup and Recovery

The system automatically creates backups in the `backups/` directory with timestamps. Each backup includes:
- Complete database schema
- All user data
- All e-waste item records
- All community and feedback data

### Security Considerations

1. **Password Security**: All passwords are hashed using bcrypt
2. **Data Encryption**: Sensitive data is encrypted at rest
3. **Access Control**: Role-based access control (user/admin/collector)
4. **Data Validation**: Input validation on all database operations

## Performance Optimization

### Indexing
The following columns are indexed for optimal performance:
- `user.email`
- `user.username`
- `otp.email`
- Foreign key columns

### Query Optimization
- Uses SQLAlchemy's relationship loading strategies
- Implements pagination for large datasets
- Caches frequently accessed data

## Maintenance

### Regular Tasks
1. **Backup Creation**: Daily automated backups
2. **Expired Data Cleanup**: Weekly cleanup of expired OTPs
3. **Database Optimization**: Monthly database optimization
4. **Schema Updates**: As needed for new features

### Monitoring
- Database size monitoring
- Query performance tracking
- Error logging and alerting

## Troubleshooting

### Common Issues

1. **Database Locked**: Usually due to concurrent access
2. **Migration Failures**: Check for existing data conflicts
3. **Backup Failures**: Ensure sufficient disk space
4. **Connection Errors**: Verify database file permissions

### Recovery Procedures
1. **Data Corruption**: Restore from latest backup
2. **Schema Issues**: Run migration scripts
3. **Performance Issues**: Rebuild indexes and optimize queries

## Future Enhancements

Planned database improvements:
- PostgreSQL support for production environments
- Advanced migration system with Alembic
- Database replication for high availability
- Advanced analytics and reporting tables