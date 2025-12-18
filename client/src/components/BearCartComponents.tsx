import React from "react";
import { motion } from "framer-motion";
import { TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/src/lib/utils";
import { BEARCART_COLORS } from "./BearCartTheme";

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

// --- UI Components (Hybrid Style) ---

export interface HybridCardProps {
    children: React.ReactNode;
    className?: string;
    delay?: number;
    interactive?: boolean;
}

export function HybridCard({ children, className = "", delay = 0, interactive = false }: HybridCardProps) {
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

export interface StickerProps {
    children: React.ReactNode;
    className?: string;
    rotate?: number;
}

export function Sticker({ children, className = "", rotate = 0 }: StickerProps) {
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

export interface DoodleButtonProps {
    children: React.ReactNode;
    active: boolean;
    onClick: () => void;
    icon: React.ReactNode;
    className?: string;
    variant?: "primary" | "secondary";
}

export function DoodleButton({
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
export interface KPICardProps {
    label: string;
    value: string | number;
    trend?: number;
    icon: React.ReactNode;
    color: string;
    delay?: number;
    format?: "currency" | "percentage" | "number";
}

export function KPICard({
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
export function SketchDot(props: any) {
    const { cx, cy, payload } = props;
    if (!payload) return null;

    return (
        <svg x={cx - 6} y={cy - 6} width={12} height={12} fill="white" viewBox="0 0 10 10">
            <circle cx="5" cy="5" r="4" stroke="black" strokeWidth="2" fill={payload.revenue > 5000 ? "#fbbf24" : "white"} />
        </svg>
    );
}
