import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { Badge } from "@/components/ui/badge";
import React from "react";
import { motion } from "framer-motion";

interface ProductCardProps {
  title: string;
  description: string;
  icon: string | React.ComponentType<{ className?: string }>;
  link: string;
  category?: string;
  featured?: boolean;
  softwareType?: string;
}

const ProductCard: React.FC<ProductCardProps> = ({
  title,
  description,
  icon,
  link,
  category,
  featured,
  softwareType,
}) => {
  const renderIcon = () => {
    return (
      <motion.div
        whileHover={{ scale: 1.1 }}
        transition={{ type: "spring", stiffness: 300 }}
        className="w-24 h-24 flex items-center justify-center mx-auto mb-4"
      >
        {typeof icon === "string" ? (
          <img src={icon} alt={title} className="w-24 h-24 object-contain" />
        ) : (
          React.createElement(icon, {
            className: "w-24 h-24 text-primary",
          })
        )}
      </motion.div>
    );
  };

  const getBadgeStyle = (type: string) => {
    switch (type.toLowerCase()) {
      case "mobile":
        return "bg-blue-500/20 text-blue-700 border-blue-300/50 hover:bg-blue-500/30 dark:text-blue-300 dark:border-blue-500/50";
      case "web":
        return "bg-purple-500/20 text-purple-700 border-purple-300/50 hover:bg-purple-500/30 dark:text-purple-300 dark:border-purple-500/50";
      case "ide":
        return "bg-emerald-500/20 text-emerald-700 border-emerald-300/50 hover:bg-emerald-500/30 dark:text-emerald-300 dark:border-emerald-500/50";
      default:
        return "bg-slate-500/20 text-slate-700 border-slate-300/50 hover:bg-slate-500/30 dark:text-slate-300 dark:border-slate-500/50";
    }
  };

  return (
    <motion.div
      whileHover={{ y: -5 }}
      transition={{ type: "spring", stiffness: 300 }}
      className="h-full relative"
    >
      <Card
        className={`cursor-pointer shadow-lg hover:shadow-xl transition-all duration-300 bg-card/50 backdrop-blur-sm border border-border/50 hover:border-primary/50 h-full flex flex-col ${
          featured ? "ring-2 ring-primary" : ""
        }`}
        onClick={() => (window.location.href = link)}
      >
        {softwareType && (
          <div className="absolute top-3 right-3 z-10">
            <Badge
              variant="outline"
              className={`text-xs ${getBadgeStyle(softwareType)}`}
            >
              {softwareType}
            </Badge>
          </div>
        )}
        <CardHeader className="flex items-center justify-center pb-2 flex-shrink-0">
          {renderIcon()}
          {category && (
            <span className="text-xs font-medium text-primary/80 uppercase tracking-wider">
              {category}
            </span>
          )}
        </CardHeader>
        <CardContent className="text-center flex-1 flex flex-col justify-between">
          <div>
            <CardTitle className="text-2xl font-bold text-foreground mb-2">
              {title}
            </CardTitle>
            <CardDescription className="text-muted-foreground text-base text-left min-h-[4.5rem] flex items-start">
              {description}
            </CardDescription>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default ProductCard;

{
  /* <div className="product-card text-center h-100">
<a href={link} className="text-decoration-none">
  <img src={icon} alt={title} className="product-icon" />
  <h3 className="link-title fw-bold">{title}</h3>
  <p className="product-description">{description}</p>
</a>
</div> */
}
