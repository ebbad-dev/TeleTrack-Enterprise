# TeleTrack v2.0 — Production Network Monitoring System

## 📋 Overview

TeleTrack v2.0 is a comprehensive production-level network monitoring and management platform built with Flask, MS SQL Server, and modern web technologies. It provides real-time device monitoring, alert management, SLA tracking, and comprehensive audit logging.

---

## 🎯 What's New in v2.0

### Database Enhancements
- ✅ 9 new tables with professional schema design
- ✅ Proper foreign key relationships and constraints
- ✅ Audit fields (CreatedAt, UpdatedAt) on all tables
- ✅ CHECK constraints for data validation
- ✅ UNIQUE constraints on IP and MAC addresses
- ✅ 20+ performance indexes on foreign keys
- ✅ 4 advanced stored procedures
- ✅ Device status history tracking
- ✅ SLA policy management
- ✅ User authentication system
- ✅ Audit logging for compliance

### Backend Improvements
- ✅ Modular Flask architecture with professional error handling
- ✅ RESTful API with consistent response format
- ✅ Dashboard metrics APIs
- ✅ Specialized endpoints for devices, alerts, technicians
- ✅ Input validation and IP address verification
- ✅ Background monitoring task (auto-alert on offline devices)
- ✅ Pagination support
- ✅ Device status history tracking
- ✅ Alert assignment workflow
- ✅ Dropdown APIs for form population

### Frontend Upgrades
- ✅ Professional dashboard with real-time metrics
- ✅ Interactive charts (Chart.js)
- ✅ 5 main tabs: Dashboard, Devices, Alerts, Technicians, Maintenance
- ✅ Advanced filtering and search
- ✅ Modal forms with validation
- ✅ Device details panel
- ✅ Alert panel with real-time updates
- ✅ Responsive design
- ✅ Pagination for large datasets
- ✅ Export to CSV
- ✅ Status badges with color coding

---

## 📁 Project Structure

```
db_project/
├── db_project/
│   ├── .venv/                    # Virtual environment
│   ├── app.py                    # ORIGINAL app (legacy)
│   ├── app_v2.py                 # NEW enhanced backend
│   ├── schema_upgrade.sql        # NEW database schema upgrade
│   ├── config.json               # Database connection config
│   ├── setup (1).sql             # Original setup script
│   └── templates/
│       ├── index.html            # ORIGINAL frontend (legacy)
│       └── index_v2.html         # NEW enhanced frontend
```

---

## 🚀 Implementation Guide

### Step 1: Backup Existing Data

```bash
# Backup your current database
# Use SQL Server Management Studio to backup TeleTrackDB
```

### Step 2: Install New Flask App

```bash
# Replace the current app.py with app_v2.py
cd c:\Users\HP\OneDrive\Desktop\db_project\db_project

# Stop the current Flask server (Ctrl+C)

# Switch to v2 app
rename app.py app_legacy.py
rename app_v2.py app.py

# Keep the old frontend for reference
rename templates\index.html templates\index_legacy.html
rename templates\index_v2.html templates\index.html
```

### Step 3: Install New Database Schema

**Option A: Via Frontend (Recommended)**
1. Access http://127.0.0.1:5000
2. Click "Setup" tab
3. Click "Initialize Database" button
4. Wait for success message

**Option B: Via SQL Server Management Studio**
1. Open the `schema_upgrade.sql` file
2. Execute it in your TeleTrackDB database
3. All tables and procedures will be created

### Step 4: Verify Installation

```bash
# Restart Flask app
python app.py

# Visit http://127.0.0.1:5000
# Should see new dashboard with metrics
```

---

## 📊 New Database Tables

### Core Tables

#### Users
Manages authentication and authorization
```
UserID | Username | PasswordHash | Role | Status | LastLogin | CreatedAt | UpdatedAt
```
**Roles:** Admin, Technician, Manager, Viewer

