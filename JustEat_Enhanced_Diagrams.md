# JustEat Food Ordering Application - Enhanced Professional Diagrams

## 1. System Architecture & User Flow Overview (Enhanced)

```mermaid
graph TB
    %% User Entry Points
    Start([👤 User Access]) --> Login{🔐 Login Required?}
    Login -->|No| Home[🏠 Home Page]
    Login -->|Yes| Auth[🔑 Authentication]
    
    %% Authentication Flow
    Auth --> Role{👥 User Role?}
    Role -->|Customer| CustomerDash[👨‍💼 Customer Dashboard]
    Role -->|Owner| OwnerDash[👨‍🍳 Owner Dashboard]
    
    %% Customer Workflow
    CustomerDash --> CustomerMenu{📋 Customer Actions}
    CustomerMenu --> BrowseRest[🍽️ Browse Restaurants]
    CustomerMenu --> ViewOrders[📦 View Orders]
    CustomerMenu --> ManageProfile[👤 Manage Profile]
    CustomerMenu --> ManagePrefs[⚙️ Manage Preferences]
    
    %% Restaurant Browsing Flow
    BrowseRest --> Search[🔍 Search & Filter]
    Search --> RestDetail[🏪 Restaurant Detail]
    RestDetail --> ViewMenu[📋 View Menu]
    ViewMenu --> AddToCart[🛒 Add to Cart]
    AddToCart --> Cart[🛍️ Shopping Cart]
    Cart --> PlaceOrder[💳 Place Order]
    PlaceOrder --> OrderConfirm[✅ Order Confirmation]
    
    %% Order Management Flow
    ViewOrders --> OrderDetail[📄 Order Details]
    OrderDetail --> TrackStatus[📍 Track Status]
    TrackStatus --> OrderComplete{✅ Order Complete?}
    OrderComplete -->|Yes| LeaveFeedback[⭐ Leave Feedback]
    OrderComplete -->|No| TrackStatus
    
    %% Owner Workflow
    OwnerDash --> OwnerMenu{📋 Owner Actions}
    OwnerMenu --> ManageRest[🏪 Manage Restaurants]
    OwnerMenu --> ManageMenu[🍽️ Manage Menu]
    OwnerMenu --> ViewOrdersOwner[📦 View Orders]
    OwnerMenu --> ViewReports[📊 View Reports]
    OwnerMenu --> ManageFeedback[💬 Manage Feedback]
    
    %% Restaurant Management Flow
    ManageRest --> CreateRest[➕ Create Restaurant]
    ManageRest --> EditRest[✏️ Edit Restaurant]
    CreateRest --> RestCreated[✅ Restaurant Created]
    EditRest --> RestUpdated[✅ Restaurant Updated]
    
    %% Menu Management Flow
    ManageMenu --> CreateItem[➕ Create Menu Item]
    ManageMenu --> EditItem[✏️ Edit Menu Item]
    CreateItem --> ItemCreated[✅ Menu Item Created]
    EditItem --> ItemUpdated[✅ Menu Item Updated]
    
    %% Order Processing Flow
    ViewOrdersOwner --> ProcessOrder[⚙️ Process Order]
    ProcessOrder --> UpdateStatus[🔄 Update Order Status]
    UpdateStatus --> StatusFlow{📊 Status Flow}
    StatusFlow --> Pending[⏳ Pending]
    StatusFlow --> Confirmed[✅ Confirmed]
    StatusFlow --> Preparing[👨‍🍳 Preparing]
    StatusFlow --> Ready[🚀 Ready]
    StatusFlow --> Completed[🎉 Completed]
    
    %% Feedback Management
    ManageFeedback --> ViewFeedback[👀 View Customer Feedback]
    ViewFeedback --> RespondFeedback[💬 Respond to Feedback]
    RespondFeedback --> FeedbackResolved[✅ Feedback Resolved]
    
    %% Enhanced Styling with Better Contrast
    classDef userAction fill:#1565c0,stroke:#0d47a1,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef systemProcess fill:#7b1fa2,stroke:#4a148c,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef decision fill:#d84315,stroke:#bf360c,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef dataStore fill:#2e7d32,stroke:#1b5e20,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef success fill:#388e3c,stroke:#1b5e20,stroke-width:3px,color:#ffffff,font-weight:bold
    
    class Start,Home,Auth,CustomerDash,OwnerDash userAction
    class BrowseRest,ViewOrders,ManageProfile,ManageRest,ManageMenu systemProcess
    class Login,Role,CustomerMenu,OwnerMenu,OrderComplete,StatusFlow decision
    class Cart,OrderConfirm dataStore
    class RestCreated,ItemCreated,FeedbackResolved success
```

## 2. Database Entity Relationship Diagram (Enhanced)

