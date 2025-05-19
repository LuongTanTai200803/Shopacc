import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const navigate = useNavigate();

  // Kiểm tra token khi vào dashboard
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login'); // Nếu không có token, chuyển về trang login
    }
  }, [navigate]);

  return (
    <div>
      <h2>Dashboard</h2>
      <p>Chào mừng bạn đến với Dashboard!</p>
    </div>
  );
}