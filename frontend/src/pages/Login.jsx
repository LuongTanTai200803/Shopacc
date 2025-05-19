import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(""); // Thêm state để lưu lỗi
  const navigate = useNavigate(); // Sử dụng useNavigate để chuyển hướng

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); // Reset lỗi trước khi gọi API

    try {
        const response = await fetch('http://127.0.0.1:5000/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            // Kiểm tra token trước khi lưu
            localStorage.setItem('token', data.access_token); // lưu token
            navigate('/dashboard'); // Chuyển hướng mà không reload trang
        } else {
            console.error('Response status:', response.status); // thêm dòng này
            console.error('Response data:', data); // thêm dòng này
            setError(data.msg || data.message || 'Đăng nhập thất bại');
        }
    } catch (error) {
        console.error('Error:', error);
        setError('Không thể kết nối tới server. Có thể server bị lỗi hoặc bạn đang offline.');
    }

    console.log("Login", { username, password });
  };

  return (
    <div>
      <h2>Đăng nhập</h2>
      <p>Đây là trang đăng nhập của bạn!</p>
      {error && <p style={{ color: 'red' }}>{error}</p>} {/* Hiển thị lỗi trên giao diện */}
      <form onSubmit={handleSubmit}>
        <p>Tên đăng nhập</p>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <p>Mật khẩu</p>
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">Đăng nhập</button>
      </form>
    </div>
  );
}

