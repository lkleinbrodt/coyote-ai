import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuIndicator,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  NavigationMenuViewport,
} from "@/components/ui/navigation-menu";

import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ModeToggle } from "@/components/DarkModeToggle";
import { useAuth } from "@/contexts/AuthContext";

export default function NavBar() {
  const { user, logout } = useAuth();

  return (
    <NavigationMenu className="navbar w-full">
      <NavigationMenuList className="w-full flex justify-between">
        <NavigationMenuItem>
          <Link to="/" className="brand-title text-xl">
            Coyote-AI
          </Link>
        </NavigationMenuItem>

        {/* Right side - Controls */}
        <div className="flex items-center gap-2">
          {user ? (
            <Button onClick={logout} variant="ghost">
              Logout
            </Button>
          ) : (
            <Button variant="ghost">
              <Link to="/login">Login</Link>
            </Button>
          )}
          <ModeToggle />
        </div>
      </NavigationMenuList>
    </NavigationMenu>
  );
}
