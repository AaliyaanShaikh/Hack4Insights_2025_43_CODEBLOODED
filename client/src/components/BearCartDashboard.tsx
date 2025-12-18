// === FILE: src/components/BearCartDashboard/BearCartDashboard.tsx ===
"use client";

import React, { useState, useMemo } from "react";
import {
  motion,
  AnimatePresence,
} from "framer-motion";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  ScatterChart,
  Scatter,
} from "recharts";
import {
  LayoutGrid,
  TrendingUp,
  Users,
  Wallet,
  Settings,
  Bell,
  Search,
  Sparkles,
  Zap,
  MessageCircle,
  Menu,
  X,
  Heart,
  Pencil,
  Filter,
  Download,
  Eye,
  BarChart3,
  PieChart as PieChartIcon,
  Activity,
  AlertCircle,
  CheckCircle,
  ShoppingCart,
  Package,
  DollarSign,
  Target,
  TrendingDown,
} from "lucide-react";
import { cn } from "@/src/lib/utils";
import { BEARCART_COLORS, BEARCART_METRICS } from "./BearCartTheme";

// --- Global Styles Component ---
export function GlobalStyles() {
  return (
    <style jsx global>{`
      @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&family=Gochi+Hand&display=swap');

      body {
        background-color: ${BEARCART_COLORS.neutral.bg};
        font-family: 'Fredoka', sans-serif;
        overflow-x: hidden;
      }

      .font-sketch {
        font-family: 'Gochi Hand', cursive;
      }

      /* Dot Grid Background */
      .bg-dots {
        background-image: radial-gradient(${BEARCART_COLORS.neutral.textTertiary} 2px, transparent 2px);
        background-size: 30px 30px;
      }

      /* Wobbly underline animation */
      @keyframes scribble {
        0% { transform: skewX(0deg) scaleY(1); }
        50% { transform: skewX(-5deg) scaleY(1.1); }
        100% { transform: skewX(0deg) scaleY(1); }
      }

      /* Floating animation */
      @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
      }

      .animate-float {
        animation: float 3s ease-in-out infinite;
      }

      /* Pulse animation for blobs */
      @keyframes blob-pulse {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.6; }
      }

      .animate-blob {
        animation: blob-pulse 4s ease-in-out infinite;
      }

      /* Scrollbar styling */
      ::-webkit-scrollbar {
        width: 8px;
      }

      ::-webkit-scrollbar-track {
        background: transparent;
      }

      ::-webkit-scrollbar-thumb {
        background: ${BEARCART_COLORS.neutral.border};
        border-radius: 4px;
      }

      ::-webkit-scrollbar-thumb:hover {
        background: ${BEARCART_COLORS.primary.purple};
      }
    `}</style>
  );
}

// --- Dummy Data Generation for BearCart ---

// Generate realistic e-commerce data
const generateRevenueData = () => {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  return days.map(day => ({
    name: day,
    revenue: Math.floor(Math.random() * 8000 + 2000),
    orders: Math.floor(Math.random() * 150 + 50),
    visitors: Math.floor(Math.random() * 5000 + 2000),
  }));
};

const generateChannelData = () => [
  { name: 'Organic', revenue: 28450, orders: 342, conversion: 4.2, color: BEARCART_COLORS.channels.organic },
  { name: 'Paid Ads', revenue: 18920, orders: 156, conversion: 2.1, color: BEARCART_COLORS.channels.paid },
  { name: 'Social', revenue: 12340, orders: 98, conversion: 1.8, color: BEARCART_COLORS.channels.social },
  { name: 'Direct', revenue: 8920, orders: 67, conversion: 1.2, color: BEARCART_COLORS.channels.direct },
  { name: 'Referral', revenue: 5670, orders: 42, conversion: 0.9, color: BEARCART_COLORS.channels.referral },
];

const generateProductData = () => [
  { id: 1, name: 'Premium Hoodie', category: 'Apparel', sales: 342, revenue: 12780, refundRate: 3.2 },
  { id: 2, name: 'Wireless Earbuds', category: 'Electronics', sales: 156, revenue: 11700, refundRate: 5.8 },
  { id: 3, name: 'Office Chair', category: 'Furniture', sales: 89, revenue: 8910, refundRate: 2.1 },
  { id: 4, name: 'USB-C Cable', category: 'Accessories', sales: 567, revenue: 5670, refundRate: 1.2 },
  { id: 5, name: 'Phone Stand', category: 'Accessories', sales: 234, revenue: 1404, refundRate: 0.8 },
];

const generateDeviceData = () => [
  { name: 'Desktop', value: 45000, sessions: 12340, conversion: 3.8, color: BEARCART_COLORS.devices.desktop },
  { name: 'Mobile', value: 38500, sessions: 18920, conversion: 1.9, color: BEARCART_COLORS.devices.mobile },
  { name: 'Tablet', value: 16500, sessions: 4560, conversion: 2.5, color: BEARCART_COLORS.devices.tablet },
];

const generateTimeSeriesData = () => {
  const hours = Array.from({ length: 24 }, (_, i) => i);
  return hours.map(hour => ({
    time: `${String(hour).padStart(2, '0')}:00`,
    hour,
    conversions: Math.floor(Math.random() * 50 + 10),
    revenue: Math.floor(Math.random() * 2000 + 500),
    bounceRate: Math.floor(Math.random() * 40 + 20),
  }));
};

