from flask import jsonify
import logging
from .exceptions import APIException
from werkzeug.exceptions import BadRequest, MethodNotAllowed, Unauthorized
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import traceback


def register_error_handlers(app):

    @app.errorhandler(APIException)
    def handle_api_exception(error):
        logging.error(f"API Error: {error.message}")
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(Unauthorized)
    def handle_unauthorized(error):
        logging.warning(f"Unauthorized Access - Detail: {str(error)}")
        return jsonify({"error": "Không xác thực được, vui lòng đăng nhập lại"}), 401
    
    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        logging.warning(f"Bad Request - Detail: {str(error)}")
        return jsonify({"error": "Yêu cầu không hợp lệ, kiểm tra dữ liệu đầu vào"}), 400
    
    @app.errorhandler(MethodNotAllowed)
    def handle_method_not_allowed(error):
        logging.warning(f"Method Not Allowed - Detail: {str(error)}")
        return jsonify({"error": "Phương thức không được phép"}), 405
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        logging.error(f"Database Integrity Error - Detail: {str(error)} | Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Lỗi dữ liệu, vi phạm ràng buộc cơ sở dữ liệu"}), 400
    
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(error):
        logging.error(f"Database Error - Detail: {str(error)} | Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Lỗi hệ thống khi truy cập cơ sở dữ liệu"}), 500

    @app.errorhandler(404)
    def not_found_error(error):
        logging.warning("Not Found API")
        return jsonify({"error": "Không tìm thấy API"}), 404

    @app.errorhandler(Exception)
    def handle_general_exception(error):
        logging.critical(f"Unexpected Server Error - Detail: {str(error)} | Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Lỗi hệ thống, vui lòng thử lại sau"}), 500
    
    @app.errorhandler(500)
    def handle_internal_server_error(error):
        logging.critical(f"Internal Server Error - Detail: {str(error)} | Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Lỗi hệ thống, vui lòng thử lại sau"}), 500