-- ════════════════════════════════════════════════════════════════════════════════
--  TELETRACK v2.0 — PRODUCTION NETWORK MONITORING SYSTEM
--  MS SQL Server Enhanced Database Schema
-- ════════════════════════════════════════════════════════════════════════════════

-- Create database (Drop if exists for a clean start)
USE master;
GO
IF EXISTS (SELECT * FROM sys.databases WHERE name = 'TeleTrackDB')
BEGIN
    ALTER DATABASE TeleTrackDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE TeleTrackDB;
    PRINT 'Old TeleTrackDB dropped.';
END
GO

CREATE DATABASE TeleTrackDB;
GO
PRINT 'New TeleTrackDB created.';
GO

USE TeleTrackDB;
GO

-- ════════════════════════════════════════════════════════════════════════════════
-- PART 1: FOUNDATIONAL TABLES
-- ════════════════════════════════════════════════════════════════════════════════

-- TABLE: Users (Authentication & Authorization)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
CREATE TABLE Users (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    Username VARCHAR(100) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    FullName VARCHAR(150),
    Email VARCHAR(150),
    Role VARCHAR(30) CHECK (Role IN ('Admin', 'Technician', 'Manager', 'Viewer')),
    Status VARCHAR(20) DEFAULT 'Active' CHECK (Status IN ('Active', 'Inactive', 'Suspended')),
    LastLogin DATETIME,
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE()
);

-- TABLE: Vendors (Device Manufacturer Normalization)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Vendors' AND xtype='U')
CREATE TABLE Vendors (
    VendorID INT PRIMARY KEY IDENTITY(1,1),
    VendorName VARCHAR(150) NOT NULL UNIQUE,
    CountryOfOrigin VARCHAR(100),
    SupportEmail VARCHAR(150),
    SupportPhone VARCHAR(30),
    Website VARCHAR(255),
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE()
);

-- TABLE: Locations (Parent)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Locations' AND xtype='U')
CREATE TABLE Locations (
    LocationID INT PRIMARY KEY IDENTITY(1,1),
    LocationName VARCHAR(150) NOT NULL,
    City VARCHAR(100),
    Country VARCHAR(100),
    SiteType VARCHAR(50),
    AddressLine VARCHAR(250),
    ContactPerson VARCHAR(150),
    ContactPhone VARCHAR(30),
    Latitude DECIMAL(10, 8),
    Longitude DECIMAL(11, 8),
    ImageUrl VARCHAR(500),
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE()
);

-- TABLE: Technicians (Independent Parent)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Technicians' AND xtype='U')
CREATE TABLE Technicians (
    TechnicianID INT PRIMARY KEY IDENTITY(1,1),
    FullName VARCHAR(150) NOT NULL,
    Email VARCHAR(150),
    Phone VARCHAR(30),
    Specialization VARCHAR(100),
    Shift VARCHAR(30) CHECK (Shift IN ('Morning', 'Evening', 'Night', 'Flexible')),
    Status VARCHAR(30) CHECK (Status IN ('Available', 'Busy', 'On Leave', 'Inactive')),
    TotalAlerts INT DEFAULT 0,
    ResolvedAlerts INT DEFAULT 0,
    AverageResolutionTime INT,
    ImageUrl VARCHAR(500),
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE()
);

-- TABLE: SLA_Policies (Service Level Agreements)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='SLA_Policies' AND xtype='U')
CREATE TABLE SLA_Policies (
    PolicyID INT PRIMARY KEY IDENTITY(1,1),
    SeverityLevel VARCHAR(30) UNIQUE CHECK (SeverityLevel IN ('Critical', 'High', 'Medium', 'Low')),
    ResponseTimeMinutes INT NOT NULL,
    ResolutionTimeMinutes INT NOT NULL,
    EscalationRequired BIT DEFAULT 0,
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE()
);

-- ════════════════════════════════════════════════════════════════════════════════
-- PART 2: DEVICE MANAGEMENT TABLES
-- ════════════════════════════════════════════════════════════════════════════════