const generateFunnelData = () => [
  { stage: 'Sessions', value: 45000, color: BEARCART_COLORS.primary.purple },
  { stage: 'Product View', value: 32400, color: BEARCART_COLORS.primary.indigo },
  { stage: 'Add to Cart', value: 8100, color: BEARCART_COLORS.primary.blue },
  { stage: 'Checkout', value: 2430, color: BEARCART_COLORS.status.warning },
  { stage: 'Purchase', value: 1215, color: BEARCART_COLORS.status.success },
];

const generateCategoryPerformance = () => [
  { category: 'Electronics', revenue: 34500, trend: 12, refundRate: 6.2 },
  { category: 'Apparel', revenue: 28900, trend: 8, refundRate: 3.5 },
  { category: 'Furniture', revenue: 18450, trend: -2, refundRate: 2.1 },
  { category: 'Accessories', revenue: 21240, trend: 15, refundRate: 1.8 },
  { category: 'Home Goods', revenue: 15600, trend: 5, refundRate: 2.8 },
];

const generateRefundData = () => [
  { reason: 'Damaged', count: 45, percentage: 28, color: BEARCART_COLORS.status.danger },
  { reason: 'Wrong Size', count: 38, percentage: 24, color: BEARCART_COLORS.status.warning },
  { reason: 'Not as Described', count: 32, percentage: 20, color: BEARCART_COLORS.status.info },
  { reason: 'Changed Mind', count: 26, percentage: 16, color: BEARCART_COLORS.status.info },
  { reason: 'Defective', count: 18, percentage: 12, color: BEARCART_COLORS.status.danger },
];

// --- UI Components (Hybrid Style) ---

interface HybridCardProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  interactive?: boolean;
}

function HybridCard({ children, className = "", delay = 0, interactive = false }: HybridCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, type: "spring", stiffness: 200, damping: 20 }}
      whileHover={interactive ? { y: -4, rotate: 0.5, boxShadow: "6px 6px 0px 0px rgba(0,0,0,1)" } : {}}
      className={cn(
        "relative overflow-hidden rounded-3xl border-[3px] border-black bg-white/60 backdrop-blur-xl p-6 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] transition-all",
        interactive && "cursor-pointer",
        className
      )}
    >
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />
      <div className="relative z-10">{children}</div>
    </motion.div>
  );
}

interface StickerProps {
  children: React.ReactNode;
  className?: string;
  rotate?: number;
}

function Sticker({ children, className = "", rotate = 0 }: StickerProps) {
  return (
    <motion.div
      drag
      dragConstraints={{ left: -10, right: 10, top: -10, bottom: 10 }}
      whileDrag={{ scale: 1.1 }}
      className={cn(
        "absolute flex items-center justify-center rounded-full border-2 border-black bg-white shadow-[2px_2px_0px_#000] z-20 cursor-grab active:cursor-grabbing",
        className
      )}
      style={{ rotate: rotate }}
    >
      {children}
    </motion.div>
  );
}

interface DoodleButtonProps {
  children: React.ReactNode;
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  className?: string;
  variant?: "primary" | "secondary";
}

function DoodleButton({
  children,
  active,
  onClick,
  icon,
  className = "",
  variant = "primary"
}: DoodleButtonProps) {
  return (
    <motion.button
      onClick={onClick}
      whileTap={{ scale: 0.95 }}
      whileHover={{ scale: 1.02 }}
      className={cn(
        "flex items-center gap-3 rounded-2xl border-[3px] border-transparent px-4 py-3 font-bold transition-all",
        active
          ? "bg-black text-white border-black shadow-[4px_4px_0px_rgba(0,0,0,0.2)]"
          : "text-slate-600 hover:bg-white/50 hover:border-black/10",
        className
      )}
    >
      <span className={cn("w-6 h-6 stroke-[3px]", active ? "text-yellow-300" : "text-slate-400")}>
        {icon}
      </span>
      {children}
    </motion.button>
  );
}

// --- KPI Card Component ---
interface KPICardProps {
  label: string;
  value: string | number;
  trend?: number;
  icon: React.ReactNode;
  color: string;
  delay?: number;
  format?: "currency" | "percentage" | "number";
}

