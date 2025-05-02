import { Link, useLocation } from "react-router-dom";
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuList,
} from "@/components/ui/navigation-menu";

import { Button } from "@/components/ui/button";
import UserItem from "@/autodraft/components/UserItem";
// import { ModeToggle } from "@/components/DarkModeToggle";
import { useAuth } from "@/contexts/AuthContext";

const getPageTitle = (pathname: string) => {
  switch (pathname) {
    case "/poeltl":
      return "PoeltlChat";
    case "/autodraft":
      return "AutoDraft";
    case "/boids":
      return "Boids";
    case "/games":
      return "Games";
    case "/games/gravity-quest":
      return "Gravity Quest";
    case "/games/shoot-the-creeps":
      return "Shoot The Creeps";
    case "/explain":
      return "Explain Like I'm ___";
    default:
      return "Landon Kleinbrodt";
  }
};

export default function NavBar() {
  const { user, login } = useAuth();
  const location = useLocation();
  const pageTitle = getPageTitle(location.pathname);

  return (
    <div className="flex fixed flex-row justify-between items-center bg-secondary-foreground h-[var(--navbar-height)] px-4 w-full z-[1000]">
      <NavigationMenu className="mx-0 my-0">
        <NavigationMenuList className="m-0 p-0">
          <NavigationMenuItem>
            <div className="flex items-center gap-4">
              <Link to="/" className="flex items-center gap-4">
                <img
                  src="/icons/coyote_logo.png"
                  alt="logo"
                  className="w-10 h-10"
                />
              </Link>
              {pageTitle && (
                <span className="text-xl font-semibold text-background cursor-default">
                  {pageTitle}
                </span>
              )}
            </div>
          </NavigationMenuItem>
        </NavigationMenuList>
      </NavigationMenu>

      <NavigationMenu className="mx-0 my-0">
        <NavigationMenuList className="m-0 p-0">
          {user ? (
            <UserItem />
          ) : (
            <Button
              variant="outline"
              className="bg-transparent text-background hover:text-background"
              onClick={() => login(location.pathname)}
            >
              Login
            </Button>
          )}
        </NavigationMenuList>
      </NavigationMenu>
    </div>
  );
}
