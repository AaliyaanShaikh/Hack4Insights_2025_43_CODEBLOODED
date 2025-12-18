// === FILE: src/components/BearCartDashboard/BearCartTheme.tsx ===
// Color & styling system for BearCart Paper-Glass Dashboard

export const BEARCART_COLORS = {
  // Primary E-Commerce Colors
  primary: {
    purple: "#7c3aed", // Vibrant purple for BearCart
    indigo: "#4f46e5",
    blue: "#3b82f6",
    teal: "#14b8a6",
  },
  
  // Status Colors
  status: {
    success: "#10b981", // Green - high conversion
    warning: "#f59e0b", // Amber - medium performance
    danger: "#ef4444", // Red - low performance / refunds
    info: "#06b6d4", // Cyan - information
  },
  
  // Data-Specific Colors
  channels: {
    organic: "#8b5cf6", // Purple
    paid: "#ec4899", // Pink
    social: "#f59e0b", // Amber
    direct: "#14b8a6", // Teal
    referral: "#3b82f6", // Blue
  },
  
  // Device Colors
  devices: {
    desktop: "#6366f1", // Indigo
    mobile: "#f472b6", // Pink
    tablet: "#fbbf24", // Amber
  },
  
  // Neutral
  neutral: {
    bg: "#f0f4f8",
    surface: "#ffffff",
    border: "#000000",
    text: "#1e293b",
    textSecondary: "#64748b",
    textTertiary: "#94a3b8",
  },
};

export const BEARCART_METRICS = {
  // Conversion funnel stages
  funnelStages: ["Sessions", "Browse", "Add to Cart", "Checkout", "Purchase"],
  
  // KPI categories
  kpiCategories: ["Revenue", "Conversion", "Quality", "Engagement"],
  
  // Time range options
  timeRanges: ["Day", "Week", "Month", "Quarter", "Year"],
  
  // Chart types for dashboard
  chartTypes: ["Area", "Bar", "Line", "Pie", "Funnel"],
};