-- TABLE: Devices (Child of Locations)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Devices' AND xtype='U')
CREATE TABLE Devices (
    DeviceID INT PRIMARY KEY IDENTITY(1,1),
    DeviceName VARCHAR(150) NOT NULL,
    DeviceType VARCHAR(50),
    VendorID INT,
    Model VARCHAR(100),
    IPAddress VARCHAR(45) UNIQUE,
    MACAddress VARCHAR(20) UNIQUE,
    LocationID INT NOT NULL,
    Status VARCHAR(30) DEFAULT 'Online' CHECK (Status IN ('Online', 'Offline', 'Degraded', 'Maintenance')),
    InstalledDate DATE,
    LastPingTime DATETIME,
    UpTime FLOAT,
    CPU_Usage FLOAT,
    Memory_Usage FLOAT,
    ImageUrl VARCHAR(500),
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Device_Location FOREIGN KEY (LocationID) REFERENCES Locations(LocationID),
    CONSTRAINT FK_Device_Vendor FOREIGN KEY (VendorID) REFERENCES Vendors(VendorID),
    CONSTRAINT UQ_Device_IP UNIQUE (IPAddress),
    CONSTRAINT UQ_Device_MAC UNIQUE (MACAddress)
);

-- TABLE: Device_Status_History (Audit Trail)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Device_Status_History' AND xtype='U')
CREATE TABLE Device_Status_History (
    HistoryID INT PRIMARY KEY IDENTITY(1,1),
    DeviceID INT NOT NULL,
    PreviousStatus VARCHAR(30),
    NewStatus VARCHAR(30),
    Reason VARCHAR(500),
    ChangedBy INT,
    ChangedAt DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_History_Device FOREIGN KEY (DeviceID) REFERENCES Devices(DeviceID),
    CONSTRAINT FK_History_User FOREIGN KEY (ChangedBy) REFERENCES Users(UserID)
);

-- TABLE: Network_Links (Device Connectivity)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Network_Links' AND xtype='U')
CREATE TABLE Network_Links (
    LinkID INT PRIMARY KEY IDENTITY(1,1),
    SourceDeviceID INT NOT NULL,
    TargetDeviceID INT NOT NULL,
    LinkType VARCHAR(50),
    Bandwidth FLOAT,
    Latency FLOAT,
    PacketLoss FLOAT,
    Status VARCHAR(30) DEFAULT 'Active',
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Link_Source FOREIGN KEY (SourceDeviceID) REFERENCES Devices(DeviceID),
    CONSTRAINT FK_Link_Target FOREIGN KEY (TargetDeviceID) REFERENCES Devices(DeviceID),
    CONSTRAINT CK_Link_Different CHECK (SourceDeviceID != TargetDeviceID)
);

-- ════════════════════════════════════════════════════════════════════════════════
-- PART 3: ALERT MANAGEMENT TABLES
-- ════════════════════════════════════════════════════════════════════════════════

-- TABLE: Alerts (Parent)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Alerts' AND xtype='U')
CREATE TABLE Alerts (
    AlertID INT PRIMARY KEY IDENTITY(1,1),
    DeviceID INT NOT NULL,
    AssignedTechID INT,
    AlertType VARCHAR(100),
    Severity VARCHAR(30) DEFAULT 'Medium' CHECK (Severity IN ('Critical', 'High', 'Medium', 'Low')),
    Message VARCHAR(500),
    AlertTime DATETIME DEFAULT GETDATE(),
    ResolvedTime DATETIME,
    Status VARCHAR(30) DEFAULT 'Open' CHECK (Status IN ('Open', 'Assigned', 'In Progress', 'Resolved', 'Escalated', 'Closed')),
    Priority INT DEFAULT 3,
    CreatedBy INT,
    ImageUrl VARCHAR(500),
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Alert_Device FOREIGN KEY (DeviceID) REFERENCES Devices(DeviceID),
    CONSTRAINT FK_Alert_Tech FOREIGN KEY (AssignedTechID) REFERENCES Technicians(TechnicianID),
    CONSTRAINT FK_Alert_User FOREIGN KEY (CreatedBy) REFERENCES Users(UserID),
    CONSTRAINT CK_Alert_Severity CHECK (Severity IN ('Critical', 'High', 'Medium', 'Low'))
);

-- TABLE: Alert_Comments (Collaborative Notes)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Alert_Comments' AND xtype='U')
CREATE TABLE Alert_Comments (
    CommentID INT PRIMARY KEY IDENTITY(1,1),
    AlertID INT NOT NULL,
    TechnicianID INT,
    Comment VARCHAR(1000),
    CommentType VARCHAR(30) DEFAULT 'Note' CHECK (CommentType IN ('Note', 'Update', 'Resolution')),
    CommentedAt DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Comment_Alert FOREIGN KEY (AlertID) REFERENCES Alerts(AlertID),
    CONSTRAINT FK_Comment_Tech FOREIGN KEY (TechnicianID) REFERENCES Technicians(TechnicianID)
);

-- ════════════════════════════════════════════════════════════════════════════════
-- PART 4: MAINTENANCE & LOGGING TABLES
-- ════════════════════════════════════════════════════════════════════════════════

