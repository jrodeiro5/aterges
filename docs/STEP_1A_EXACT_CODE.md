# 🔧 STEP 1A: Desktop Sidebar Collapse - Exact Code Changes

## Current vs Enhanced Code

### **File:** `components/layouts/app-layout.tsx`

### **STEP 1: Add State Management (Line ~44)**

**Current code:**
```typescript
const [sidebarOpen, setSidebarOpen] = useState(false);
```

**Replace with:**
```typescript
const [sidebarOpen, setSidebarOpen] = useState(false);
const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

// Load collapse state from localStorage
useEffect(() => {
  const saved = localStorage.getItem('sidebar-collapsed');
  if (saved !== null) {
    setSidebarCollapsed(JSON.parse(saved));
  }
}, []);

// Save collapse state when it changes
useEffect(() => {
  localStorage.setItem('sidebar-collapsed', JSON.stringify(sidebarCollapsed));
}, [sidebarCollapsed]);
```

---

### **STEP 2: Add Collapse Button (Line ~92, in sidebar header)**

**Current code:**
```jsx
<div className="flex h-28 items-center justify-between px-6 border-b border-border">
  <Link href="/app/dashboard" className="flex items-center">
    <Image
      src="/aterges_logo-removebg-preview.png"
      alt="Aterges AI"
      width={320}
      height={85}
      className="h-20 w-auto object-contain"
      priority
      style={{ objectPosition: 'left center' }}
    />
  </Link>
  <Button
    variant="ghost"
    size="sm"
    className="lg:hidden"
    onClick={() => setSidebarOpen(false)}
  >
    <X className="h-4 w-4" />
  </Button>
</div>
```

**Replace with:**
```jsx
<div className="flex h-28 items-center justify-between px-6 border-b border-border">
  <Link href="/app/dashboard" className="flex items-center">
    <Image
      src="/aterges_logo-removebg-preview.png"
      alt="Aterges AI"
      width={320}
      height={85}
      className={cn(
        "h-20 w-auto object-contain transition-all duration-300",
        sidebarCollapsed ? "scale-75 opacity-60" : ""
      )}
      priority
      style={{ objectPosition: 'left center' }}
    />
  </Link>
  <div className="flex items-center space-x-2">
    {/* Desktop collapse button */}
    <Button
      variant="ghost"
      size="sm"
      className="hidden lg:flex"
      onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
      title={sidebarCollapsed ? "Expandir sidebar" : "Colapsar sidebar"}
    >
      {sidebarCollapsed ? (
        <Menu className="h-4 w-4" />
      ) : (
        <X className="h-4 w-4" />
      )}
    </Button>
    {/* Mobile close button */}
    <Button
      variant="ghost"
      size="sm"
      className="lg:hidden"
      onClick={() => setSidebarOpen(false)}
    >
      <X className="h-4 w-4" />
    </Button>
  </div>
</div>
```

---

### **STEP 3: Update Sidebar Container Classes (Line ~74)**

**Current code:**
```jsx
<div className={cn(
  "fixed inset-y-0 left-0 z-50 w-80 bg-card border-r border-border transform transition-transform duration-200 ease-in-out lg:translate-x-0",
  sidebarOpen ? "translate-x-0" : "-translate-x-full"
)}>
```

**Replace with:**
```jsx
<div className={cn(
  "fixed inset-y-0 left-0 z-50 bg-card border-r border-border transform transition-all duration-300 ease-in-out lg:translate-x-0",
  // Mobile behavior
  sidebarOpen ? "translate-x-0" : "-translate-x-full",
  // Desktop behavior
  "lg:translate-x-0",
  // Desktop width based on collapse state
  sidebarCollapsed ? "lg:w-20" : "lg:w-80",
  // Mobile always full width
  "w-80"
)}>
```

---

### **STEP 4: Update Navigation Items for Collapsed State (Line ~120)**

**Current navigation code:**
```jsx
{navigation.map((item) => {
  const Icon = item.icon;
  const isActive = pathname === item.href;
  
  return (
    <Link
      key={item.name}
      href={item.href}
      className={cn(
        "group flex flex-col space-y-1 rounded-lg px-3 py-3 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground",
        isActive 
          ? "bg-accent text-accent-foreground shadow-sm" 
          : "text-muted-foreground hover:text-foreground"
      )}
      onClick={() => setSidebarOpen(false)}
    >
      <div className="flex items-center space-x-3">
        <Icon className="h-4 w-4 shrink-0" />
        <span className="font-medium">{item.name}</span>
      </div>
      <p className="text-xs text-muted-foreground group-hover:text-muted-foreground/80 pl-7">
        {item.description}
      </p>
    </Link>
  );
})}
```

