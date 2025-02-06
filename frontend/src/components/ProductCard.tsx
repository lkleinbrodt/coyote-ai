import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import React from "react";

interface ProductCardProps {
  title: string;
  description: string;
  icon: string;
  link: string;
}

const ProductCard: React.FC<ProductCardProps> = ({
  title,
  description,
  icon,
  link,
}) => {
  const renderIcon = () => {
    return (
      <img
        src={icon}
        alt={title}
        className="img-fluid max-w-[200px] max-h-[200px] object-contain"
      />
    );
  };

  return (
    <Card
      className="cursor-pointer shadow-none hover:shadow-lg hover:scale-105 transition-all duration-200 bg-card border-0"
      onClick={() => (window.location.href = link)}
    >
      <CardHeader>{renderIcon()}</CardHeader>
      <CardContent>
        <CardTitle className="text-center text-3xl text-foreground mb-3">
          {title}
        </CardTitle>
        <CardDescription className="text-left text-muted-foreground text-xl">
          {description}
        </CardDescription>
      </CardContent>
    </Card>
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
