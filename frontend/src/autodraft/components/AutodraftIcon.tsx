interface AutodraftIconProps {
  className?: string;
  theme?: "light" | "dark";
}

export const AutodraftIcon = ({
  className = "h-4 w-4",
  theme = "light",
}: AutodraftIconProps) => {
  const iconPath =
    theme === "dark"
      ? "/icons/drafting-compass-dark.png"
      : "/icons/drafting-compass-light.png";

  return <img src={iconPath} className={className} alt="Autodraft logo" />;
};
