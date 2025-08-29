-- Xóa bảng nếu đã tồn tại
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS users;

-- Tạo bảng users
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Tạo bảng tasks, liên kết với users
CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    category VARCHAR(100),   -- Phân loại công việc (Học tập, Cá nhân, Việc nhà, ...)
    label VARCHAR(100),      -- Nhãn (Gấp, Quan trọng, Bình thường, ...)
    status VARCHAR(50) DEFAULT 'Chưa hoàn thành',
    user_id INT NOT NULL,    -- Liên kết với người dùng
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
