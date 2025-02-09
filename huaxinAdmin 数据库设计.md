# huaxinAdmin 数据库设计

## 1.基础信息

### 1.1 部门表

```sql
CREATE TABLE huaxinAdmin_departments (
    id INT IDENTITY(1,1) PRIMARY KEY,  
    department_name NVARCHAR(100) NOT NULL UNIQUE,  
    parent_id INT NULL,  -- 允许子部门
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),

    -- 阻止删除父部门（即删除父部门时必须首先删除所有子部门），可以使用 NO ACTION
    CONSTRAINT FK_departments_parent FOREIGN KEY (parent_id) REFERENCES huaxinAdmin_departments(id) ON DELETE NO ACTION
);
```

```sql
# DDL
CREATE TABLE [dbo].[huaxinAdmin_departments] (
  [id] int  IDENTITY(1,1) NOT NULL,
  [department_name] nvarchar(100) COLLATE Chinese_PRC_CI_AS  NOT NULL,
  [parent_id] int  NULL,
  [status] tinyint DEFAULT 1 NULL,
  [created_at] datetime2(7) DEFAULT sysdatetime() NULL,
  [updated_at] datetime2(7) DEFAULT sysdatetime() NULL,
  CONSTRAINT [PK__huaxinAd__3213E83F11443D9B] PRIMARY KEY CLUSTERED ([id])
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)  
ON [PRIMARY],
  CONSTRAINT [FK_departments_parent] FOREIGN KEY ([parent_id]) REFERENCES [dbo].[huaxinAdmin_departments] ([id]) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT [UQ__huaxinAd__226ED1570F65858C] UNIQUE NONCLUSTERED ([department_name] ASC)
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)  
ON [PRIMARY]
)  
ON [PRIMARY]
GO

ALTER TABLE [dbo].[huaxinAdmin_departments] SET (LOCK_ESCALATION = TABLE)
GO

CREATE TRIGGER [dbo].[huaxinAdminDepartments_UpdateUserTimestamps]
ON [dbo].[huaxinAdmin_departments]
WITH EXECUTE AS CALLER
FOR UPDATE
AS
BEGIN
    -- 更新修改时间和更新时间
    UPDATE huaxinAdmin_departments
    SET 
        created_at = SYSDATETIME(),  -- 更新时间
        updated_at = SYSDATETIME()  -- 修改时间
    FROM huaxinAdmin_departments u
    INNER JOIN inserted i ON u.id = i.id;
END;
```





### 1.2 用户表

```sql
CREATE TABLE huaxinAdmin_users (
    id INT IDENTITY(1,1) PRIMARY KEY,  
    username NVARCHAR(50) NOT NULL UNIQUE,  
    password_hash NVARCHAR(255) NOT NULL,  
    email NVARCHAR(100) UNIQUE,  
    department_id INT NULL,  
    status TINYINT DEFAULT 1,  
    last_login DATETIME2 NULL,  -- 可为空的字段
    created_at DATETIME2 DEFAULT SYSDATETIME(),  -- 设置为当前时间
    updated_at DATETIME2 DEFAULT SYSDATETIME(),  -- 设置为当前时间
    CONSTRAINT FK_users_department FOREIGN KEY (department_id) REFERENCES huaxinAdmin_departments(id) ON DELETE SET NULL
);
```

