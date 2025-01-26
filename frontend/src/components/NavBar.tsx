import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Link, useLocation } from "react-router-dom";
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuList,
} from "@/components/ui/navigation-menu";

import { Button } from "@/components/ui/button";
import { ChevronDownIcon } from "@radix-ui/react-icons";
import { ModeToggle } from "@/components/DarkModeToggle";
import { useAuth } from "@/contexts/AuthContext";

export default function NavBar() {
  const { user, logout, login } = useAuth();
  const location = useLocation();
  return (
    <div className="w-full top-0 z-1 flex flex-row justify-between items-center bg-secondary-foreground opacity-90">
      <NavigationMenu>
        <NavigationMenuList className="h-full flex items-center">
          <NavigationMenuItem>
            <Link to="/">
              <img
                src="icons/coyote_logo.png"
                alt="logo"
                className="w-10 h-10"
              />
            </Link>
          </NavigationMenuItem>
        </NavigationMenuList>
      </NavigationMenu>

      <NavigationMenu>
        <NavigationMenuList>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline">
                <ChevronDownIcon className="w-4 h-4 text-foreground" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56">
              <DropdownMenuLabel className="flex flex-row justify-between items-center">
                {user ? user.name : "Guest"}
                <ModeToggle />
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              {user ? (
                <DropdownMenuItem onClick={logout}>Logout</DropdownMenuItem>
              ) : (
                <DropdownMenuItem onClick={() => login(location.pathname)}>
                  Login
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
            </DropdownMenuContent>
          </DropdownMenu>
        </NavigationMenuList>
      </NavigationMenu>
    </div>
  );
}
