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
  return (
    <Card
      className="cursor-pointer hover:shadow-lg hover:scale-105 transition-all duration-200"
      onClick={() => (window.location.href = link)}
    >
      <CardHeader>
        <img
          src={icon}
          alt={title}
          style={{
            width: "100px",
            height: "100px",
            display: "block",
            margin: "0 auto",
          }}
        />
      </CardHeader>
      <CardContent>
        <CardTitle className="text-center h3">{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
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
