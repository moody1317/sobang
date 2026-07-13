import { Navigate } from 'react-router-dom';
import { isLoggedIn } from '../../../api/auth';

function PatrolProtectedRoute({ children }) {
  if (!isLoggedIn()) {
    return <Navigate to="/firefighter_patrol/login" replace />;
  }
  return children;
}

export default PatrolProtectedRoute;