-- TABLE: Maintenance_Logs
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Maintenance_Logs' AND xtype='U')
CREATE TABLE Maintenance_Logs (
    LogID INT PRIMARY KEY IDENTITY(1,1),
    DeviceID INT NOT NULL,
    TechnicianID INT,
    MaintenanceType VARCHAR(100) CHECK (MaintenanceType IN ('Preventive', 'Corrective', 'Emergency', 'Upgrade')),
    Description VARCHAR(500),
    ScheduledDate DATETIME,
    CompletedDate DATETIME,
    Duration_Minutes INT,
    Outcome VARCHAR(50) CHECK (Outcome IN ('Success', 'Partial', 'Failed', 'Rescheduled')),
    Notes VARCHAR(500),
    ImageUrl VARCHAR(500),
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_MaintLog_Device FOREIGN KEY (DeviceID) REFERENCES Devices(DeviceID),
    CONSTRAINT FK_MaintLog_Tech FOREIGN KEY (TechnicianID) REFERENCES Technicians(TechnicianID)
);

-- TABLE: Audit_Log (System-wide Activity Tracking)
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Audit_Log' AND xtype='U')
CREATE TABLE Audit_Log (
    AuditID INT PRIMARY KEY IDENTITY(1,1),
    UserID INT,
    Action VARCHAR(100),
    TableName VARCHAR(100),
    RecordID INT,
    OldValue VARCHAR(1000),
    NewValue VARCHAR(1000),
    Timestamp DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Audit_User FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

-- ════════════════════════════════════════════════════════════════════════════════
-- PART 5: INDEXES FOR PERFORMANCE
-- ════════════════════════════════════════════════════════════════════════════════

-- Foreign Key Indexes
CREATE NONCLUSTERED INDEX IDX_Device_LocationID ON Devices(LocationID);
CREATE NONCLUSTERED INDEX IDX_Device_VendorID ON Devices(VendorID);
CREATE NONCLUSTERED INDEX IDX_Alert_DeviceID ON Alerts(DeviceID);
CREATE NONCLUSTERED INDEX IDX_Alert_TechID ON Alerts(AssignedTechID);
CREATE NONCLUSTERED INDEX IDX_Alert_Status ON Alerts(Status);
CREATE NONCLUSTERED INDEX IDX_Alert_Severity ON Alerts(Severity);
CREATE NONCLUSTERED INDEX IDX_MaintLog_DeviceID ON Maintenance_Logs(DeviceID);
CREATE NONCLUSTERED INDEX IDX_MaintLog_TechID ON Maintenance_Logs(TechnicianID);
CREATE NONCLUSTERED INDEX IDX_DeviceHistory_DeviceID ON Device_Status_History(DeviceID);
CREATE NONCLUSTERED INDEX IDX_AlertComments_AlertID ON Alert_Comments(AlertID);
CREATE NONCLUSTERED INDEX IDX_Link_SourceID ON Network_Links(SourceDeviceID);
CREATE NONCLUSTERED INDEX IDX_Link_TargetID ON Network_Links(TargetDeviceID);

-- Search & Filtering Indexes
CREATE NONCLUSTERED INDEX IDX_Device_Status ON Devices(Status);
CREATE NONCLUSTERED INDEX IDX_Device_IPAddress ON Devices(IPAddress);
CREATE NONCLUSTERED INDEX IDX_Technician_Status ON Technicians(Status);
CREATE NONCLUSTERED INDEX IDX_Alert_AlertTime ON Alerts(AlertTime);
CREATE NONCLUSTERED INDEX IDX_Alert_CreatedAt ON Alerts(CreatedAt);
CREATE NONCLUSTERED INDEX IDX_User_Username ON Users(Username);

-- ════════════════════════════════════════════════════════════════════════════════
-- PART 6: STORED PROCEDURES
-- ════════════════════════════════════════════════════════════════════════════════

-- SP: Insert Device with Validation
IF OBJECT_ID('sp_InsertDeviceWithValidation', 'P') IS NOT NULL
    DROP PROCEDURE sp_InsertDeviceWithValidation;
GO

CREATE PROCEDURE sp_InsertDeviceWithValidation
    @DeviceName VARCHAR(150),
    @DeviceType VARCHAR(50),
    @VendorID INT,
    @Model VARCHAR(100),
    @IPAddress VARCHAR(45),
    @MACAddress VARCHAR(20),
    @LocationID INT,
    @Status VARCHAR(30) = 'Online'
AS
BEGIN
    -- Validate IP format (basic)
    IF @IPAddress NOT LIKE '%[0-9]%'
        RAISERROR('Invalid IP Address format', 16, 1);
    
    -- Check Location exists
    IF NOT EXISTS (SELECT 1 FROM Locations WHERE LocationID = @LocationID)
        RAISERROR('Location does not exist', 16, 1);
    
    -- Check Vendor exists (if provided)
    IF @VendorID IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Vendors WHERE VendorID = @VendorID)
        RAISERROR('Vendor does not exist', 16, 1);
    
    -- Insert Device
    INSERT INTO Devices (DeviceName, DeviceType, VendorID, Model, IPAddress, MACAddress, LocationID, Status)
    VALUES (@DeviceName, @DeviceType, @VendorID, @Model, @IPAddress, @MACAddress, @LocationID, @Status);
    
    SELECT @@IDENTITY AS DeviceID;
