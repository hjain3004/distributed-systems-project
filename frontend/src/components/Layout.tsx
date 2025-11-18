/**
 * Layout Component with Navigation Drawer
 */

import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
} from '@mui/material';
import {
  Home,
  CompareArrows,
  Calculate,
  Science,
  Analytics,
  Assessment,
  AccountTree,
  Menu as MenuIcon,
} from '@mui/icons-material';
import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const drawerWidth = 280;

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = [
    { text: 'Dashboard', icon: <Home />, path: '/' },
    { text: 'M/G/N vs M/M/N', icon: <CompareArrows />, path: '/comparison' },
    { text: 'M/M/N Calculator', icon: <Calculate />, path: '/mmn' },
    { text: 'M/G/N Calculator', icon: <Science />, path: '/mgn' },
    { text: 'Tandem Queue', icon: <AccountTree />, path: '/tandem' },
    { text: '15 Equations', icon: <Analytics />, path: '/equations' },
    { text: 'Results Viewer', icon: <Assessment />, path: '/results' },
  ];

  const drawer = (
    <div>
      <Toolbar sx={{ backgroundColor: 'primary.main', color: 'white' }}>
        <Typography variant="h6" noWrap component="div" fontWeight="bold">
          Queue Modeling
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component={Link}
              to={item.path}
              selected={location.pathname === item.path}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'primary.light',
                  '&:hover': {
                    backgroundColor: 'primary.light',
                  },
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: location.pathname === item.path ? 'primary.main' : 'inherit',
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <Box sx={{ p: 2, backgroundColor: 'background.default' }}>
        <Typography variant="caption" color="text.secondary">
          Based on Li et al. (2015)
        </Typography>
        <br />
        <Typography variant="caption" color="text.secondary">
          15 Analytical Equations
        </Typography>
        <br />
        <Typography variant="caption" color="text.secondary">
          Heavy-Tailed Distributions
        </Typography>
      </Box>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            Distributed Systems Performance Modeling
          </Typography>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better mobile performance
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>
        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          backgroundColor: 'background.default',
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};
