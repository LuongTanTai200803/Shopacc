import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
//import { handlerLogout } from './Home.jsx';

export default function Profile() {
    const navigate = useNavigate();
    const [userData, setUserData] = useState(null);
    const [error, setError] = useState(null);
    const [tokenExpired, setTokenExpired] = useState(false);

    const token = localStorage.getItem('token');

    const handleLogout = () => {
        setIsLoggedIn(false);
        localStorage.removeItem("isLoggedIn");
        localStorage.removeItem("token");
        setScreen("/home");
        console.log("Logout completed, isLoggedIn:", false);
    };

  // Kiểm tra token khi vào 
    useEffect(() => {
        if (!token) {
        navigate('/'); // Nếu không có token, chuyển về trang login
        return;
    }
    // Hiển thị thông tin user
    const fetchData = async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/auth/profile', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok) {
                setUserData(data);// Lưu vào state
                setTokenExpired(false);
            } else {
                if (data.msg === 'Token has expired') {
                    setTokenExpired(true);
                } else {
                    console.error('Response status:', response.status); // thêm dòng này
                    console.error('Response data:', data); // thêm dòng này
                    setError(data.msg || data.message || 'Lỗi dữ liệu');
                }
            }
        } catch (error) {
            console.error('Error:', error);
            setError('Không thể kết nối tới server. Có thể server bị lỗi hoặc bạn đang offline.');
        }
    };

        fetchData();
    }, [navigate, token]);

    if (tokenExpired) {
        localStorage.removeItem("token");
        return (
            <div>
                
                <p>Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại.</p>
                <button onClick={() => navigate("/")}>Đăng nhập</button>
                
            </div>
        );
    }

  return (
    <div>
      <nav className="navbar navbar-expand-lg navbar-light bg-light">
      <div className="container px-4 px-lg-5">
        <a className="navbar-brand" href="/">ShopACC uy tín chất lượng</a>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse"
                data-bs-target="#navbarSupportedContent"
                aria-controls="navbarSupportedContent" aria-expanded="false"
                aria-label="Toggle navigation">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarSupportedContent">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0 ms-lg-4">
            <li className="nav-item"><a className="nav-link active" href="/">Trang chủ</a></li>
            <li className="nav-item"><a className="nav-link" href="#">Giới thiệu</a></li>
          </ul>
          <div className="d-flex"> 
            {token ? (   // Kiểm tra đăng nhập
                <>
                  <button
                    className="btn btn-outline-dark me-2"
                    onClick={() => navigate("/profile")} // Điều hướng đến trang hồ sơ
                  >
                    <i className="bi bi-person me-1"></i> Hồ sơ
                  </button>
                  <button
                    className="btn btn-outline-dark"
                    onClick={handleLogout} // Đăng xuất
                  >
                    <i className="bi bi-box-arrow-right me-1"></i> Đăng xuất
                  </button>
                </>
              ) : (
              <>
                <button className="btn btn-outline-dark me-2" onClick={() => setScreen("signup")}>
                  <i className="bi bi-person-plus me-1"></i> Đăng ký
                </button>
                <button className="btn btn-outline-dark" onClick={() => setScreen("login")}>
                  <i className="bi bi-box-arrow-in-right me-1"></i> Đăng nhập
                </button>
              </>
          )}  
          </div>
        </div>
      </div>
    </nav>

    <div>
      {userData ? (
        <>
          <h2>Xin chào, {userData.username}</h2>
          <p>Số coin hiện có: {userData.coin}</p>
        </>
      ) : (
        <p>Đang tải dữ liệu...</p>
      )}
    </div>

    {/* Footer */}
    <footer className="py-5 bg-dark">
      <div className="container">
        <p className="m-0 text-center text-white">Copyright &copy; ShopACC 2025</p>
      </div>
    </footer>
    </div>
    
  );
}