**Replace with:**
```jsx
{navigation.map((item) => {
  const Icon = item.icon;
  const isActive = pathname === item.href;
  
  return (
    <Link
      key={item.name}
      href={item.href}
      className={cn(
        "group flex rounded-lg px-3 py-3 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground",
        isActive 
          ? "bg-accent text-accent-foreground shadow-sm" 
          : "text-muted-foreground hover:text-foreground",
        // Adjust layout based on collapse state
        sidebarCollapsed ? "flex-col items-center space-y-1 lg:px-2" : "flex-col space-y-1"
      )}
      onClick={() => setSidebarOpen(false)}
      title={sidebarCollapsed ? item.name : ""}
    >
      <div className={cn(
        "flex items-center",
        sidebarCollapsed ? "lg:justify-center" : "space-x-3"
      )}>
        <Icon className="h-4 w-4 shrink-0" />
        <span className={cn(
          "font-medium transition-all duration-300",
          sidebarCollapsed ? "lg:hidden" : ""
        )}>
          {item.name}
        </span>
      </div>
      <p className={cn(
        "text-xs text-muted-foreground group-hover:text-muted-foreground/80 transition-all duration-300",
        sidebarCollapsed ? "lg:hidden" : "pl-7"
      )}>
        {item.description}
      </p>
    </Link>
  );
})}
```

---

### **STEP 5: Update Quick Actions Section (Line ~165)**

**Current code:**
```jsx
<div className="border-t border-border p-4 space-y-2">
  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider px-3">
    Acciones Rápidas
  </p>
  <Button
    variant="ghost"
    size="sm"
    className="w-full justify-start text-muted-foreground hover:text-foreground"
    onClick={() => {
      if (pathname !== '/app/dashboard') {
        router.push('/app/dashboard');
      }
    }}
  >
    <MessageSquare className="mr-2 h-4 w-4" />
    Nueva Conversación
  </Button>
</div>
```

**Replace with:**
```jsx
<div className="border-t border-border p-4 space-y-2">
  <p className={cn(
    "text-xs font-medium text-muted-foreground uppercase tracking-wider px-3 transition-all duration-300",
    sidebarCollapsed ? "lg:hidden" : ""
  )}>
    Acciones Rápidas
  </p>
  <Button
    variant="ghost"
    size="sm"
    className={cn(
      "w-full text-muted-foreground hover:text-foreground transition-all duration-300",
      sidebarCollapsed ? "lg:px-2 lg:justify-center" : "justify-start"
    )}
    onClick={() => {
      if (pathname !== '/app/dashboard') {
        router.push('/app/dashboard');
      }
    }}
    title={sidebarCollapsed ? "Nueva Conversación" : ""}
  >
    <MessageSquare className={cn(
      "h-4 w-4 transition-all duration-300",
      sidebarCollapsed ? "" : "mr-2"
    )} />
    <span className={cn(
      "transition-all duration-300",
      sidebarCollapsed ? "lg:hidden" : ""
    )}>
      Nueva Conversación
    </span>
  </Button>
</div>
```

---

### **STEP 6: Update Main Content Layout (Line ~224)**

**Current code:**
```jsx
<div className="lg:pl-80">
```

**Replace with:**
```jsx
<div className={cn(
  "transition-all duration-300",
  sidebarCollapsed ? "lg:pl-20" : "lg:pl-80"
)}>
```

---

### **STEP 7: Add Import for Menu Icon (Line ~12)**

**Add to existing imports:**
```typescript
import { 
  LayoutDashboard, 
  Bot, 
  Settings, 
  LogOut,
  Menu,
  X,
  MessageSquare,
  Database
} from 'lucide-react';
```

---

## 🧪 Testing Checklist

After making these changes:

### **Desktop Testing:**
- [ ] Sidebar collapses when clicking the collapse button
- [ ] Logo scales down when collapsed
- [ ] Navigation items show only icons when collapsed
- [ ] Quick actions button shows only icon when collapsed
- [ ] Main content area adjusts width properly
- [ ] Collapsed state persists after page refresh
- [ ] Smooth 300ms animations work

### **Mobile Testing:**
- [ ] Mobile sidebar overlay still works
- [ ] Mobile close button still functions
- [ ] Mobile sidebar is always full width
- [ ] No layout issues on small screens

### **Responsiveness:**
- [ ] Transitions work smoothly between mobile/desktop
- [ ] No horizontal scrollbars appear
- [ ] Layout doesn't break at different screen sizes

## 🚨 If Something Breaks

**Immediate revert command:**
```bash
git checkout -- components/layouts/app-layout.tsx
```

**Then debug by adding changes one step at a time.**

## ✅ Success Result

You should see:
- Desktop sidebar that can collapse to a narrow icon-only version
- Smooth animations and transitions
- State persistence across page reloads
- All existing functionality preserved
- Mobile behavior unchanged

**Time to implement:** ~30-45 minutes  
**Difficulty:** Easy to Medium  
**Risk:** Low (changes are isolated to styling and state)

Ready to implement? Go step by step and test after each change! 🚀
