# JustEat Food Ordering Application - Complete Workflow Diagram

## System Architecture & User Flow Overview

```mermaid
graph TB
    %% User Entry Points
    Start([User Access]) --> Login{Login Required?}
    Login -->|No| Home[Home Page]
    Login -->|Yes| Auth[Authentication]
    
    %% Authentication Flow
    Auth --> Role{User Role?}
    Role -->|Customer| CustomerDash[Customer Dashboard]
    Role -->|Owner| OwnerDash[Owner Dashboard]
    
    %% Customer Workflow
    CustomerDash --> CustomerMenu{Customer Actions}
    CustomerMenu --> BrowseRest[Browse Restaurants]
    CustomerMenu --> ViewOrders[View Orders]
    CustomerMenu --> ManageProfile[Manage Profile]
    CustomerMenu --> ManagePrefs[Manage Preferences]
    
    %% Restaurant Browsing Flow
    BrowseRest --> Search[Search & Filter]
    Search --> RestDetail[Restaurant Detail]
    RestDetail --> ViewMenu[View Menu]
    ViewMenu --> AddToCart[Add to Cart]
    AddToCart --> Cart[Shopping Cart]
    Cart --> PlaceOrder[Place Order]
    PlaceOrder --> OrderConfirm[Order Confirmation]
    
    %% Order Management Flow
    ViewOrders --> OrderDetail[Order Details]
    OrderDetail --> TrackStatus[Track Status]
    TrackStatus --> OrderComplete{Order Complete?}
    OrderComplete -->|Yes| LeaveFeedback[Leave Feedback]
    OrderComplete -->|No| TrackStatus
    
    %% Owner Workflow
    OwnerDash --> OwnerMenu{Owner Actions}
    OwnerMenu --> ManageRest[Manage Restaurants]
    OwnerMenu --> ManageMenu[Manage Menu]
    OwnerMenu --> ViewOrdersOwner[View Orders]
    OwnerMenu --> ViewReports[View Reports]
    OwnerMenu --> ManageFeedback[Manage Feedback]
    
    %% Restaurant Management Flow
    ManageRest --> CreateRest[Create Restaurant]
    ManageRest --> EditRest[Edit Restaurant]
    CreateRest --> RestCreated[Restaurant Created]
    EditRest --> RestUpdated[Restaurant Updated]
    
    %% Menu Management Flow
    ManageMenu --> CreateItem[Create Menu Item]
    ManageMenu --> EditItem[Edit Menu Item]
    CreateItem --> ItemCreated[Menu Item Created]
    EditItem --> ItemUpdated[Menu Item Updated]
    
    %% Order Processing Flow
    ViewOrdersOwner --> ProcessOrder[Process Order]
    ProcessOrder --> UpdateStatus[Update Order Status]
    UpdateStatus --> StatusFlow{Status Flow}
    StatusFlow --> Pending[Pending]
    StatusFlow --> Confirmed[Confirmed]
    StatusFlow --> Preparing[Preparing]
    StatusFlow --> Ready[Ready]
    StatusFlow --> Completed[Completed]
    
    %% Feedback Management
    ManageFeedback --> ViewFeedback[View Customer Feedback]
    ViewFeedback --> RespondFeedback[Respond to Feedback]
    RespondFeedback --> FeedbackResolved[Feedback Resolved]
    
    %% Styling
    classDef userAction fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef systemProcess fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef dataStore fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    
    class Start,Home,Auth,CustomerDash,OwnerDash userAction
    class BrowseRest,ViewOrders,ManageProfile,ManageRest,ManageMenu systemProcess
    class Login,Role,CustomerMenu,OwnerMenu,OrderComplete,StatusFlow decision
    class Cart,OrderConfirm,RestCreated,ItemCreated dataStore
```

## Database Entity Relationship Diagram

```mermaid
erDiagram
    User {
        int id PK
        string username UK
        string email UK
        string password_hash
        string role
        datetime created_at
    }
    
    Customer {
        int id PK
        int user_id FK
        string name
        string address
        string phone
        text preferences
        text dietary_restrictions
        datetime created_at
        datetime updated_at
    }
    
    RestaurantOwner {
        int id PK
        int user_id FK
        string name
        string phone
        datetime created_at
        datetime updated_at
    }
    
    Restaurant {
        int id PK
        int owner_id FK
        string name
        text description
        string location
        text cuisines
        string image_path
        datetime created_at
        datetime updated_at
    }
    
    MenuItem {
        int id PK
        int restaurant_id FK
        string name
        text description
        float price
        string category
        boolean is_vegetarian
        boolean is_vegan
        boolean is_guilt_free
        string image_path
        boolean is_special
        boolean is_deal_of_day
        int times_ordered_today
        date last_order_date
        datetime created_at
        datetime updated_at
    }
    
    Order {
        int id PK
        int customer_id FK
        int restaurant_id FK
        string status
        float total_amount
        datetime created_at
        datetime updated_at
    }
    
    OrderItem {
        int id PK
        int order_id FK
        int menu_item_id FK
        int quantity
        float price
        datetime created_at
    }
    
    Feedback {
        int id PK
        int order_id FK
        int customer_id FK
        int restaurant_id FK
        int rating
        text message
        text response
        boolean is_resolved
        datetime created_at
        datetime updated_at
    }
    
    DishRating {
        int id PK
        int order_id FK
        int customer_id FK
        int restaurant_id FK
        int menu_item_id FK
        int rating
        datetime created_at
        datetime updated_at
    }
    
    %% Relationships
    User ||--o| Customer : "has profile"
    User ||--o| RestaurantOwner : "has profile"
    RestaurantOwner ||--o{ Restaurant : "owns"
    Restaurant ||--o{ MenuItem : "has"
    Restaurant ||--o{ Order : "receives"
    Customer ||--o{ Order : "places"
    Order ||--o{ OrderItem : "contains"
    MenuItem ||--o{ OrderItem : "ordered as"
    Order ||--o| Feedback : "has feedback"
    Order ||--o{ DishRating : "has dish ratings"
    Customer ||--o{ Feedback : "leaves"
    Customer ||--o{ DishRating : "rates"
    Restaurant ||--o{ Feedback : "receives"
    Restaurant ||--o{ DishRating : "receives"
    MenuItem ||--o{ DishRating : "rated"
```