```mermaid
erDiagram
    User {
        int id PK "Primary Key"
        string username UK "Unique Username"
        string email UK "Unique Email"
        string password_hash "Hashed Password"
        string role "customer/owner"
        datetime created_at "Account Creation"
    }
    
    Customer {
        int id PK "Primary Key"
        int user_id FK "User Reference"
        string name "Full Name"
        string address "Delivery Address"
        string phone "Contact Number"
        text preferences "JSON Preferences"
        text dietary_restrictions "JSON Restrictions"
        datetime created_at "Profile Creation"
        datetime updated_at "Last Update"
    }
    
    RestaurantOwner {
        int id PK "Primary Key"
        int user_id FK "User Reference"
        string name "Owner Name"
        string phone "Contact Number"
        datetime created_at "Profile Creation"
        datetime updated_at "Last Update"
    }
    
    Restaurant {
        int id PK "Primary Key"
        int owner_id FK "Owner Reference"
        string name "Restaurant Name"
        text description "Restaurant Description"
        string location "Restaurant Location"
        text cuisines "JSON Cuisine Types"
        string image_path "Restaurant Image"
        datetime created_at "Restaurant Creation"
        datetime updated_at "Last Update"
    }
    
    MenuItem {
        int id PK "Primary Key"
        int restaurant_id FK "Restaurant Reference"
        string name "Item Name"
        text description "Item Description"
        float price "Item Price"
        string category "Menu Category"
        boolean is_vegetarian "Vegetarian Flag"
        boolean is_vegan "Vegan Flag"
        boolean is_guilt_free "Healthy Option"
        string image_path "Item Image"
        boolean is_special "Today's Special"
        boolean is_deal_of_day "Deal of Day"
        int times_ordered_today "Daily Order Count"
        date last_order_date "Last Order Date"
        datetime created_at "Item Creation"
        datetime updated_at "Last Update"
    }
    
    Order {
        int id PK "Primary Key"
        int customer_id FK "Customer Reference"
        int restaurant_id FK "Restaurant Reference"
        string status "Order Status"
        float total_amount "Total Cost"
        datetime created_at "Order Creation"
        datetime updated_at "Last Update"
    }
    
    OrderItem {
        int id PK "Primary Key"
        int order_id FK "Order Reference"
        int menu_item_id FK "Menu Item Reference"
        int quantity "Item Quantity"
        float price "Price at Order Time"
        datetime created_at "Item Addition"
    }
    
    Feedback {
        int id PK "Primary Key"
        int order_id FK "Order Reference"
        int customer_id FK "Customer Reference"
        int restaurant_id FK "Restaurant Reference"
        int rating "1-5 Star Rating"
        text message "Feedback Message"
        text response "Owner Response"
        boolean is_resolved "Response Status"
        datetime created_at "Feedback Creation"
        datetime updated_at "Last Update"
    }
    
    DishRating {
        int id PK "Primary Key"
        int order_id FK "Order Reference"
        int customer_id FK "Customer Reference"
        int restaurant_id FK "Restaurant Reference"
        int menu_item_id FK "Menu Item Reference"
        int rating "1-5 Star Rating"
        datetime created_at "Rating Creation"
        datetime updated_at "Last Update"
    }
    
    %% Enhanced Relationships with Clear Labels
    User ||--o| Customer : "has profile"
    User ||--o| RestaurantOwner : "has profile"
    RestaurantOwner ||--o{ Restaurant : "owns"
    Restaurant ||--o{ MenuItem : "has menu"
    Restaurant ||--o{ Order : "receives orders"
    Customer ||--o{ Order : "places orders"
    Order ||--o{ OrderItem : "contains items"
    MenuItem ||--o{ OrderItem : "ordered as"
    Order ||--o| Feedback : "has feedback"
    Order ||--o{ DishRating : "has dish ratings"
    Customer ||--o{ Feedback : "leaves feedback"
    Customer ||--o{ DishRating : "rates dishes"
    Restaurant ||--o{ Feedback : "receives feedback"
    Restaurant ||--o{ DishRating : "receives ratings"
    MenuItem ||--o{ DishRating : "rated by customers"
```

## 3. Customer Journey Flow (Enhanced)

```mermaid
journey
    title Customer Ordering Journey - JustEat App
    section Discovery Phase
      Visit Homepage: 5: Customer
      Browse Restaurants: 4: Customer
      Search by Cuisine: 4: Customer
      View Restaurant Details: 5: Customer
      Check Menu Items: 5: Customer
    section Ordering Phase
      Add Items to Cart: 5: Customer
      Review Cart Contents: 4: Customer
      Apply Dietary Filters: 4: Customer
      Place Order: 5: Customer
      Receive Confirmation: 5: Customer
    section Tracking Phase
      Track Order Status: 4: Customer
      Order Confirmed: 4: Customer
      Order Preparation: 3: Customer
      Order Ready: 5: Customer
      Order Completed: 5: Customer
    section Feedback Phase
      Rate Individual Dishes: 4: Customer
      Leave Restaurant Feedback: 4: Customer
      View Owner Response: 3: Customer
      Update Preferences: 3: Customer
```

