import { AlertCircle } from "lucide-react";

interface PlaceholderMessageProps {
  title: string;
  description: string;
}

const PlaceholderMessage: React.FC<PlaceholderMessageProps> = ({
  title,
  description,
}) => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center p-4">
      <AlertCircle className="w-12 h-12 text-gray-400 mb-4" />
      <h2 className="text-2xl font-semibold text-gray-700 mb-2">{title}</h2>
      <p className="text-gray-500">{description}</p>
    </div>
  );
};

export default PlaceholderMessage;
