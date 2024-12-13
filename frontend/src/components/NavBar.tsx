import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuList,
} from "@/components/ui/navigation-menu";

import { Button } from "@/components/ui/button";
import { ChevronDownIcon } from "@radix-ui/react-icons";
import { Link } from "react-router-dom";
import { ModeToggle } from "@/components/DarkModeToggle";
import { useAuth } from "@/contexts/AuthContext";

export default function NavBar() {
  const { user, logout } = useAuth();

  return (
    <div className="w-full fixed top-0 z-1 flex flex-row justify-between items-center">
      {/* these buttons go on the left */}
      <NavigationMenu>
        <NavigationMenuList>
          <NavigationMenuItem>
            <Link to="/" className="text-foreground">
              <img
                src="icons/coyote_logo.png"
                alt="logo"
                className="w-10 h-10"
              />
            </Link>
          </NavigationMenuItem>
        </NavigationMenuList>
      </NavigationMenu>

      {/* these buttons go on the right */}
      <NavigationMenu className="p-4">
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
                <DropdownMenuItem>
                  <Link
                    to="/login"
                    className="text-foreground text-decoration-none"
                  >
                    Login
                  </Link>
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