```sql
# DDL
CREATE TABLE [dbo].[huaxinAdmin_users] (
  [id] int  IDENTITY(1,1) NOT NULL,
  [username] nvarchar(50) COLLATE Chinese_PRC_CI_AS  NOT NULL,
  [password_hash] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NOT NULL,
  [email] nvarchar(100) COLLATE Chinese_PRC_CI_AS  NULL,
  [department_id] int  NULL,
  [status] tinyint DEFAULT 1 NULL,
  [last_login] datetime2(7)  NULL,
  [created_at] datetime2(7) DEFAULT sysdatetime() NULL,
  [updated_at] datetime2(7) DEFAULT sysdatetime() NULL,
  CONSTRAINT [PK__huaxinAd__3213E83F30D70CA5] PRIMARY KEY CLUSTERED ([id])
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)  
ON [PRIMARY],
  CONSTRAINT [FK_users_department] FOREIGN KEY ([department_id]) REFERENCES [dbo].[huaxinAdmin_departments] ([id]) ON DELETE SET NULL ON UPDATE NO ACTION,
  CONSTRAINT [UQ__huaxinAd__AB6E6164DD0565D1] UNIQUE NONCLUSTERED ([email] ASC)
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)  
ON [PRIMARY],
  CONSTRAINT [UQ__huaxinAd__F3DBC5721A21B6FD] UNIQUE NONCLUSTERED ([username] ASC)
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)  
ON [PRIMARY]
)  
ON [PRIMARY]
GO

ALTER TABLE [dbo].[huaxinAdmin_users] SET (LOCK_ESCALATION = TABLE)
GO

CREATE TRIGGER [dbo].[huaxinAdminUsers_UpdateUserTimestamps]
ON [dbo].[huaxinAdmin_users]
WITH EXECUTE AS CALLER
FOR UPDATE
AS
BEGIN
    -- 更新修改时间和更新时间
    UPDATE huaxinAdmin_users
    SET 
        created_at = SYSDATETIME(),  -- 更新时间
        updated_at = SYSDATETIME()  -- 修改时间
    FROM huaxinAdmin_users u
    INNER JOIN inserted i ON u.id = i.id;
END;
```





### 1.3 用户头像表

```sql
CREATE TABLE huaxinAdmin_userAvatars (
    id INT IDENTITY(1,1) PRIMARY KEY,  
    user_id INT NOT NULL,  
    avatar_url NVARCHAR(255) NOT NULL,  
		is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT SYSDATETIME(),  
    updated_at DATETIME2 DEFAULT SYSDATETIME(),   

    CONSTRAINT FK_userAvatars_users FOREIGN KEY (user_id) REFERENCES huaxinAdmin_users(id) ON DELETE CASCADE  
);

CREATE UNIQUE INDEX UX_userAvatars_active ON huaxinAdmin_userAvatars(user_id) WHERE is_active = 1;
```

```sql
# DDL
CREATE TABLE [dbo].[huaxinAdmin_userAvatars] (
  [id] int  IDENTITY(1,1) NOT NULL,
  [user_id] int  NOT NULL,
  [avatar_url] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NOT NULL,
  [is_active] bit DEFAULT 1 NULL,
  [created_at] datetime2(7) DEFAULT sysdatetime() NULL,
  [updated_at] datetime2(7) DEFAULT sysdatetime() NULL,
  CONSTRAINT [PK__huaxinAd__3213E83F07D3BD7C] PRIMARY KEY CLUSTERED ([id])
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)  
ON [PRIMARY],
  CONSTRAINT [FK_userAvatars_users] FOREIGN KEY ([user_id]) REFERENCES [dbo].[huaxinAdmin_users] ([id]) ON DELETE CASCADE ON UPDATE NO ACTION
)  
ON [PRIMARY]
GO

ALTER TABLE [dbo].[huaxinAdmin_userAvatars] SET (LOCK_ESCALATION = TABLE)
GO

CREATE UNIQUE NONCLUSTERED INDEX [UX_userAvatars_active]
ON [dbo].[huaxinAdmin_userAvatars] (
  [user_id] ASC
)
WHERE ([is_active]=(1))
GO

CREATE TRIGGER [dbo].[huaxinAdminUserAvatars_UpdateUserTimestamps]
ON [dbo].[huaxinAdmin_userAvatars]
WITH EXECUTE AS CALLER
FOR UPDATE
AS
BEGIN
    -- 更新修改时间和更新时间
    UPDATE huaxinAdmin_userAvatars
    SET 
        created_at = SYSDATETIME(),  -- 更新时间
        updated_at = SYSDATETIME()  -- 修改时间
    FROM huaxinAdmin_userAvatars u
    INNER JOIN inserted i ON u.id = i.id;
END;
```



###  1.4 角色表

```sql
CREATE TABLE huaxinAdmin_roles (
    id INT IDENTITY(1,1) PRIMARY KEY,  
    role_name NVARCHAR(50) NOT NULL UNIQUE,  
    description NVARCHAR(255) NULL,  
    created_at DATETIME2 DEFAULT SYSDATETIME(),
);
```

