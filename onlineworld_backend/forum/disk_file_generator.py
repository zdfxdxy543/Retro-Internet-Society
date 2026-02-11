import os
import uuid
import random
import string
from datetime import datetime
from .models import OnlineDiskShare, db
from sqlalchemy.exc import SQLAlchemyError

class DiskFileGenerator:
    """
    网盘文件生成器
    用于生成本地文件并保存到网盘中，同时在数据库中注册分享记录
    """
    def __init__(self, db, app_config):
        """
        初始化方法
        :param db: SQLAlchemy数据库实例
        :param app_config: 应用配置
        """
        self.db = db
        self.app_config = app_config
        
        # 网盘文件存储路径
        self.disk_storage_path = app_config.get(
            "DISK_STORAGE_PATH", 
            os.path.join("static", "files", "online_disk")
        )
        
        # 确保存储目录存在
        os.makedirs(self.disk_storage_path, exist_ok=True)
        
        # 分享号和密码的配置
        self.share_id_length = app_config.get("SHARE_ID_LENGTH", 8)
        self.password_length = app_config.get("PASSWORD_LENGTH", 6)
    
    def _generate_random_string(self, length, use_letters=True, use_digits=True, use_symbols=False):
        """
        生成随机字符串（内部私有方法）
        :param length: 字符串长度
        :param use_letters: 是否包含字母
        :param use_digits: 是否包含数字
        :param use_symbols: 是否包含符号
        :return: 随机字符串
        """
        characters = ""
        if use_letters:
            characters += string.ascii_letters
        if use_digits:
            characters += string.digits
        if use_symbols:
            characters += string.punctuation
        
        if not characters:
            characters = string.ascii_letters + string.digits
        
        return ''.join(random.choice(characters) for _ in range(length))
    
    def _generate_unique_share_id(self):
        """
        生成唯一的分享号（内部私有方法）
        :return: 唯一的分享号字符串
        """
        while True:
            # 生成分享号（使用字母和数字）
            share_id = self._generate_random_string(
                self.share_id_length, 
                use_letters=True, 
                use_digits=True, 
                use_symbols=False
            )
            # 检查分享号是否已存在
            if not OnlineDiskShare.query.filter_by(share_id=share_id).first():
                return share_id
    
    def _generate_password(self):
        """
        生成随机密码（内部私有方法）
        :return: 随机密码字符串
        """
        return self._generate_random_string(
            self.password_length, 
            use_letters=False, 
            use_digits=True, 
            use_symbols=False
        )
    
    def _save_content_to_file(self, content, file_name, file_extension="txt"):
        """
        将内容保存到文件（内部私有方法）
        :param content: 要保存的内容
        :param file_name: 文件名（不带扩展名）
        :param file_extension: 文件扩展名
        :return: 保存的文件路径
        """
        # 构建完整的文件名
        full_file_name = f"{file_name}.{file_extension}"
        
        # 构建完整的文件路径
        file_path = os.path.join(self.disk_storage_path, full_file_name)
        
        # 保存内容到文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # 返回相对于应用根目录的文件路径，使用Web标准的正斜杠
        return "/" + "/".join(["static", "files", "online_disk", full_file_name])
    
    def generate_disk_file(self, content, file_name=None, file_extension="txt", password=None):
        """
        核心方法：生成网盘文件并在数据库中注册
        :param content: 文件内容
        :param file_name: 文件名（可选，不带扩展名）
        :param file_extension: 文件扩展名（默认txt）
        :param password: 密码（可选，不提供则自动生成）
        :return: 字典形式的分享信息（share_id, password, file_name等）
        :raises ValueError: 缺少必填参数或参数非法
        :raises SQLAlchemyError: 数据库存储异常
        :raises IOError: 文件保存异常
        """
        # 1. 校验必填参数
        if not content or not isinstance(content, str):
            raise ValueError("文件内容必填，且必须是字符串类型")
        
        # 2. 生成文件名（如果未提供）
        if not file_name:
            file_name = f"ai-generated-{str(uuid.uuid4())[:8]}"
        
        # 3. 生成唯一分享号
        share_id = self._generate_unique_share_id()
        
        # 4. 生成密码（如果未提供）
        if not password:
            password = self._generate_password()
        
        try:
            # 5. 保存内容到文件
            file_path = self._save_content_to_file(content, file_name, file_extension)
            
            # 6. 在数据库中注册分享记录
            share_record = OnlineDiskShare(
                share_id=share_id,
                password=password,  # 直接存储明文密码，根据需求无需加密
                file_path=file_path,
                file_name=f"{file_name}.{file_extension}"
            )
            
            self.db.session.add(share_record)
            self.db.session.commit()
            
            # 7. 返回分享信息
            return {
                "share_id": share_id,
                "password": password,
                "file_name": f"{file_name}.{file_extension}",
                "file_path": file_path,
                "create_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "message": "文件生成成功并已添加到网盘"
            }
        except IOError as e:
            raise IOError(f"文件保存失败：{str(e)}")
        except SQLAlchemyError as e:
            self.db.session.rollback()
            raise SQLAlchemyError(f"数据库注册失败：{str(e)}")
        except Exception as e:
            self.db.session.rollback()
            raise Exception(f"文件生成失败：{str(e)}")
    
    def generate_disk_file_from_dict(self, data_dict, file_name=None, file_extension="json"):
        """
        辅助方法：从字典生成JSON文件
        :param data_dict: 要保存的字典数据
        :param file_name: 文件名（可选，不带扩展名）
        :param file_extension: 文件扩展名（默认json）
        :return: 字典形式的分享信息
        """
        import json
        
        # 将字典转换为JSON字符串
        content = json.dumps(data_dict, ensure_ascii=False, indent=2)
        
        # 调用核心方法生成文件
        return self.generate_disk_file(content, file_name, file_extension)
    
    def generate_disk_file_from_list(self, data_list, file_name=None, file_extension="json"):
        """
        辅助方法：从列表生成JSON文件
        :param data_list: 要保存的列表数据
        :param file_name: 文件名（可选，不带扩展名）
        :param file_extension: 文件扩展名（默认json）
        :return: 字典形式的分享信息
        """
        import json
        
        # 将列表转换为JSON字符串
        content = json.dumps(data_list, ensure_ascii=False, indent=2)
        
        # 调用核心方法生成文件
        return self.generate_disk_file(content, file_name, file_extension)
    
    def get_share_info(self, share_id):
        """
        辅助方法：获取分享信息
        :param share_id: 分享号
        :return: 字典形式的分享信息，不存在则返回None
        """
        share = OnlineDiskShare.query.filter_by(share_id=share_id).first()
        if share:
            return {
                "share_id": share.share_id,
                "file_name": share.file_name,
                "create_time": share.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "download_count": share.download_count,
                "is_active": share.is_active
            }
        return None
    
    def deactivate_share(self, share_id):
        """
        辅助方法：停用分享
        :param share_id: 分享号
        :return: 是否停用成功
        """
        share = OnlineDiskShare.query.filter_by(share_id=share_id).first()
        if share:
            share.is_active = False
            self.db.session.commit()
            return True
        return False