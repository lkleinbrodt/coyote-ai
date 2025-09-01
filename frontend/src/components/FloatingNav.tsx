import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { Button } from "@/components/ui/button";
import UserItem from "@/autodraft/components/UserItem";
import { useAuth } from "@/contexts/AuthContext";
import { useState } from "react";

export default function FloatingNav() {
  const { user, login } = useAuth();
  // const pageTitle = getPageTitle(location.pathname);
  const [isOpen, setIsOpen] = useState(false);

  const handleLogin = () => {
    setIsOpen(false);
    login();
  };

  return (
    <div className="fixed top-4 left-4 z-50">
      <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
        <DropdownMenuTrigger asChild>
          <Button
            variant="outline"
            size="icon"
            className="h-12 w-12 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 bg-background/80 backdrop-blur-sm border-2"
          >
            <img
              src="/icons/coyote_logo.png"
              alt="logo"
              className="w-10 h-10"
            />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent
          align="start"
          className="w-auto min-w-64 max-w-80 p-2"
          sideOffset={8}
        >
          <div className="p-2">
            {user ? (
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <UserItem />
                </div>
              </div>
            ) : (
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={handleLogin}
              >
                Login
              </Button>
            )}
          </div>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
