import { useState } from "react";
import { useNavigate } from "react-router-dom";


export default function Home() {
  const [screen, setScreen] = useState("home"); // "home", "signup", "login"

    if (screen === "signup") 
      return <Signup
              onBack={() => setScreen("home")}
              onSwitchToSignup={() => setScreen("signup")}
              onSwitchToLogin={() => setScreen("login")}
             />;
    if (screen === "login") 
      return <Login
              onBack={() => setScreen("home")}
              onSwitchToSignup={() => setScreen("signup")}
              onSwitchToLogin={() => setScreen("login")}
             />;


  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light">
      <div className="card p-5 shadow" style={{ maxWidth: '500px', width: '100%' }}>
        <h2 className="text-center mb-4">Chào mừng bạn đến với <span className="text-primary">SHOPACC</span></h2>
        <p className="text-center mb-4">Đăng ký hoặc đăng nhập để tạo tài khoản và bắt đầu mua bán ngay hôm nay!</p>
        <div className="d-flex justify-content-center">
          <button onClick={() => setScreen("signup")}>Đăng ký</button>
          <button onClick={() => setScreen("login")}>Đăng nhập</button>
        </div>
      </div>
    </div>
  );
  console.log("SCREEN =", screen);

}

function Signup({ onBack, onSwitchToSignup, onSwitchToLogin}) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(""); // Thêm state để lưu lỗi

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); // Reset lỗi trước khi gọi API

    try {
        const response = await fetch('http://127.0.0.1:5000/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            setError('Đăng ký thành công! Vui lòng đăng nhập.');
            setTimeout(() => {
              if (onSwitchToLogin) onSwitchToLogin(); // gọi callback để chuyển sang form login
            }, 2000);
        } else {
            console.error('Response status:', response.status); // thêm dòng này
            console.error('Response data:', data); // thêm dòng này
            setError(data.msg || data.message || 'Đăng ký thất bại');
        }
    } catch (error) {
        console.error('Error:', error);
        setError('Không thể kết nối tới server. Có thể server bị lỗi hoặc bạn đang offline.');
    }

    console.log("Signup", { username, password });
  };

  return (
    <div className="card p-4 shadow bg-white" style={{ maxWidth: "400px", margin: "0 auto" }}>
      <h2 className="text-center mb-4">Tạo tài khoản mới</h2>

      {error && (
        <div className="alert alert-warning py-2 text-center" role="alert">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <input
            type="text"
            className="form-control"
            placeholder="Tên đăng nhập"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        <div className="mb-3">
          <input
            type="password"
            className="form-control"
            placeholder="Nhập mật khẩu"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div className="mb-3">
          <input
            type="password"
            className="form-control"
            placeholder="Nhập mật khẩu"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button type="submit" className="btn btn btn-success w-100" >
          Đăng Ký
        </button>

        </form> &nbsp;
      <button className="btn btn-primary" onClick={onSwitchToLogin}>
          Đăng nhập
      </button>
        <br />
      <button className="btn btn-sm btn-outline-secondary mt-2" onClick={onBack}>
          ← Quay lại Trang chính
      </button>
      </div>
  );
}

function Login({ onBack, onSwitchToSignup ,onSwitchToLogin}) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(""); // Thêm state để lưu lỗi

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
            setTimeout(() => {
              if (onSwitchToLogin) onBack(); // gọi callback để chuyển sang form login
            }, 2000);
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
    <div className="card p-4 shadow bg-white" style={{ maxWidth: "400px", margin: "0 auto" }}>
      <h2 className="text-center mb-4">Tạo tài khoản mới</h2>

        {error && (
          <div className="alert alert-warning py-2 text-center" role="alert">
            {error}
          </div>
        )}
      
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Tên đăng nhập</label>
            <input
              type="text"
              className="form-control"
              placeholder="Nhập username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="mb-3">
            <label className="form-label">Mật khẩu</label>
            <input
              type="password"
              className="form-control"
              placeholder="Nhập mật khẩu"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
        <button type="submit" className="btn btn-primary w-100" >
          Đăng Nhập
        </button>

        </form> &nbsp;
      <button className="btn btn-success" onClick={onSwitchToSignup}>
          Đăng Ký
      </button>
        <br />
      <button className="btn btn-sm btn-outline-secondary mt-2" onClick={onBack}>
          ← Quay lại Trang chính
      </button>
      </div>
  );
}