#### Vendors
Device manufacturer normalization
```
VendorID | VendorName | CountryOfOrigin | SupportEmail | Website | CreatedAt | UpdatedAt
```

#### SLA_Policies
Service Level Agreements per severity
```
PolicyID | SeverityLevel | ResponseTimeMinutes | ResolutionTimeMinutes | EscalationRequired
```

### Tracking Tables

#### Device_Status_History
Audit trail for device status changes
```
HistoryID | DeviceID | PreviousStatus | NewStatus | Reason | ChangedBy | ChangedAt
```

#### Alert_Comments
Collaborative notes on alerts
```
CommentID | AlertID | TechnicianID | Comment | CommentType | CommentedAt
```

#### Network_Links
Device connectivity relationships
```
LinkID | SourceDeviceID | TargetDeviceID | LinkType | Bandwidth | Latency | PacketLoss | Status
```

#### Audit_Log
System-wide activity tracking
```
AuditID | UserID | Action | TableName | RecordID | OldValue | NewValue | Timestamp
```

---

## 🔌 New API Endpoints

### Dashboard APIs
```
GET  /api/dashboard/summary              → Get key metrics
GET  /api/dashboard/alerts-by-severity   → Alert distribution
GET  /api/dashboard/devices-by-status    → Device distribution
GET  /api/dashboard/recent-alerts        → Last 10 alerts
```

### Device APIs
```
GET  /api/devices                        → Get all devices with filtering
GET  /api/devices/<id>                   → Device details + history
POST /api/devices                        → Create device
PUT  /api/devices/<id>                   → Update device
PUT  /api/devices/<id>/status            → Update status + history
```

### Alert APIs
```
GET  /api/alerts                         → Get alerts with pagination
POST /api/alerts                         → Create alert
POST /api/alerts/<id>/assign             → Assign to technician
POST /api/alerts/<id>/resolve            → Mark as resolved
GET  /api/alerts/<id>/comments           → Get comments
POST /api/alerts/<id>/comments           → Add comment
```

### Dropdown APIs (for forms)
```
GET  /api/dropdowns/locations            → Populate location selector
GET  /api/dropdowns/technicians          → Populate technician selector
GET  /api/dropdowns/vendors              → Populate vendor selector
GET  /api/dropdowns/sla-policies         → Populate SLA selector
```

### Technician APIs
```
GET  /api/technicians                    → Get all technicians
GET  /api/technicians/<id>/workload      → Tech's workload stats
```

---

## 🎨 Frontend Features

### Dashboard Tab
- **Metrics Cards**: Total, Online, Offline, Open Alerts, Critical, Technicians
- **Chart 1**: Alerts by Severity (Pie chart)
- **Chart 2**: Devices by Status (Bar chart)
- **Alert Feed**: Last 10 alerts with auto-refresh

### Devices Tab
- **Filters**: By Status, By Location
- **Table**: All device info with status badges
- **Actions**: View details, Edit, Add new
- **Export**: Download as CSV

### Alerts Tab
- **Filters**: By Status, By Severity
- **Table**: Alert details with device info
- **Pagination**: 20 alerts per page
- **Actions**: Assign to technician, Add comments

### Technicians Tab
- **Statistics**: Total alerts, Resolved, Avg resolution time
- **Status**: Visual indicators (Available/Busy/On Leave)

### Maintenance Tab
- **Log Creation**: New maintenance records
- **History**: All maintenance activities

### Setup Tab
- **One-Click DB Setup**: Initialize or upgrade schema

---

## 🔄 Stored Procedures

### sp_InsertDeviceWithValidation
Validates IP format and location before inserting
```sql
EXEC sp_InsertDeviceWithValidation
    @DeviceName='Router-1',
    @DeviceType='Router',
    @IPAddress='192.168.1.1',
    @LocationID=1
```

### sp_AssignAlert
Assigns alert to technician and updates stats
```sql
EXEC sp_AssignAlert
    @AlertID=5,
    @TechnicianID=1,
    @AssignedBy=1
```

