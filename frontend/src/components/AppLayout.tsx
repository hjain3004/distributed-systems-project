import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    LayoutDashboard,
    Calculator,
    GitCompare,
    Activity,
    Settings,
    Menu,
    X,
    RefreshCw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface AppLayoutProps {
    children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
    const location = useLocation();
    const [isSidebarOpen, setIsSidebarOpen] = React.useState(true);

    const navItems = [
        { path: '/', label: 'Dashboard', icon: LayoutDashboard },
        { path: '/control', label: 'Control Center', icon: Activity },
        { path: '/mmn', label: 'M/M/N Calculator', icon: Calculator },
        { path: '/mgn', label: 'M/G/N Calculator', icon: Activity },
        { path: '/compare', label: 'Model Comparison', icon: GitCompare },
        { path: '/tandem', label: 'Tandem Queue', icon: RefreshCw },
    ];

    return (
        <div className="min-h-screen bg-background font-sans antialiased flex">
            {/* Sidebar */}
            <motion.aside
                initial={{ width: isSidebarOpen ? 280 : 80 }}
                animate={{ width: isSidebarOpen ? 280 : 80 }}
                transition={{ duration: 0.3, ease: "easeInOut" }}
                className="h-screen sticky top-0 border-r bg-card/50 backdrop-blur-xl z-50 hidden md:flex flex-col"
            >
                <div className="p-6 flex items-center justify-between">
                    {isSidebarOpen ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="font-bold text-xl bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent"
                        >
                            QueueSim
                        </motion.div>
                    ) : (
                        <div className="w-full flex justify-center">
                            <Activity className="h-8 w-8 text-primary" />
                        </div>
                    )}
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                        className="ml-auto"
                    >
                        {isSidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
                    </Button>
                </div>

                <nav className="flex-1 px-4 space-y-2 py-4">
                    {navItems.map((item) => {
                        const isActive = location.pathname === item.path;
                        const Icon = item.icon;

                        return (
                            <Link to={item.path} key={item.path}>
                                <Button
                                    variant={isActive ? "secondary" : "ghost"}
                                    className={cn(
                                        "w-full justify-start gap-4 mb-1",
                                        !isSidebarOpen && "justify-center px-2"
                                    )}
                                >
                                    <Icon className={cn("h-5 w-5", isActive && "text-primary")} />
                                    {isSidebarOpen && <span>{item.label}</span>}
                                </Button>
                            </Link>
                        );
                    })}
                </nav>

                <div className="p-4 border-t">
                    {isSidebarOpen && (
                        <div className="text-xs text-muted-foreground text-center">
                            v2.0.0 • Distributed Systems
                        </div>
                    )}
                </div>
            </motion.aside>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto bg-background/95">
                <div className="container mx-auto p-8 max-w-7xl">
                    <motion.div
                        key={location.pathname}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.4, ease: "easeOut" }}
                    >
                        {children}
                    </motion.div>
                </div>
            </main>
        </div>
    );
};

export default AppLayout;
