class APIException(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class BadRequestException(APIException):
    def __init__(self, message="Yêu cầu không hợp lệ"):
        super().__init__(message, 400)
class BadRequest(APIException):
    def __init__(self, message="Request not invalid"):
        super().__init__(message, 400)

class UnauthorizedException(APIException):
    def __init__(self, message="Không có quyền truy cập"):
        super().__init__(message, 401)

class ForbiddenException(APIException):
    def __init__(self, message="Bạn không có quyền thực hiện thao tác này"):
        super().__init__(message, 403)

class NotFoundException(APIException):
    def __init__(self, message="Không tìm thấy tài nguyên"):
        super().__init__(message, 404)

class IntegrityErrorException(APIException):
    def __init__(self, message="Lỗi dữ liệu, vui lòng kiểm tra lại"):
        super().__init__(message, 400)

class DatabaseException(APIException):
    def __init__(self, message="Lỗi hệ thống, vui lòng thử lại sau"):
        super().__init__(message, 500)

class ServerException(APIException):
    def __init__(self, message="Lỗi server"):
        super().__init__(message, 500)