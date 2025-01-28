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
// import { ModeToggle } from "@/components/DarkModeToggle";
import { useAuth } from "@/contexts/AuthContext";

const getPageTitle = (pathname: string) => {
  switch (pathname) {
    case "/poeltl":
      return "PoeltlGPT";
    case "/autodraft":
      return "Autodraft";
    default:
      return "Coyote-AI";
  }
};

export default function NavBar() {
  const { user, logout, login } = useAuth();
  const location = useLocation();
  const pageTitle = getPageTitle(location.pathname);

  return (
    <div className="flex fixed flex-row justify-between items-center bg-secondary-foreground h-16 px-4 w-full z-1000">
      <NavigationMenu className="mx-0 my-0">
        <NavigationMenuList className="m-0 p-0">
          <NavigationMenuItem>
            <div className="flex items-center gap-4">
              <Link to="/" className="flex items-center gap-4">
                <img
                  src="icons/coyote_logo.png"
                  alt="logo"
                  className="w-10 h-10"
                />
              </Link>
              {pageTitle && (
                <span className="text-xl font-semibold text-background">
                  {pageTitle}
                </span>
              )}
            </div>
          </NavigationMenuItem>
        </NavigationMenuList>
      </NavigationMenu>

      <NavigationMenu className="mx-0 my-0">
        <NavigationMenuList className="m-0 p-0">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="icon" className="bg-transparent">
                <ChevronDownIcon className="w-4 h-4 text-background" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-60">
              <DropdownMenuLabel className="flex flex-row justify-between items-center">
                {user ? user.name : "Guest"}
                {/* <ModeToggle /> */}
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