## 4. Owner Management Flow (Enhanced)

```mermaid
journey
    title Restaurant Owner Management Journey - JustEat App
    section Setup Phase
      Register Restaurant: 5: Owner
      Add Restaurant Details: 4: Owner
      Upload Restaurant Images: 3: Owner
      Add Menu Categories: 4: Owner
      Create Menu Items: 4: Owner
      Set Special Items: 4: Owner
    section Operations Phase
      Receive New Orders: 5: Owner
      Confirm Orders: 4: Owner
      Update Order Status: 4: Owner
      Manage Kitchen Workflow: 3: Owner
      Handle Order Cancellations: 2: Owner
    section Analytics Phase
      View Order Reports: 4: Owner
      Check Popular Items: 5: Owner
      Monitor Daily Sales: 4: Owner
      Review Customer Feedback: 4: Owner
      Respond to Feedback: 3: Owner
      Update Menu Based on Data: 3: Owner
```

## 5. System Components Architecture (Enhanced)

```mermaid
graph TB
    subgraph "🎨 Frontend Layer"
        A[📄 HTML Templates<br/>Jinja2 Engine] --> B[🎨 Bootstrap CSS<br/>Responsive Design]
        A --> C[⭐ Font Awesome Icons<br/>UI Enhancement]
        A --> D[⚡ JavaScript<br/>Interactive Features]
    end
    
    subgraph "⚙️ Application Layer"
        E[🚀 Flask Application<br/>Web Framework] --> F[🎮 Controllers<br/>Route Handlers]
        F --> G[📝 Forms<br/>WTForms Validation]
        F --> H[🗃️ Models<br/>SQLAlchemy ORM]
        F --> I[🔧 Utils<br/>Helper Functions]
    end
    
    subgraph "💾 Data Layer"
        J[🗄️ SQLAlchemy ORM<br/>Database Abstraction] --> K[📊 SQLite Database<br/>Data Storage]
        L[📁 File Upload System<br/>Image Management] --> M[🖼️ Static Files<br/>Media Storage]
    end
    
    subgraph "🔐 Security Layer"
        N[🔑 Flask-Login<br/>Session Management] --> O[👤 User Sessions<br/>Authentication State]
        P[🛡️ Password Hashing<br/>Werkzeug Security] --> Q[🔒 Secure Storage<br/>Encrypted Passwords]
    end
    
    subgraph "🧪 Quality Assurance"
        R[✅ Unit Tests<br/>Model & Route Testing] --> S[📝 Test Coverage<br/>Quality Metrics]
        T[📋 Logging System<br/>Event Tracking] --> U[📊 Application Logs<br/>Debug Information]
    end
    
    %% Enhanced Connections
    A --> E
    E --> J
    E --> N
    E --> L
    E --> R
    E --> T
    
    %% Enhanced Styling with High Contrast
    classDef frontend fill:#1976d2,stroke:#0d47a1,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef application fill:#7b1fa2,stroke:#4a148c,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef data fill:#388e3c,stroke:#1b5e20,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef security fill:#d84315,stroke:#bf360c,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef quality fill:#f57c00,stroke:#e65100,stroke-width:3px,color:#ffffff,font-weight:bold
    
    class A,B,C,D frontend
    class E,F,G,H,I application
    class J,K,L,M data
    class N,O,P,Q security
    class R,S,T,U quality
```

## 6. Order Status Workflow (Enhanced)

```mermaid
stateDiagram-v2
    [*] --> Pending: 🛒 Order Placed
    Pending --> Confirmed: ✅ Owner Confirms
    Pending --> Cancelled: ❌ Owner Cancels
    Confirmed --> Preparing: 👨‍🍳 Kitchen Starts
    Preparing --> Ready: 🚀 Food Ready
    Ready --> Completed: 🎉 Customer Picks Up
    Completed --> [*]: ✅ Order Finished
    Cancelled --> [*]: ❌ Order Cancelled
    
    note right of Pending: 👀 Customer can view order<br/>⏳ Waiting for confirmation
    note right of Confirmed: 🍳 Kitchen preparation begins<br/>📱 Customer notified
    note right of Preparing: 👨‍🍳 Food is being cooked<br/>⏰ Estimated time provided
    note right of Ready: 🚀 Ready for pickup/delivery<br/>📞 Customer notified
    note right of Completed: 🎉 Order fulfilled<br/>⭐ Feedback available
    note right of Cancelled: ❌ Order cancelled<br/>💰 Refund processed
```

## 7. User Authentication Flow (New)