```sql
# DDL
CREATE TABLE [dbo].[huaxinAdmin_roles] (
  [id] int  IDENTITY(1,1) NOT NULL,
  [role_name] nvarchar(50) COLLATE Chinese_PRC_CI_AS  NOT NULL,
  [description] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NULL,
  [status] tinyint DEFAULT 1 NULL,
  [created_at] datetime2(7) DEFAULT sysdatetime() NULL,
  CONSTRAINT [PK__huaxinAd__3213E83F1977DE16] PRIMARY KEY CLUSTERED ([id])
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)  
ON [PRIMARY],
  CONSTRAINT [UQ__huaxinAd__783254B1A1BF1E26] UNIQUE NONCLUSTERED ([role_name] ASC)
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)  
ON [PRIMARY]
)  
ON [PRIMARY]
GO

ALTER TABLE [dbo].[huaxinAdmin_roles] SET (LOCK_ESCALATION = TABLE)
```



### 1.5菜单表

```sql
CREATE TABLE dbo.huaxinAdmin_menus (
    id INT IDENTITY(1,1) PRIMARY KEY,         -- 菜单ID，自增
    parent_id INT NULL,                       -- 父级菜单ID，顶级菜单为NULL
    path NVARCHAR(255) NOT NULL,              -- 路由路径
    component NVARCHAR(255) NULL,             -- 组件路径
    redirect NVARCHAR(255) NULL,              -- 重定向路径
    name NVARCHAR(100) NOT NULL,              -- 路由名称
    title NVARCHAR(255) NOT NULL,             -- 菜单标题
    icon NVARCHAR(255) NULL,                  -- 图标
    always_show BIT DEFAULT 0,                -- 是否始终显示（0-否，1-是）
    no_cache BIT DEFAULT 0,                   -- 是否禁用缓存（0-否，1-是）
    affix BIT DEFAULT 0,                      -- 是否固定在标签栏（0-否，1-是）
    hidden BIT DEFAULT 0,                     -- 是否隐藏菜单（0-否，1-是）
    external_link NVARCHAR(255) NULL,         -- 外部链接
    permission NVARCHAR(MAX) NULL,            -- 权限标识（如['add', 'edit', 'delete']）
    menu_order INT DEFAULT 0,                 -- 排序（越小越靠前）
    create_time DATETIME2 DEFAULT SYSDATETIME(), -- 创建时间
    update_time DATETIME2 DEFAULT SYSDATETIME() -- 更新时间
);

-- 索引：为查询父级菜单时创建索引，提高查询效率
CREATE NONCLUSTERED INDEX IX_huaxinAdmin_menus_parent_id
ON dbo.huaxinAdmin_menus(parent_id);

-- 索引：根据菜单排序字段进行排序查询
CREATE NONCLUSTERED INDEX IX_huaxinAdmin_menus_menu_order
ON dbo.huaxinAdmin_menus(menu_order);
```

```sql
CREATE TABLE [dbo].[huaxinAdmin_menus] (
  [id] int  IDENTITY(1,1) NOT NULL,
  [parent_id] int  NULL,
  [path] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NOT NULL,
  [component] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NULL,
  [redirect] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NULL,
  [name] nvarchar(100) COLLATE Chinese_PRC_CI_AS  NOT NULL,
  [title] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NOT NULL,
  [icon] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NULL,
  [always_show] bit DEFAULT 0 NULL,
  [no_cache] bit DEFAULT 0 NULL,
  [affix] bit DEFAULT 0 NULL,
  [hidden] bit DEFAULT 0 NULL,
  [external_link] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NULL,
  [permission] nvarchar(max) COLLATE Chinese_PRC_CI_AS  NULL,
  [menu_order] int DEFAULT 0 NULL,
  [create_time] datetime2(7) DEFAULT sysdatetime() NULL,
  [update_time] datetime2(7) DEFAULT sysdatetime() NULL,
  CONSTRAINT [PK__huaxinAd__3213E83F44EE4F86] PRIMARY KEY CLUSTERED ([id])
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)  
ON [PRIMARY]
)  
ON [PRIMARY]
TEXTIMAGE_ON [PRIMARY]
GO

ALTER TABLE [dbo].[huaxinAdmin_menus] SET (LOCK_ESCALATION = TABLE)
GO

CREATE NONCLUSTERED INDEX [IX_huaxinAdmin_menus_parent_id]
ON [dbo].[huaxinAdmin_menus] (
  [parent_id] ASC
)
GO

CREATE NONCLUSTERED INDEX [IX_huaxinAdmin_menus_menu_order]
ON [dbo].[huaxinAdmin_menus] (
  [menu_order] ASC
)
```



