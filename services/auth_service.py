# services/auth_service.py
import hashlib
from sqlalchemy.orm import Session
from database.db_connection import SessionLocal
from models.user import User

class AuthService:
    def __init__(self):
        pass

    def hash_password(self, password: str) -> str:
        """
        Hash password using SHA-256.
        Note: For production, use bcrypt or argon2. Using SHA-256 for simplicity.
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify if password matches the hash."""
        return self.hash_password(password) == password_hash

    def authenticate(self, username: str, password: str):
        """
        Authenticate user by username and password.
        Returns (success, user_or_message)
        """
        session: Session = SessionLocal()
        try:
            user = session.query(User).filter(User.username == username).first()
            
            if not user:
                return False, "Tên đăng nhập không tồn tại"
            
            if not self.verify_password(password, user.password_hash):
                return False, "Mật khẩu không đúng"
            
            # Return user data as dict to avoid session issues
            user_data = {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'role': user.role,
                'is_admin': user.is_admin()
            }
            return True, user_data
            
        except Exception as e:
            return False, f"Lỗi đăng nhập: {str(e)}"
        finally:
            session.close()

    def create_user(self, data: dict):
        """
        Create a new user.
        :param data: Dictionary containing user details
        """
        session: Session = SessionLocal()
        try:
            # Check if username already exists
            existing = session.query(User).filter(User.username == data.get('username')).first()
            if existing:
                return False, "Tên đăng nhập đã tồn tại"
            
            new_user = User(
                username=data.get('username'),
                password_hash=self.hash_password(data.get('password')),
                full_name=data.get('full_name', ''),
                role=data.get('role', 'staff')
            )
            session.add(new_user)
            session.commit()
            return True, "Tạo tài khoản thành công"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi tạo tài khoản: {str(e)}"
        finally:
            session.close()

    def get_all_users(self):
        """Retrieve all users from the database."""
        session: Session = SessionLocal()
        try:
            users = session.query(User).all()
            return users
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
        finally:
            session.close()

    def delete_user(self, user_id: int):
        """Delete a user by ID."""
        session: Session = SessionLocal()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                if user.role == 'admin':
                    # Check if this is the last admin
                    admin_count = session.query(User).filter(User.role == 'admin').count()
                    if admin_count <= 1:
                        return False, "Không thể xoá admin cuối cùng"
                
                username = user.username
                session.delete(user)
                session.commit()
                return True, f"Đã xoá tài khoản '{username}'"
            else:
                return False, "Không tìm thấy tài khoản"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def create_default_admin(self):
        """Create default admin account if no admin exists."""
        session: Session = SessionLocal()
        try:
            admin_exists = session.query(User).filter(User.role == 'admin').first()
            if not admin_exists:
                default_admin = User(
                    username='admin',
                    password_hash=self.hash_password('admin123'),
                    full_name='Administrator',
                    role='admin'
                )
                session.add(default_admin)
                session.commit()
                print("Default admin account created: admin / admin123")
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error creating default admin: {e}")
            return False
        finally:
            session.close()