END;
GO

-- SP: Assign Alert to Technician
IF OBJECT_ID('sp_AssignAlert', 'P') IS NOT NULL
    DROP PROCEDURE sp_AssignAlert;
GO

CREATE PROCEDURE sp_AssignAlert
    @AlertID INT,
    @TechnicianID INT,
    @AssignedBy INT
AS
BEGIN
    -- Check Alert exists
    IF NOT EXISTS (SELECT 1 FROM Alerts WHERE AlertID = @AlertID)
        RAISERROR('Alert does not exist', 16, 1);
    
    -- Check Technician exists
    IF NOT EXISTS (SELECT 1 FROM Technicians WHERE TechnicianID = @TechnicianID)
        RAISERROR('Technician does not exist', 16, 1);
    
    -- Update Alert
    UPDATE Alerts
    SET AssignedTechID = @TechnicianID,
        Status = 'Assigned',
        UpdatedAt = GETDATE()
    WHERE AlertID = @AlertID;
    
    -- Log to Audit
    INSERT INTO Audit_Log (UserID, Action, TableName, RecordID, NewValue)
    VALUES (@AssignedBy, 'ALERT_ASSIGNED', 'Alerts', @AlertID, CAST(@TechnicianID AS VARCHAR));
    
    -- Update Technician stats
    UPDATE Technicians
    SET TotalAlerts = TotalAlerts + 1
    WHERE TechnicianID = @TechnicianID;
END;
GO

-- SP: Resolve Alert
IF OBJECT_ID('sp_ResolveAlert', 'P') IS NOT NULL
    DROP PROCEDURE sp_ResolveAlert;
GO

CREATE PROCEDURE sp_ResolveAlert
    @AlertID INT,
    @ResolutionNote VARCHAR(500),
    @ResolvedBy INT
AS
BEGIN
    DECLARE @TechID INT, @AlertTimedate DATETIME;
    
    -- Get Alert details
    SELECT @TechID = AssignedTechID, @AlertTimedate = AlertTime
    FROM Alerts
    WHERE AlertID = @AlertID;
    
    IF @TechID IS NULL
        RAISERROR('Alert not found', 16, 1);
    
    -- Update Alert
    UPDATE Alerts
    SET Status = 'Resolved',
        ResolvedTime = GETDATE(),
        UpdatedAt = GETDATE()
    WHERE AlertID = @AlertID;
    
    -- Add resolution comment
    INSERT INTO Alert_Comments (AlertID, TechnicianID, Comment, CommentType)
    VALUES (@AlertID, @TechID, @ResolutionNote, 'Resolution');
    
    -- Update Technician stats
    UPDATE Technicians
    SET ResolvedAlerts = ResolvedAlerts + 1,
        AverageResolutionTime = (
            SELECT AVG(DATEDIFF(MINUTE, AlertTime, ResolvedTime))
            FROM Alerts
            WHERE AssignedTechID = @TechID AND ResolvedTime IS NOT NULL
        )
    WHERE TechnicianID = @TechID;
    
    -- Log to Audit
    INSERT INTO Audit_Log (UserID, Action, TableName, RecordID, NewValue)
    VALUES (@ResolvedBy, 'ALERT_RESOLVED', 'Alerts', @AlertID, @ResolutionNote);
END;
GO

-- SP: Update Device Status
IF OBJECT_ID('sp_UpdateDeviceStatus', 'P') IS NOT NULL
    DROP PROCEDURE sp_UpdateDeviceStatus;
GO

CREATE PROCEDURE sp_UpdateDeviceStatus
    @DeviceID INT,
    @NewStatus VARCHAR(30),
    @Reason VARCHAR(500),
    @ChangedBy INT
