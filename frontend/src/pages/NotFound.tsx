import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <div className="text-center mt-5">
      <h1>404: Page Not Found</h1>
      <p>The page you're looking for doesn't exist.</p>
      <Link to="/" className="btn btn-primary">
        Go Home
      </Link>
    </div>
  );
}

export default NotFound; 