## Customer Journey Flow

```mermaid
journey
    title Customer Ordering Journey
    section Discovery
      Visit Homepage: 5: Customer
      Browse Restaurants: 4: Customer
      Search by Cuisine: 4: Customer
      View Restaurant Details: 5: Customer
    section Ordering
      Browse Menu: 5: Customer
      Add Items to Cart: 5: Customer
      Review Cart: 4: Customer
      Place Order: 5: Customer
    section Tracking
      Receive Confirmation: 5: Customer
      Track Order Status: 4: Customer
      Order Preparation: 3: Customer
      Order Ready: 5: Customer
    section Feedback
      Receive Order: 5: Customer
      Rate Dishes: 4: Customer
      Leave Restaurant Feedback: 4: Customer
      View Owner Response: 3: Customer
```

## Owner Management Flow

```mermaid
journey
    title Restaurant Owner Management Journey
    section Setup
      Register Restaurant: 5: Owner
      Add Menu Items: 4: Owner
      Set Special Items: 4: Owner
      Upload Images: 3: Owner
    section Operations
      Receive New Orders: 5: Owner
      Confirm Orders: 4: Owner
      Update Order Status: 4: Owner
      Manage Inventory: 3: Owner
    section Analytics
      View Order Reports: 4: Owner
      Check Popular Items: 5: Owner
      Review Customer Feedback: 4: Owner
      Respond to Feedback: 3: Owner
```

## System Components Architecture

```mermaid
graph LR
    subgraph "Frontend Layer"
        A[HTML Templates] --> B[Bootstrap CSS]
        A --> C[Font Awesome Icons]
        A --> D[JavaScript]
    end
    
    subgraph "Application Layer"
        E[Flask App] --> F[Controllers]
        F --> G[Forms]
        F --> H[Models]
        F --> I[Utils]
    end
    
    subgraph "Data Layer"
        J[SQLAlchemy ORM] --> K[SQLite Database]
        L[File Uploads] --> M[Static Files]
    end
    
    subgraph "Authentication"
        N[Flask-Login] --> O[Session Management]
        P[Password Hashing] --> Q[Werkzeug Security]
    end
    
    A --> E
    E --> J
    E --> N
    E --> L
    
    classDef frontend fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef application fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef data fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef auth fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    
    class A,B,C,D frontend
    class E,F,G,H,I application
    class J,K,L,M data
    class N,O,P,Q auth
```

## Order Status Workflow

```mermaid
stateDiagram-v2
    [*] --> Pending: Order Placed
    Pending --> Confirmed: Owner Confirms
    Pending --> Cancelled: Owner Cancels
    Confirmed --> Preparing: Kitchen Starts
    Preparing --> Ready: Food Ready
    Ready --> Completed: Customer Picks Up
    Completed --> [*]: Order Finished
    Cancelled --> [*]: Order Cancelled
    
    note right of Pending: Customer can view order
    note right of Confirmed: Kitchen preparation begins
    note right of Preparing: Food is being cooked
    note right of Ready: Ready for pickup/delivery
    note right of Completed: Order fulfilled
```

## Key Features & Capabilities

### Customer Features
- **Restaurant Discovery**: Search by name, location, cuisine type
- **Smart Filtering**: Dietary preferences, price range, special items
- **Shopping Cart**: Session-based cart with quantity management
- **Order Tracking**: Real-time status updates
- **Feedback System**: Rate dishes and restaurants
- **Preferences**: Save favorite cuisines and restaurants
- **Recommendations**: Personalized suggestions based on history

### Owner Features
- **Restaurant Management**: Create, edit, delete restaurants
- **Menu Management**: Add, edit, delete menu items with images
- **Order Processing**: Update order status through workflow
- **Analytics**: View reports on popular items and revenue
- **Feedback Management**: Respond to customer feedback
- **Special Items**: Mark items as "Today's Special" or "Deal of the Day"

### System Features
- **Role-based Authentication**: Separate customer and owner access
- **Secure Password Management**: Hashing, reset, and change functionality
- **File Upload**: Secure image handling for restaurants and menu items
- **Database Migrations**: Version-controlled schema changes
- **Comprehensive Testing**: Unit tests for models and routes
- **Logging**: Application and security event logging
- **Responsive Design**: Mobile-friendly Bootstrap interface

## Technology Stack

- **Backend**: Flask 2.x, SQLAlchemy ORM, Flask-Login, Flask-WTF
- **Frontend**: Bootstrap 5.3.0, Font Awesome 6.4.0, Vanilla JavaScript
- **Database**: SQLite with Alembic migrations
- **Security**: Werkzeug password hashing, CSRF protection
- **Testing**: Python unittest framework
- **Development**: Virtual environment, Git version control

This comprehensive workflow diagram illustrates the complete JustEat food ordering application, showing user journeys, system architecture, database relationships, and key features. The application demonstrates a well-structured, scalable food ordering platform with role-based access, comprehensive order management, and modern web development practices.
