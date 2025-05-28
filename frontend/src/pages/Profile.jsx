import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
//import { handlerLogout } from './Home.jsx';

export default function Profile() {
    const navigate = useNavigate();
    const [userData, setUserData] = useState(null);
    const [error, setError] = useState(null);
    const [tokenExpired, setTokenExpired] = useState(false);

    const token = localStorage.getItem('token');
    const [role, setRole] = useState(false);

    const [showForm, setShowForm] = useState(false);
    const [showForm_create, setShowForm_create] = useState('');
    const [coin, setCoin] = useState('');
    const [confirmMessage, setConfirmMessage] = useState('');
    
    const [id, setId] = useState('');
    const [hero, setHero] = useState('');
    const [skin, setSkin] = useState('');
    const [price, setPrice] = useState('');
    const [description, setDescription] = useState('');
    const [rank, setRank] = useState('');

    const handleLogout = () => {
        
        localStorage.removeItem("isLoggedIn");
        localStorage.removeItem("token");
        
        navigate("/")
        console.log("Logout completed, isLoggedIn:", false);
    };

  // Kiểm tra token khi vào 
    useEffect(() => {
        if (!token) {
        navigate('/'); // Nếu không có token, chuyển về trang login
        }else { //Kiểm tra role
        fetch("http://127.0.0.1:5000/acc/check", {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
          .then(res => {
            if (res.status === 200) {
              setRole(true) // Role
              console.log("Status code:", res.status);
              // console.error('Response status:', res.status); // thêm dòng này
              // console.error('Response data:', data); // thêm dòng này
            }
          });
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
    }, []);

    if (tokenExpired) {
        localStorage.removeItem("token");
        return (
            <div>
                
                <p>Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại.</p>
                <button onClick={() => navigate("/")}>Đăng nhập</button>
                
            </div>
        );
    }
  // Nạp coin
  const handleChargeCoin = async (e) => {
    e.preventDefault();
    setError(""); // Reset lỗi trước khi gọi API
    try {

      const response = await fetch('http://127.0.0.1:5000/auth/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`, // nếu có token
        },
        body: JSON.stringify({ coin }),
      });
      const data = await response.json();

      if (response.ok) {
          console.log("Status code:", response.status);
          setUserData(prev => ({
            ...prev,
            coin: data.coin || (Number(prev.coin) + Number(coin))
          }));

        } else {
            console.error('Response status:', response.status); // thêm dòng này
            console.error('Response data:', data); // thêm dòng này
            setError(data.msg || data.message || 'Đăng nhập thất bại');
        }
    } catch (error) {
        console.error('Error:', error);
        setError('Không thể kết nối tới server. Có thể server bị lỗi hoặc bạn đang offline.');
    }
      setConfirmMessage(`Đã nhận được ${coin} coin`);
      // Tự động ẩn message sau 5 giây
      setTimeout(() => {
        setConfirmMessage("");
      }, 5000);
      setShowForm(false); // Ẩn form sau khi submit
      setCoin('');
  };
  // create nick
  const create_nick = async (e) => {
    e.preventDefault();
    setError(""); // Reset lỗi trước khi gọi API
    try {

      const response = await fetch('http://127.0.0.1:5000/acc/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`, // nếu có token
        },
        body: JSON.stringify({ hero, skin, price, description }),
      });
      const data = await response.json();

      if (response.ok) {
          console.log("Status code:", response.status);
          setUserData(data)
          setConfirmMessage(`Nick ${data.id || 'mới'} created`);
          setTimeout(() => {
            setConfirmMessage("");
          }, 5000);
          setShowForm_create(false); // Ẩn form sau khi submit

        } else {
            console.error('Response status:', response.status); // thêm dòng này
            console.error('Response data:', data); // thêm dòng này
            setError(data.msg || data.message || 'Đăng nhập thất bại');
        }
    } catch (error) {
        console.error('Error:', error);
        setError('Không thể kết nối tới server. Có thể server bị lỗi hoặc bạn đang offline.');
    }

  };
  // Return origin
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
            {token && (   // Kiểm tra đăng nhập
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
              ) }  
          </div>
        </div>
      </div>
    </nav>

    <div>
{userData ? (
  <>
    <h2>Xin chào, {userData.username}</h2>
    <p>Số coin hiện có: {userData.coin}</p>

    {/* Nút hiển thị form */}
    {!showForm ? (
      <button
        className="btn btn-outline-dark"
        onClick={() => setShowForm(true)}
      >
        <i className="bi me-1"></i> Nạp coin
      </button>
    ) : (
      // Form nhập số coin
      <form onSubmit={handleChargeCoin} >
        <div className="mb-3">

          <label htmlFor="coinInput" className="form-label">Nhập số coin muốn nạp</label>
          <input
            type="text"
            value={coin}
            onChange={(e) => setCoin(e.target.value)}

          />
        </div>
        <button type="submit" className="btn btn-success me-2">Xác nhận</button>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => setShowForm(false)}
        >
          Hủy
        </button>
      </form>
    )}
    
    {/* Thông báo sau khi submit */}
    {confirmMessage && (
      <div className="alert alert-info mt-3">
        {confirmMessage}
      </div>
    )}
  </>
  ) : (
    <p>Đang tải dữ liệu...</p>
  )}
    </div>

    {role && (
      !showForm_create? (

      <button
        className="btn btn-outline-dark" 
        onClick={() => setShowForm_create(true)}
        >
        <i className="bi me-1"></i> Thêm acc
      </button>
    ) : (
      // Form nhập số coin
      <form onSubmit={create_nick} >
        <div className="mb-3">

          <label htmlFor="coinInput" className="form-label">Nhập thông tin tài khoản</label>
          <br />
          <label htmlFor="coinInput" className="form-label">Số lượng tướng</label>
          <input
            type="text"
            value={hero}
            onChange={(e) => setHero(e.target.value)}
          /><br />
          <label htmlFor="coinInput" className="form-label">Số skin</label>
          <input
            type="text"
            value={skin}
            onChange={(e) => setSkin(e.target.value)}
          /><br />
          <label htmlFor="coinInput" className="form-label">Giá trị</label>
          <input
            type="text"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
          /><br />
          <label htmlFor="coinInput" className="form-label">Mô tả </label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          /><br />
          <label htmlFor="coinInput" className="form-label">Rank</label>
          <input
            type="text"
            value={rank}
            onChange={(e) => setRank(e.target.value)}
          />

        </div>
        <button type="submit" className="btn btn-success me-2">Xác nhận</button>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={() => setShowForm_create(false)}
        >
          Hủy
        </button>
      </form>
      )
    )}


    {/* Footer */}
    <footer className="py-5 bg-dark">
      <div className="container">
        <p className="m-0 text-center text-white">Copyright &copy; ShopACC 2025</p>
      </div>
    </footer>
    </div>
    
  );
}