```mermaid
flowchart TD
    Start([👤 User Visits App]) --> CheckAuth{🔐 Authenticated?}
    CheckAuth -->|No| LoginPage[🔑 Login Page]
    CheckAuth -->|Yes| CheckRole{👥 Check Role}
    
    LoginPage --> EnterCreds[📝 Enter Credentials]
    EnterCreds --> ValidateCreds{✅ Validate Credentials}
    ValidateCreds -->|Invalid| ShowError[❌ Show Error Message]
    ValidateCreds -->|Valid| SetSession[🔐 Set User Session]
    ShowError --> LoginPage
    
    SetSession --> CheckRole
    CheckRole -->|Customer| CustomerDashboard[👨‍💼 Customer Dashboard]
    CheckRole -->|Owner| OwnerDashboard[👨‍🍳 Owner Dashboard]
    
    CustomerDashboard --> CustomerActions[📋 Customer Actions]
    OwnerDashboard --> OwnerActions[📋 Owner Actions]
    
    CustomerActions --> BrowseRestaurants[🍽️ Browse Restaurants]
    CustomerActions --> ViewOrders[📦 View Orders]
    CustomerActions --> ManageProfile[👤 Manage Profile]
    
    OwnerActions --> ManageRestaurants[🏪 Manage Restaurants]
    OwnerActions --> ProcessOrders[📦 Process Orders]
    OwnerActions --> ViewReports[📊 View Reports]
    
    %% Enhanced Styling
    classDef start fill:#4caf50,stroke:#2e7d32,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef process fill:#2196f3,stroke:#1565c0,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef decision fill:#ff9800,stroke:#f57c00,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef error fill:#f44336,stroke:#d32f2f,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef success fill:#4caf50,stroke:#2e7d32,stroke-width:3px,color:#ffffff,font-weight:bold
    
    class Start start
    class LoginPage,EnterCreds,SetSession,CustomerDashboard,OwnerDashboard process
    class CheckAuth,CheckRole,ValidateCreds decision
    class ShowError error
    class CustomerActions,OwnerActions,BrowseRestaurants,ViewOrders,ManageProfile,ManageRestaurants,ProcessOrders,ViewReports success
```

## 8. Menu Management Workflow (New)

```mermaid
flowchart LR
    subgraph "🏪 Restaurant Management"
        A[👨‍🍳 Owner Login] --> B[📋 Restaurant Dashboard]
        B --> C{🎯 Management Action}
    end
    
    subgraph "🍽️ Menu Item Creation"
        C -->|Create Item| D[➕ Add New Menu Item]
        D --> E[📝 Fill Item Details]
        E --> F[🖼️ Upload Item Image]
        F --> G[✅ Save Menu Item]
    end
    
    subgraph "✏️ Menu Item Editing"
        C -->|Edit Item| H[📋 Select Menu Item]
        H --> I[✏️ Update Item Details]
        I --> J[🔄 Update Image]
        J --> K[💾 Save Changes]
    end
    
    subgraph "🏷️ Special Item Management"
        C -->|Special Items| L[⭐ Mark Special Items]
        L --> M[🎯 Today's Special]
        L --> N[🔥 Deal of the Day]
        L --> O[📊 Mostly Ordered]
    end
    
    subgraph "📊 Analytics & Reports"
        C -->|Analytics| P[📈 View Item Performance]
        P --> Q[📊 Popular Items Report]
        P --> R[💰 Revenue Analysis]
        P --> S[⭐ Rating Analytics]
    end
    
    %% Enhanced Styling
    classDef owner fill:#7b1fa2,stroke:#4a148c,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef action fill:#2196f3,stroke:#1565c0,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef decision fill:#ff9800,stroke:#f57c00,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef success fill:#4caf50,stroke:#2e7d32,stroke-width:3px,color:#ffffff,font-weight:bold
    classDef special fill:#e91e63,stroke:#c2185b,stroke-width:3px,color:#ffffff,font-weight:bold
    
    class A,B owner
    class D,E,F,H,I,J,P action
    class C decision
    class G,K success
    class L,M,N,O,Q,R,S special
```

These enhanced diagrams feature:

✅ **High Contrast Colors**: Dark backgrounds with white text for excellent readability
✅ **Professional Icons**: Emojis and symbols for visual clarity
✅ **Bold Typography**: Enhanced font weights for better visibility
✅ **Clear Labels**: Descriptive text with context
✅ **Logical Grouping**: Related elements grouped together
✅ **Enhanced Relationships**: Clear connection labels
✅ **Status Indicators**: Visual feedback for different states
✅ **Comprehensive Coverage**: All major workflows included

You can copy any of these enhanced diagrams directly into Mermaid Live Editor or any Mermaid-compatible tool for professional, easy-to-read visualizations! 🚀