### sp_ResolveAlert
Marks alert resolved and updates technician metrics
```sql
EXEC sp_ResolveAlert
    @AlertID=5,
    @ResolutionNote='Device rebooted',
    @ResolvedBy=1
```

### sp_UpdateDeviceStatus
Updates device status with history and auto-alert
```sql
EXEC sp_UpdateDeviceStatus
    @DeviceID=1,
    @NewStatus='Offline',
    @Reason='Connection lost',
    @ChangedBy=1
```

---

## 🔐 Security Improvements

1. **User Roles**: Admin, Technician, Manager, Viewer
2. **Audit Trail**: All changes logged with timestamp and user
3. **Input Validation**: IP format, email format, required fields
4. **Password Hashing**: SHA256 (can upgrade to bcrypt)
5. **SQL Constraints**: Prevents invalid data at database level

---

## 📊 Background Task

The app runs an automatic device monitoring task that:
- **Runs Every 60 Seconds**
- **Checks** for devices not pinged in 5 minutes
- **Creates** high-severity alert automatically
- **Updates** device status to "Offline"
- **Non-blocking** (runs in separate thread)

---

## ⚙️ Configuration

Edit `config.json` to change database connection:
```json
{
    "server": "localhost",
    "database": "TeleTrackDB",
    "driver": "ODBC Driver 17 for SQL Server"
}
```

---

## 📈 Performance Features

1. **20+ Indexes** on foreign keys and search columns
2. **Pagination** to limit query results
3. **Selective Column Loading** (only needed fields)
4. **Async/Await** in frontend for non-blocking UI
5. **Auto-refresh** on dashboard (every 30s)

---

## 🐛 Troubleshooting

### Issue: "schema_upgrade.sql not found"
**Solution**: Make sure `schema_upgrade.sql` is in the same directory as `app.py`

### Issue: "Column 'XXX' is not valid" 
**Solution**: Run database setup first via Setup tab or SQL script

### Issue: Charts not showing
**Solution**: Ensure Chart.js CDN is accessible, check browser console

### Issue: Dropdowns empty
**Solution**: Insert sample data first (see schema_upgrade.sql)

---

## 📚 Sample SQL Data

The schema includes sample data:
- 3 Vendors (Cisco, Juniper, Fortinet)
- 4 SLA Policies (Critical, High, Medium, Low)
- 3 Locations
- 3 Technicians
- 2 Users (admin, tech1)
- 3 Sample Devices

---

## 🔄 Migration from v1.0

**Old Features Preserved:**
- Generic CRUD endpoints still work (`/api/insert`, `/api/retrieve`, etc.)
- Legacy apps using v1.0 API won't break
- Old database tables remain unchanged

**New Features in v2.0:**
- Advanced monitoring APIs
- Dashboard with real-time metrics
- Professional UI
- Audit logging
- User management
- SLA tracking

---

## 📝 Future Enhancements

Potential additions for v3.0:
- Real-time WebSocket updates
- LDAP/AD integration
- Advanced reporting engine
- Email alert notifications
- Mobile app
- Kubernetes monitoring
- Machine learning anomaly detection
- Multi-tenant support

---

## 📞 Support

For issues or questions:
1. Check browser console for errors
2. Check Flask terminal for server errors
3. Verify database connection in config.json
4. Ensure all dependencies are installed

---

## 📄 License

Proprietary - TeleTrack Network Monitoring System

---

## ✅ Checklist Before Go-Live

- [ ] Database backup created
- [ ] schema_upgrade.sql executed successfully
- [ ] Sample data inserted
- [ ] Dashboard loads without errors
- [ ] All dropdowns populated
- [ ] Device creation works
- [ ] Alert creation works
- [ ] Filtering works
- [ ] Charts display correctly
- [ ] Forms validate input
- [ ] Export to CSV works
- [ ] Background monitoring active

---

**Version:** 2.0
**Last Updated:** May 2026
**Tested On:** MS SQL Server 2019+, Python 3.14, Flask 2.3+