function KPICard({
  label,
  value,
  trend,
  icon,
  color,
  delay = 0,
  format = "number"
}: KPICardProps) {
  const isPositive = (trend ?? 0) >= 0;

  let displayValue = value;
  if (format === "currency") {
    displayValue = `$${Number(value).toLocaleString()}`;
  } else if (format === "percentage") {
    displayValue = `${value}%`;
  }

  return (
    <HybridCard
      delay={delay}
      className={cn("flex flex-col justify-between", color)}
      interactive
    >
      <div className="flex justify-between items-start">
        <span className="font-bold text-slate-600 text-sm">{label}</span>
        <div className="w-10 h-10 bg-white border-2 border-black rounded-full flex items-center justify-center">
          {icon}
        </div>
      </div>
      <div className="text-4xl font-black mt-4">{displayValue}</div>
      {trend !== undefined && (
        <div className={cn(
          "font-sketch text-sm mt-2 flex items-center gap-1",
          isPositive ? "text-green-600" : "text-red-600"
        )}>
          {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
          {isPositive ? "+" : ""}{trend}% this month
        </div>
      )}
    </HybridCard>
  );
}

// --- Custom Chart Dot Component ---
function SketchDot(props: any) {
  const { cx, cy, payload } = props;
  if (!payload) return null;

  return (
    <svg x={cx - 6} y={cy - 6} width={12} height={12} fill="white" viewBox="0 0 10 10">
      <circle cx="5" cy="5" r="4" stroke="black" strokeWidth="2" fill={payload.revenue > 5000 ? "#fbbf24" : "white"} />
    </svg>
  );
}

// --- Main Dashboard Component ---

export default function BearCartDashboard() {
  const [activeTab, setActiveTab] = useState("Overview");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [timeRange, setTimeRange] = useState("Week");
  const [selectedChannel, setSelectedChannel] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  // Generate all data
  const revenueData = useMemo(() => generateRevenueData(), []);
  const channelData = useMemo(() => generateChannelData(), []);
  const productData = useMemo(() => generateProductData(), []);
  const deviceData = useMemo(() => generateDeviceData(), []);
  const timeSeriesData = useMemo(() => generateTimeSeriesData(), []);
  const funnelData = useMemo(() => generateFunnelData(), []);
  const categoryPerformance = useMemo(() => generateCategoryPerformance(), []);
  const refundData = useMemo(() => generateRefundData(), []);

  // Calculate KPIs
  const totalRevenue = channelData.reduce((sum, item) => sum + item.revenue, 0);
  const totalOrders = channelData.reduce((sum, item) => sum + item.orders, 0);
  const avgConversion = (channelData.reduce((sum, item) => sum + item.conversion, 0) / channelData.length).toFixed(1);
  const totalSessions = funnelData[0].value;
  const conversionRate = ((funnelData[funnelData.length - 1].value / totalSessions) * 100).toFixed(2);
  const avgOrderValue = (totalRevenue / totalOrders).toFixed(2);
  const totalRefunds = refundData.reduce((sum, item) => sum + item.count, 0);
  const refundRate = ((totalRefunds / totalOrders) * 100).toFixed(1);

  // Filter data based on selections
  const filteredChannelData = selectedChannel
    ? channelData.filter(item => item.name === selectedChannel)
    : channelData;

  const filteredCategoryData = selectedCategory
    ? categoryPerformance.filter(item => item.category === selectedCategory)
    : categoryPerformance;

  return (
    <div className="min-h-screen bg-dots text-slate-800 selection:bg-yellow-200">
      <GlobalStyles />

      {/* Background Blobs (Glass Effect) */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[600px] h-[600px] bg-purple-400/20 rounded-full blur-[100px] animate-blob" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] bg-pink-400/20 rounded-full blur-[100px] animate-blob" style={{ animationDelay: "1s" }} />
        <div className="absolute top-1/2 left-1/2 w-[400px] h-[400px] bg-blue-400/20 rounded-full blur-[100px] animate-blob" style={{ animationDelay: "2s" }} />
      </div>

      <div className="relative z-10 flex h-screen overflow-hidden p-4 lg:p-6 gap-6">

        {/* ========== SIDEBAR ========== */}
        <aside className={cn(
          "fixed inset-y-0 left-0 z-50 w-72 bg-white/80 backdrop-blur-2xl border-r-[3px] border-black p-6 flex flex-col gap-6 transition-transform lg:relative lg:translate-x-0 lg:rounded-[32px] lg:border-[3px] lg:shadow-[6px_6px_0px_#000] lg:h-full overflow-y-auto",
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        )}>

          {/* Logo Area */}
          <div className="flex items-center gap-3 px-2">
            <div className="relative">
              <div className="w-12 h-12 bg-purple-400 rounded-xl border-[3px] border-black shadow-[3px_3px_0px_#000] flex items-center justify-center">
                <ShoppingCart className="w-6 h-6 text-black fill-white" />
              </div>
              <Sticker className="w-6 h-6 -top-2 -right-2 bg-pink-400 text-white border-white rotate-12" rotate={12}>
                <span className="text-[10px] font-bold">PRO</span>
              </Sticker>
            </div>
            <div>
              <h1 className="text-2xl font-black tracking-tight leading-none">BearCart</h1>
              <p className="font-sketch text-slate-500 text-sm">Analytics</p>
            </div>
            <button onClick={() => setMobileOpen(false)} className="lg:hidden ml-auto">
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex flex-col gap-2 flex-1 mt-4">
            {[
              { id: "Overview", icon: LayoutGrid },
              { id: "Channels", icon: Activity },
              { id: "Products", icon: Package },
              { id: "Funnel", icon: ShoppingCart },
              { id: "Reports", icon: BarChart3 },
              { id: "Settings", icon: Settings },
            ].map((item) => (
              <DoodleButton
                key={item.id}
                active={activeTab === item.id}
                onClick={() => {
                  setActiveTab(item.id);
                  setMobileOpen(false);
                }}
                icon={<item.icon className="w-5 h-5" />}
                className="w-full justify-start"
              >
                {item.id}
              </DoodleButton>
            ))}
          </nav>

          {/* User Profile */}
          <HybridCard className="p-4 flex items-center gap-3 bg-gradient-to-r from-purple-100/50 to-pink-100/50" delay={0}>
            <div className="w-10 h-10 rounded-full border-2 border-black overflow-hidden bg-white">
              <img src="https://api.dicebear.com/7.x/notionists/svg?seed=BearCart" alt="Admin" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-bold text-sm truncate">Admin User</p>
              <p className="text-xs text-slate-500 truncate">analytics@bearcart.io</p>
            </div>
          </HybridCard>
        </aside>

        {/* ========== MAIN CONTENT ========== */}
        <main className="flex-1 flex flex-col min-w-0 h-full">

          {/* Header */}
          <header className="flex items-center justify-between mb-6 flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <button onClick={() => setMobileOpen(true)} className="lg:hidden p-2 bg-white border-2 border-black rounded-xl">
                <Menu className="w-6 h-6" />
              </button>
              <div>
                <h2 className="text-3xl font-black text-slate-900">
                  {activeTab} <span className="inline-block animate-bounce">📊</span>
                </h2>
                <p className="font-sketch text-slate-500 text-lg">Real-time e-commerce analytics</p>
              </div>
            </div>

            <div className="flex items-center gap-3 flex-wrap">
              {/* Search */}
              <div className="hidden md:flex relative group">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-black transition-colors" />
                <input
                  type="text"
                  placeholder="Search metrics..."
                  className="pl-10 pr-4 py-3 bg-white/60 backdrop-blur-md border-[3px] border-transparent focus:border-black rounded-2xl w-64 transition-all focus:shadow-[4px_4px_0px_#000] outline-none font-bold"
                />
              </div>

              {/* Time Range */}
              <div className="flex gap-2 bg-slate-100 p-2 rounded-2xl border-2 border-black shadow-[2px_2px_0px_#000]">
                {BEARCART_METRICS.timeRanges.map(range => (
                  <button
                    key={range}
                    onClick={() => setTimeRange(range)}
                    className={cn(
                      "px-3 py-2 text-sm font-bold rounded-lg transition-all",
                      timeRange === range
                        ? "bg-purple-400 text-white shadow-[2px_2px_0px_#000]"
                        : "hover:bg-white hover:shadow-sm"
                    )}
                  >
                    {range}
                  </button>
                ))}
              </div>

              {/* Notifications */}
              <button className="relative w-12 h-12 bg-white border-[3px] border-black rounded-full flex items-center justify-center shadow-[2px_2px_0px_#000] active:translate-y-1 active:shadow-none transition-all hover:bg-purple-50">
                <Bell className="w-6 h-6" />
                <span className="absolute top-0 right-0 w-4 h-4 bg-red-500 border-2 border-white rounded-full text-white text-xs font-bold flex items-center justify-center">3</span>
              </button>

              {/* Export */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="w-12 h-12 bg-white border-[3px] border-black rounded-full flex items-center justify-center shadow-[2px_2px_0px_#000] hover:bg-purple-50"
              >
                <Download className="w-6 h-6" />
              </motion.button>
            </div>
          </header>

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto pr-2">
            <AnimatePresence mode="wait">

              {/* ===== OVERVIEW TAB ===== */}
              {activeTab === "Overview" && (
                <motion.div
                  key="overview"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-6 pb-10"
                >
                  {/* KPI Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <KPICard
                      label="Total Revenue"
                      value={totalRevenue}
                      trend={12}
                      icon={<DollarSign className="w-5 h-5 text-purple-600" />}
                      color="bg-gradient-to-br from-purple-50 to-indigo-50"
                      delay={0}
                      format="currency"
                    />
                    <KPICard
                      label="Total Orders"
                      value={totalOrders}
                      trend={8}
                      icon={<ShoppingCart className="w-5 h-5 text-blue-600" />}
                      color="bg-gradient-to-br from-blue-50 to-cyan-50"
                      delay={0.1}
                    />
                    <KPICard
                      label="Conversion Rate"
                      value={conversionRate}
                      trend={-2}
                      icon={<Target className="w-5 h-5 text-green-600" />}
                      color="bg-gradient-to-br from-green-50 to-emerald-50"
                      delay={0.2}
                      format="percentage"
                    />
                    <KPICard
                      label="Avg Order Value"
                      value={avgOrderValue}
                      trend={5}
                      icon={<Wallet className="w-5 h-5 text-amber-600" />}
                      color="bg-gradient-to-br from-amber-50 to-orange-50"
                      delay={0.3}
                      format="currency"
                    />
                  </div>

                  {/* Main Revenue Chart */}
                  <HybridCard delay={0.4} interactive className="md:col-span-2 lg:col-span-3 min-h-[400px]">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-2xl font-black flex items-center gap-2">
                        Revenue Trend
                        <TrendingUp className="w-6 h-6 text-purple-600" />
                      </h3>
                    </div>

                    <div className="h-[300px] w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={revenueData}>
                          <defs>
                            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor={BEARCART_COLORS.primary.purple} stopOpacity={0.4} />
                              <stop offset="95%" stopColor={BEARCART_COLORS.primary.purple} stopOpacity={0} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                          <XAxis dataKey="name" tick={{ fontFamily: 'Gochi Hand', fontSize: 14, fill: '#64748b' }} />
                          <YAxis tick={{ fontFamily: 'Gochi Hand', fontSize: 12, fill: '#64748b' }} />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'rgba(255, 255, 255, 0.9)',
                              backdropFilter: 'blur(8px)',
                              borderRadius: '16px',
                              border: '3px solid black',
                              boxShadow: '4px 4px 0px black',
                              fontFamily: 'Fredoka',
                              fontWeight: 'bold'
                            }}
                            formatter={(value) => [`$${value}`, 'Revenue']}
                          />
                          <Area
                            type="monotone"
                            dataKey="revenue"
                            stroke="#000"
                            strokeWidth={3}
                            fill="url(#colorRevenue)"
                            dot={<SketchDot />}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </HybridCard>

                  {/* Funnel & Refunds Row */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                    {/* Conversion Funnel */}
                    <HybridCard delay={0.5} interactive className="flex flex-col">
                      <h3 className="text-xl font-black mb-6 flex items-center gap-2">
                        Conversion Funnel
                        <ShoppingCart className="w-5 h-5 text-blue-600" />
                      </h3>
                      <div className="space-y-3 flex-1">
                        {funnelData.map((stage, idx) => {
                          const percentage = ((stage.value / funnelData[0].value) * 100).toFixed(1);
                          const dropoff = idx > 0 ? (((funnelData[idx - 1].value - stage.value) / funnelData[idx - 1].value) * 100).toFixed(1) : null;

                          return (
                            <motion.div
                              key={stage.stage}
                              initial={{ opacity: 0, x: -20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: 0.5 + idx * 0.1 }}
                              className="space-y-2"
                            >
                              <div className="flex justify-between items-center">
                                <span className="font-bold text-sm">{stage.stage}</span>
                                <div className="flex gap-2 items-center">
                                  <span className="font-bold">{stage.value.toLocaleString()}</span>
                                  {dropoff && <span className="text-xs text-red-600 font-sketch">-{dropoff}%</span>}
                                </div>
                              </div>
                              <div className="h-6 bg-slate-200 rounded-full border-2 border-black overflow-hidden">
                                <motion.div
                                  initial={{ width: 0 }}
                                  animate={{ width: `${percentage}%` }}
                                  transition={{ delay: 0.6 + idx * 0.1, duration: 0.5 }}
                                  style={{ backgroundColor: stage.color }}
                                  className="h-full rounded-full"
                                />
                              </div>
                            </motion.div>
                          );
                        })}
                      </div>
                    </HybridCard>

                    {/* Refund Analysis */}
                    <HybridCard delay={0.6} interactive className="flex flex-col">
                      <h3 className="text-xl font-black mb-6 flex items-center gap-2">
                        Refund Reasons
                        <AlertCircle className="w-5 h-5 text-red-600" />
                      </h3>
                      <div className="space-y-3 flex-1">
                        {refundData.map((item, idx) => (
                          <motion.div
                            key={item.reason}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.6 + idx * 0.1 }}
                            className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border-2 border-slate-200 hover:border-black transition-all"
                          >
                            <div className="flex items-center gap-3 flex-1">
                              <div
                                className="w-4 h-4 rounded-full border-2 border-black"
                                style={{ backgroundColor: item.color }}
                              />
                              <span className="font-bold text-sm">{item.reason}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-xs bg-white px-2 py-1 rounded border border-black font-bold">
                                {item.count}
                              </span>
                              <span className="font-sketch text-xs text-slate-500">{item.percentage}%</span>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                      <div className="mt-4 p-3 bg-red-50 rounded-xl border-2 border-red-200">
                        <p className="text-sm font-bold text-red-900">
                          Total Refunds: <span className="text-xl">{totalRefunds}</span> ({refundRate}% rate)
                        </p>
                      </div>
                    </HybridCard>
                  </div>

                  {/* Channel & Device Performance */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                    {/* Device Breakdown - Pie Chart */}
                    <HybridCard delay={0.7} interactive className="flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-cyan-50">
                      <h3 className="text-xl font-black mb-4 self-start w-full">Device Breakdown</h3>
                      <div className="relative w-full h-[250px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <PieChart>
                            <Pie
                              data={deviceData}
                              innerRadius={60}
                              outerRadius={90}
                              paddingAngle={3}
                              dataKey="value"
                              stroke="black"
                              strokeWidth={2}
                            >
                              {deviceData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                              ))}
                            </Pie>
                            <Tooltip
                              contentStyle={{
                                borderRadius: '12px',
                                border: '2px solid black',
                                fontFamily: 'Fredoka',
                                fontWeight: 'bold'
                              }}
                              formatter={(value) => `$${value?.toLocaleString() ?? ''}`}
                            />
                          </PieChart>
                        </ResponsiveContainer>
                      </div>
                      <div className="w-full space-y-2 mt-4">
                        {deviceData.map((device) => (
                          <div key={device.name} className="flex items-center justify-between text-sm p-2 hover:bg-white rounded-lg transition-colors">
                            <div className="flex items-center gap-3">
                              <div
                                className="w-4 h-4 rounded-full border-2 border-black"
                                style={{ backgroundColor: device.color }}
                              />
                              <span className="font-bold">{device.name}</span>
                            </div>
                            <div className="flex gap-3">
                              <span className="font-sketch text-xs text-slate-500">{device.sessions.toLocaleString()} sessions</span>
                              <span className="font-bold text-green-600">{device.conversion.toFixed(1)}%</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </HybridCard>

                    {/* Top Products */}
                    <HybridCard delay={0.8} interactive className="flex flex-col">
                      <h3 className="text-xl font-black mb-4">Top Products</h3>
                      <div className="space-y-3 flex-1 overflow-y-auto">
                        {productData.map((product, idx) => (
                          <motion.div
                            key={product.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.8 + idx * 0.08 }}
                            className="p-3 bg-gradient-to-r from-slate-50 to-transparent rounded-xl border-2 border-slate-200 hover:border-purple-400 transition-all cursor-pointer"
                          >
                            <div className="flex justify-between items-start mb-2">
                              <div>
                                <p className="font-bold text-sm">{product.name}</p>
                                <p className="text-xs text-slate-500">{product.category}</p>
                              </div>
                              <span className="text-xs bg-purple-200 text-purple-900 px-2 py-1 rounded font-bold">
                                #{idx + 1}
                              </span>
                            </div>
                            <div className="flex justify-between items-center text-xs">
                              <span className="font-bold">${product.revenue.toLocaleString()}</span>
                              <span className="text-slate-500">{product.sales} sales</span>
                              <span className="text-red-600">{product.refundRate}% refund</span>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </HybridCard>
                  </div>

                </motion.div>
              )}

              {/* ===== CHANNELS TAB ===== */}
              {activeTab === "Channels" && (
                <motion.div
                  key="channels"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-6 pb-10"
                >
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Channel Selector */}
                    <HybridCard delay={0} interactive className="lg:col-span-1">
                      <h3 className="text-xl font-black mb-4">Traffic Sources</h3>
                      <div className="space-y-2">
                        <motion.button
                          onClick={() => setSelectedChannel(null)}
                          whileHover={{ x: 4 }}
                          className={cn(
                            "w-full p-3 rounded-xl font-bold text-left transition-all border-2",
                            !selectedChannel
                              ? "bg-purple-400 text-white border-black shadow-[2px_2px_0px_#000]"
                              : "border-slate-200 hover:border-black"
                          )}
                        >
                          All Channels
                        </motion.button>
                        {channelData.map((channel) => (
                          <motion.button
                            key={channel.name}
                            onClick={() => setSelectedChannel(channel.name)}
                            whileHover={{ x: 4 }}
                            className={cn(
                              "w-full p-3 rounded-xl font-bold text-left transition-all border-2 flex items-center gap-2",
                              selectedChannel === channel.name
                                ? "bg-black text-white border-black shadow-[2px_2px_0px_#000]"
                                : "border-slate-200 hover:border-black"
                            )}
                          >
                            <div
                              className="w-3 h-3 rounded-full"
                              style={{ backgroundColor: channel.color }}
                            />
                            {channel.name}
                          </motion.button>
                        ))}
                      </div>
                    </HybridCard>

                    {/* Channel Metrics */}
                    <HybridCard delay={0.1} interactive className="lg:col-span-2">
                      <h3 className="text-xl font-black mb-6">Performance Metrics</h3>
                      <div className="space-y-3">
                        {filteredChannelData.map((channel, idx) => (
                          <motion.div
                            key={channel.name}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.2 + idx * 0.1 }}
                            className="p-4 bg-gradient-to-r from-slate-50 to-transparent rounded-xl border-2 border-slate-200 hover:border-black transition-all"
                          >
                            <div className="flex justify-between items-start mb-3">
                              <div>
                                <p className="font-black text-lg">{channel.name}</p>
                                <p className="text-sm text-slate-500">{channel.orders} orders</p>
                              </div>
                              <div className="text-right">
                                <p className="font-black text-2xl">${channel.revenue.toLocaleString()}</p>
                                <p className="text-sm text-green-600 font-bold">{channel.conversion}% Conv.</p>
                              </div>
                            </div>
                            <div className="h-2 bg-slate-200 rounded-full border border-black overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${channel.conversion * 10}%` }}
                                transition={{ delay: 0.3 + idx * 0.1, duration: 0.5 }}
                                style={{ backgroundColor: channel.color }}
                                className="h-full"
                              />
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </HybridCard>
                  </div>

                  {/* Channel Comparison Chart */}
                  <HybridCard delay={0.3} interactive className="min-h-[400px]">
                    <h3 className="text-2xl font-black mb-6">Channel Comparison</h3>
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={channelData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                          <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#64748b' }} />
                          <YAxis tick={{ fontSize: 12, fill: '#64748b' }} />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'rgba(255, 255, 255, 0.9)',
                              borderRadius: '12px',
                              border: '2px solid black',
                              fontFamily: 'Fredoka',
                              fontWeight: 'bold'
                            }}
                          />
                          <Legend />
                          <Bar dataKey="revenue" fill={BEARCART_COLORS.primary.purple} stroke="black" strokeWidth={2} />
                          <Bar dataKey="orders" fill={BEARCART_COLORS.primary.blue} stroke="black" strokeWidth={2} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </HybridCard>

                </motion.div>
              )}

              {/* ===== PRODUCTS TAB ===== */}
              {activeTab === "Products" && (
                <motion.div
                  key="products"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-6 pb-10"
                >

                  {/* Category Performance */}
                  <HybridCard delay={0} interactive className="min-h-[400px]">
                    <h3 className="text-2xl font-black mb-6">Category Performance</h3>
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={categoryPerformance} layout="vertical">
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                          <XAxis type="number" tick={{ fontSize: 12, fill: '#64748b' }} />
                          <YAxis type="category" dataKey="category" tick={{ fontSize: 11, fill: '#64748b' }} />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'rgba(255, 255, 255, 0.9)',
                              borderRadius: '12px',
                              border: '2px solid black',
                            }}
                            formatter={(value: number | undefined) => `$${value?.toLocaleString() ?? ''}`}
                          />
                          <Bar dataKey="revenue" fill={BEARCART_COLORS.primary.purple} stroke="black" strokeWidth={2} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </HybridCard>

                  {/* Product Details Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {productData.map((product, idx) => (
                      <HybridCard
                        key={product.id}
                        delay={0.1 * idx}
                        interactive
                        className="bg-gradient-to-br from-indigo-50 to-purple-50"
                      >
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h4 className="text-lg font-black">{product.name}</h4>
                            <p className="text-sm text-slate-500">{product.category}</p>
                          </div>
                          <span className={cn(
                            "text-xs font-bold px-2 py-1 rounded",
                            product.refundRate > 5
                              ? "bg-red-200 text-red-900"
                              : product.refundRate > 3
                                ? "bg-yellow-200 text-yellow-900"
                                : "bg-green-200 text-green-900"
                          )}>
                            {product.refundRate}% refund
                          </span>
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-center">
                          <div className="p-3 bg-white rounded-lg border-2 border-slate-200">
                            <p className="text-xs text-slate-500 font-bold mb-1">Sales</p>
                            <p className="text-xl font-black">{product.sales}</p>
                          </div>
                          <div className="p-3 bg-white rounded-lg border-2 border-slate-200">
                            <p className="text-xs text-slate-500 font-bold mb-1">Revenue</p>
                            <p className="text-xl font-black">${(product.revenue / 1000).toFixed(1)}k</p>
                          </div>
                          <div className="p-3 bg-white rounded-lg border-2 border-slate-200">
                            <p className="text-xs text-slate-500 font-bold mb-1">Avg Price</p>
                            <p className="text-xl font-black">${(product.revenue / product.sales).toFixed(0)}</p>
                          </div>
                        </div>
                      </HybridCard>
                    ))}
                  </div>

                </motion.div>
              )}

              {/* ===== FUNNEL TAB ===== */}
              {activeTab === "Funnel" && (
                <motion.div
                  key="funnel"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-6 pb-10"
                >

                  {/* Hourly Time Series */}
                  <HybridCard delay={0} interactive className="min-h-[400px]">
                    <h3 className="text-2xl font-black mb-6">Conversion by Hour</h3>
                    <div className="h-[300px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={timeSeriesData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                          <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#64748b' }} />
                          <YAxis tick={{ fontSize: 12, fill: '#64748b' }} />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: 'rgba(255, 255, 255, 0.9)',
                              borderRadius: '12px',
                              border: '2px solid black',
                            }}
                          />
                          <Legend />
                          <Line
                            type="monotone"
                            dataKey="conversions"
                            stroke={BEARCART_COLORS.primary.purple}
                            strokeWidth={3}
                            dot={{ fill: 'black', r: 4 }}
                            activeDot={{ r: 6 }}
                          />
                          <Line
                            type="monotone"
                            dataKey="bounceRate"
                            stroke={BEARCART_COLORS.status.danger}
                            strokeWidth={3}
                            dot={{ fill: 'black', r: 4 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </HybridCard>

                  {/* Funnel Detailed Breakdown */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <HybridCard delay={0.2} interactive>
                      <h3 className="text-xl font-black mb-6">Stage Analysis</h3>
                      <div className="space-y-4">
                        {funnelData.map((stage, idx) => {
                          const prevValue = idx > 0 ? funnelData[idx - 1].value : stage.value;
                          const dropoff = ((prevValue - stage.value) / prevValue * 100).toFixed(1);
                          const percentage = ((stage.value / funnelData[0].value) * 100).toFixed(1);

                          return (
                            <motion.div
                              key={stage.stage}
                              initial={{ opacity: 0, x: -20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: 0.3 + idx * 0.1 }}
                              className="space-y-2"
                            >
                              <div className="flex justify-between items-center">
                                <p className="font-bold">{stage.stage}</p>
                                <div className="text-right">
                                  <p className="font-black">{stage.value.toLocaleString()}</p>
                                  <p className="text-xs text-slate-500">{percentage}% of funnel</p>
                                </div>
                              </div>
                              {idx > 0 && (
                                <p className="text-xs text-red-600 font-bold">↓ {dropoff}% drop from previous</p>
                              )}
                              <div className="h-4 bg-slate-200 rounded-full border-2 border-black overflow-hidden">
                                <motion.div
                                  initial={{ width: 0 }}
                                  animate={{ width: `${percentage}%` }}
                                  transition={{ delay: 0.4 + idx * 0.1, duration: 0.5 }}
                                  style={{ backgroundColor: stage.color }}
                                  className="h-full rounded-full"
                                />
                              </div>
                            </motion.div>
                          );
                        })}
                      </div>
                    </HybridCard>

                    <HybridCard delay={0.3} interactive className="bg-gradient-to-br from-orange-50 to-red-50">
                      <h3 className="text-xl font-black mb-6">Optimization Opportunities</h3>
                      <div className="space-y-3">
                        {[
                          { step: "Product Page", dropoff: 28.6, impact: "High" },
                          { step: "Add to Cart", dropoff: 74.1, impact: "Critical" },
                          { step: "Checkout", dropoff: 50.0, impact: "High" },
                        ].map((opp, idx) => (
                          <motion.div
                            key={opp.step}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.4 + idx * 0.1 }}
                            className="p-3 bg-white rounded-xl border-2 border-orange-200 hover:border-black transition-all"
                          >
                            <div className="flex justify-between items-start mb-2">
                              <p className="font-bold">{opp.step}</p>
                              <span className={cn(
                                "text-xs font-bold px-2 py-1 rounded",
                                opp.impact === "Critical" ? "bg-red-200 text-red-900" : "bg-orange-200 text-orange-900"
                              )}>
                                {opp.impact}
                              </span>
                            </div>
                            <p className="text-sm text-slate-600">{opp.dropoff}% users drop off</p>
                          </motion.div>
                        ))}
                      </div>
                    </HybridCard>
                  </div>

                </motion.div>
              )}

              {/* ===== REPORTS TAB ===== */}
              {activeTab === "Reports" && (
                <motion.div
                  key="reports"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-6 pb-10"
                >
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[
                      { title: "Weekly Summary", date: "Dec 11-17, 2025", icon: Activity, color: "from-blue-50 to-cyan-50" },
                      { title: "Monthly Report", date: "December 2025", icon: BarChart3, color: "from-purple-50 to-pink-50" },
                      { title: "Custom Report", date: "Build Your Own", icon: Settings, color: "from-amber-50 to-orange-50" },
                      { title: "Product Analysis", date: "Real-time", icon: Package, color: "from-green-50 to-emerald-50" },
                      { title: "Channel Deep Dive", date: "Organic Performance", icon: Activity, color: "from-indigo-50 to-purple-50" },
                      { title: "Customer Insights", date: "Behavioral Data", icon: Users, color: "from-pink-50 to-red-50" },
                    ].map((report, idx) => (
                      <HybridCard
                        key={report.title}
                        delay={0.1 * idx}
                        interactive
                        className={`bg-gradient-to-br ${report.color} cursor-pointer flex flex-col items-center justify-center text-center p-8`}
                      >
                        <report.icon className="w-12 h-12 mb-4 text-slate-400" />
                        <h4 className="text-lg font-black mb-2">{report.title}</h4>
                        <p className="text-sm text-slate-500">{report.date}</p>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          className="mt-4 px-4 py-2 bg-black text-white rounded-lg font-bold text-sm border-2 border-black"
                        >
                          View →
                        </motion.button>
                      </HybridCard>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* ===== SETTINGS TAB ===== */}
              {activeTab === "Settings" && (
                <motion.div
                  key="settings"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-6 pb-10 max-w-2xl"
                >
                  <HybridCard delay={0} interactive className="space-y-6">
                    <h2 className="text-2xl font-black">Dashboard Settings</h2>

                    {/* Theme Toggle */}
                    <div className="space-y-2">
                      <label className="font-bold text-sm">Dashboard Theme</label>
                      <div className="flex gap-2">
                        {["Light", "Dark", "Auto"].map(theme => (
                          <motion.button
                            key={theme}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="px-4 py-2 rounded-lg border-2 border-black font-bold text-sm bg-white hover:bg-slate-100"
                          >
                            {theme}
                          </motion.button>
                        ))}
                      </div>
                    </div>

                    {/* Data Refresh */}
                    <div className="space-y-2">
                      <label className="font-bold text-sm">Auto Refresh</label>
                      <div className="flex gap-2">
                        {["Off", "30s", "1min", "5min"].map(interval => (
                          <motion.button
                            key={interval}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="px-4 py-2 rounded-lg border-2 border-black font-bold text-sm bg-white hover:bg-slate-100"
                          >
                            {interval}
                          </motion.button>
                        ))}
                      </div>
                    </div>

                    {/* Export Options */}
                    <div className="space-y-2">
                      <label className="font-bold text-sm">Export Data</label>
                      <div className="flex gap-2">
                        {["CSV", "PDF", "Excel", "JSON"].map(format => (
                          <motion.button
                            key={format}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="px-4 py-2 rounded-lg border-2 border-black font-bold text-sm bg-purple-400 text-white hover:bg-purple-500"
                          >
                            {format}
                          </motion.button>
                        ))}
                      </div>
                    </div>
                  </HybridCard>
                </motion.div>
              )}

            </AnimatePresence>

          </div>

        </main>
      </div>
    </div>
  );
}