### 1.6 用户角色表

```sql
CREATE TABLE huaxinAdmin_userRoles (
    id INT IDENTITY(1,1) PRIMARY KEY,  
    user_id INT NOT NULL,  
    role_id INT NOT NULL,  
    assigned_at DATETIME2 DEFAULT SYSDATETIME(), 

    CONSTRAINT FK_userRoles_user FOREIGN KEY (user_id) REFERENCES huaxinAdmin_users(id) ON DELETE CASCADE,  
    CONSTRAINT FK_userRoles_role FOREIGN KEY (role_id) REFERENCES huaxinAdmin_roles(id) ON DELETE CASCADE,  

    UNIQUE (user_id, role_id)  
);
```



### 1.7 权限表

```sql
CREATE TABLE [dbo].[huaxinAdmin_permissions] (
  [id] int  IDENTITY(1,1) NOT NULL,
  [menu_id] int  NULL,
  [name] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NULL,
  [action] nvarchar(255) COLLATE Chinese_PRC_CI_AS  NULL,
  [created_at] datetime2(7) DEFAULT sysdatetime() NULL,
  [updated_at] datetime2(7) DEFAULT sysdatetime() NULL,
  CONSTRAINT [PK__huaxinAd__3213E83FF010F634] PRIMARY KEY CLUSTERED ([id])
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)  
ON [PRIMARY]
)  
ON [PRIMARY]
GO

ALTER TABLE [dbo].[huaxinAdmin_permissions] SET (LOCK_ESCALATION = TABLE)
GO

CREATE TRIGGER [dbo].[huaxinAdminPermissions_UpdateUserTimestamps]
ON [dbo].[huaxinAdmin_permissions]
WITH EXECUTE AS CALLER
FOR UPDATE
AS
BEGIN
    -- 更新修改时间和更新时间
    UPDATE huaxinAdmin_permissions
    SET 
        created_at = SYSDATETIME(),  -- 更新时间
        updated_at = SYSDATETIME()  -- 修改时间
    FROM huaxinAdmin_permissions u
    INNER JOIN inserted i ON u.id = i.id;
END;
```



### 1.8 角色-权限关联表

```sql
CREATE TABLE huaxinAdmin_rolePermissions (
    id INT IDENTITY(1,1) PRIMARY KEY,  
    role_id INT NOT NULL,  
    permission_id INT NOT NULL,  
    granted_at DATETIME2 DEFAULT SYSDATETIME(), 

    CONSTRAINT FK_rolePermissions_role FOREIGN KEY (role_id) REFERENCES huaxinAdmin_roles(id) ON DELETE CASCADE,  
    CONSTRAINT FK_rolePermissions_permission FOREIGN KEY (permission_id) REFERENCES huaxinAdmin_permissions(id) ON DELETE CASCADE,  

    UNIQUE (role_id, permission_id)  
);
```



### 1.9 **权限管理逻辑**

#### **1. 给用户分配角色**

```sql
INSERT INTO huaxinAdmin_userRoles (user_id, role_id) VALUES (1, 2);
```

#### **2. 给角色分配权限**

```sql
INSERT INTO huaxinAdmin_rolePermissions (role_id, permission_id) VALUES (2, 5);
```

#### **3. 查询用户的所有权限**

```sql
SELECT p.permission_key
FROM huaxinAdmin_userRoles ur
JOIN huaxinAdmin_rolePermissions rp ON ur.role_id = rp.role_id
JOIN huaxinAdmin_permissions p ON rp.permission_id = p.id
WHERE ur.user_id = 1;
```

------

### **设计优点**