AS
BEGIN
    DECLARE @OldStatus VARCHAR(30);
    
    SELECT @OldStatus = Status FROM Devices WHERE DeviceID = @DeviceID;
    
    IF @OldStatus IS NULL
        RAISERROR('Device not found', 16, 1);
    
    -- Update Device
    UPDATE Devices
    SET Status = @NewStatus,
        UpdatedAt = GETDATE()
    WHERE DeviceID = @DeviceID;
    
    -- Log to Status History
    INSERT INTO Device_Status_History (DeviceID, PreviousStatus, NewStatus, Reason, ChangedBy)
    VALUES (@DeviceID, @OldStatus, @NewStatus, @Reason, @ChangedBy);
    
    -- Auto-create alert if Device goes offline
    IF @NewStatus = 'Offline' AND @OldStatus != 'Offline'
    BEGIN
        INSERT INTO Alerts (DeviceID, AlertType, Severity, Message, Status, CreatedBy)
        VALUES (@DeviceID, 'Device Offline', 'High', 'Device went offline: ' + @Reason, 'Open', @ChangedBy);
    END
END;
GO

-- ════════════════════════════════════════════════════════════════════════════════
-- PART 7: SAMPLE DATA (Optional)
-- ════════════════════════════════════════════════════════════════════════════════

-- Insert Sample Vendors
INSERT INTO Vendors (VendorName, CountryOfOrigin, SupportEmail, Website)
VALUES
    ('Cisco', 'USA', 'support@cisco.com', 'https://www.cisco.com'),
    ('Juniper', 'USA', 'support@juniper.net', 'https://www.juniper.net'),
    ('Fortinet', 'USA', 'support@fortinet.com', 'https://www.fortinet.com');

-- Insert Sample SLA Policies
INSERT INTO SLA_Policies (SeverityLevel, ResponseTimeMinutes, ResolutionTimeMinutes, EscalationRequired)
VALUES
    ('Critical', 15, 60, 1),
    ('High', 30, 240, 1),
    ('Medium', 60, 480, 0),
    ('Low', 120, 1440, 0);

-- Insert Sample Users
INSERT INTO Users (Username, PasswordHash, FullName, Email, Role, Status)
VALUES
    ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'Admin User', 'admin@teletrack.com', 'Admin', 'Active'),
    ('tech1', 'e807f1fcf82d132f9bb018ca6738a19f27f2a2d4feb4b92f288b32ad84d08295', 'John Smith', 'john@teletrack.com', 'Technician', 'Active');

-- Insert Sample Locations
INSERT INTO Locations (LocationName, City, Country, SiteType, ContactPerson, ContactPhone)
VALUES
    ('HQ - Manhattan', 'New York', 'USA', 'Headquarters', 'Alice Brown', '+1-212-555-0001'),
    ('Data Center - New Jersey', 'Jersey City', 'USA', 'Data Center', 'Bob Wilson', '+1-201-555-0002'),
    ('Branch - Boston', 'Boston', 'USA', 'Branch Office', 'Carol Davis', '+1-617-555-0003');

-- Insert Sample Technicians
INSERT INTO Technicians (FullName, Email, Phone, Specialization, Shift, Status)
VALUES
    ('John Doe', 'john.doe@teletrack.com', '+1-212-555-1001', 'Network Infrastructure', 'Morning', 'Available'),
    ('Jane Smith', 'jane.smith@teletrack.com', '+1-212-555-1002', 'Systems Administration', 'Evening', 'Available'),
    ('Mike Johnson', 'mike.johnson@teletrack.com', '+1-212-555-1003', 'Security', 'Night', 'Busy');

-- Insert Sample Devices
INSERT INTO Devices (DeviceName, DeviceType, VendorID, Model, IPAddress, MACAddress, LocationID, Status, InstalledDate, LastPingTime)
VALUES
    ('NYC-Router-1', 'Router', 1, 'Cisco ASR 9006', '192.168.1.1', '00:1A:2B:3C:4D:5E', 1, 'Online', '2023-01-15', GETDATE()),
    ('Jersey-Firewall-1', 'Firewall', 3, 'FortiGate 7000', '192.168.2.1', '00:2B:3C:4D:5E:6F', 2, 'Online', '2023-02-20', GETDATE()),
    ('Boston-Switch-1', 'Switch', 2, 'Juniper EX4600', '192.168.3.1', '00:3C:4D:5E:6F:7G', 3, 'Online', '2023-03-10', GETDATE());

GO

PRINT '✓ TeleTrack v2.0 Database Schema Created Successfully!';
