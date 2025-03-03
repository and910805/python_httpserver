import os
import cgi
import platform
import shutil
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote, quote
from datetime import datetime

class EnhancedHandler(SimpleHTTPRequestHandler):
    FILE_ICONS = {
        'folder': '📁',
        'image': '🖼️',
        'pdf': '📄',
        'text': '📝',
        'code': '💻',
        'audio': '🎵',
        'video': '🎥',
        'archive': '📦',
        'default': '📄'
    }

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Python File Server</title>
                <style>
                    {self.get_css()}
                </style>
            </head>
            <body>
                <div class="container">
                    {self.get_header()}
                    {self.get_upload_section()}
                    {self.get_file_list()}
                </div>
                <script>
                    {self.get_js()}
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            super().do_GET()

    def get_header(self):
        return f"""
        <header>
            <h1>📁 Python File Server</h1>
            <div class="status-bar">
                <span>🕒 Server Time: {self.get_formatted_time()}</span>
                <span>💾 Disk Usage: {self.get_disk_usage()}</span>
                <span>By goole910805@gmail.com</span>
            </div>
        </header>
        """

    def get_upload_section(self):
        return """
        <div class="upload-section">
            <h2>⬆️ Upload File</h2>
            <form action="/upload" method="post" enctype="multipart/form-data" onsubmit="showLoading()">
                <div class="file-input">
                    <input type="file" name="file" id="file" required>
                    <label for="file">Choose file...</label>
                </div>
                <div class="upload-options">
                    <label>
                        <input type="checkbox" name="overwrite" id="overwrite">
                        Overwrite existing files
                    </label>
                </div>
                <button type="submit">Upload File</button>
            </form>
            <div id="loading" style="display:none">
                <div class="spinner"></div>
                <p>Uploading...</p>
            </div>
        </div>
        """

    def get_file_list(self):
        path = self.translate_path(self.path)
        if not os.path.isdir(path):
            return ""
        
        items = []
        for name in sorted(os.listdir(path)):
            full_path = os.path.join(path, name)
            is_dir = os.path.isdir(full_path)
            size = os.path.getsize(full_path) if not is_dir else '-'
            mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
            
            icon = self.get_file_icon(name, is_dir)
            encoded_name = quote(name)
            
            items.append(f"""
            <tr>
                <td>{icon}</td>
                <td><a href="{encoded_name}" title="{name}">{name}</a></td>
                <td>{self.format_size(size)}</td>
                <td>{mtime.strftime('%Y-%m-%d %H:%M:%S')}</td>
                <td>
                    <button onclick="deleteFile('{encoded_name}')" class="delete-btn">🗑️</button>
                </td>
            </tr>
            """)
        
        return f"""
        <div class="file-list">
            <h2>📂 Current Directory: {unquote(self.path)}</h2>
            <div class="search-box">
                <input type="text" id="search" placeholder="Search files..." oninput="filterFiles()">
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Name</th>
                        <th>Size</th>
                        <th>Last Modified</th>
                        <th>Action(Delete)</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(items)}
                </tbody>
            </table>
        </div>
        """

    def get_file_icon(self, filename, is_dir):
        if is_dir:
            return self.FILE_ICONS['folder']
        
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif']:
            return self.FILE_ICONS['image']
        elif ext in ['.pdf']:
            return self.FILE_ICONS['pdf']
        elif ext in ['.txt', '.md']:
            return self.FILE_ICONS['text']
        elif ext in ['.py', '.js', '.html', '.css']:
            return self.FILE_ICONS['code']
        elif ext in ['.mp3', '.wav']:
            return self.FILE_ICONS['audio']
        elif ext in ['.mp4', '.mov']:
            return self.FILE_ICONS['video']
        elif ext in ['.zip', '.tar', '.gz']:
            return self.FILE_ICONS['archive']
        return self.FILE_ICONS['default']

    def format_size(self, size):
        if size == '-':
            return '-'
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    def get_formatted_time(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def get_disk_usage(self):
        if platform.system() == 'Windows':
            usage = shutil.disk_usage(os.getcwd())
            return f"{self.format_size(usage.used)} / {self.format_size(usage.total)}"
        else:
            usage = os.statvfs('/')
            total = usage.f_frsize * usage.f_blocks
            used = (usage.f_blocks - usage.f_bfree) * usage.f_frsize
            return f"{self.format_size(used)} / {self.format_size(total)}"

    def get_css(self):
        return """
        :root {
            --primary: #2563eb;
            --background: #f8fafc;
            --text: #1e293b;
        }

        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: var(--background);
            color: var(--text);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
        }

        h1 {
            color: var(--primary);
            margin: 0;
            font-size: 2.5rem;
        }

        .status-bar {
            margin-top: 1rem;
            display: flex;
            justify-content: center;
            gap: 2rem;
            color: #64748b;
        }

        .upload-section {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }

        .upload-options {
            margin: 1rem 0;
        }

        .file-input {
            position: relative;
            margin: 1rem 0;
        }

        .file-input input[type="file"] {
            opacity: 0;
            position: absolute;
            width: 100%;
            height: 100%;
        }

        .file-input label {
            display: block;
            padding: 1rem;
            border: 2px dashed #cbd5e1;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
        }

        .file-input label:hover {
            border-color: var(--primary);
            background: #f1f5f9;
        }

        button {
            background: var(--primary);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            width: 100%;
            transition: opacity 0.2s;
        }

        button:hover {
            opacity: 0.9;
        }

        .file-list {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .search-box {
            margin: 1rem 0;
        }

        #search {
            width: 100%;
            padding: 8px;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }

        th {
            background-color: #f8fafc;
            font-weight: 600;
        }

        tr:hover {
            background-color: #f8fafc;
        }

        .delete-btn {
            background: none;
            border: none;
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
        }

        .delete-btn:hover {
            background-color: #fee2e2;
        }

        .spinner {
            width: 24px;
            height: 24px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        #loading {
            text-align: center;
            margin-top: 1rem;
            color: var(--primary);
        }

        a {
            color: var(--primary);
            text-decoration: none;
            padding: 4px;
            border-radius: 4px;
        }

        a:hover {
            background: #f1f5f9;
        }
        """

    def get_js(self):
        return """
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
        }

        function filterFiles() {
            const search = document.getElementById('search').value.toLowerCase();
            const rows = document.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const name = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
                row.style.display = name.includes(search) ? '' : 'none';
            });
        }

        function deleteFile(filename) {
            if (confirm('Are you sure you want to delete ' + filename + '?')) {
                fetch(filename, {
                    method: 'DELETE'
                }).then(response => {
                    if (response.ok) {
                        location.reload();
                    } else {
                        alert('Failed to delete file');
                    }
                });
            }
        }
        """

    def do_DELETE(self):
        path = self.translate_path(self.path)
        if os.path.exists(path):
            try:
                os.remove(path)
                self.send_response(200)
                self.end_headers()
            except Exception as e:
                self.send_error(500, f"Delete failed: {str(e)}")
        else:
            self.send_error(404, "File not found")

    def do_POST(self):
        if self.path == '/upload':
            try:
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                file_item = form['file']
                if file_item.filename:
                    file_name = os.path.basename(file_item.filename)
                    file_path = os.path.join(os.getcwd(), file_name)
                    
                    # 检查文件是否已存在
                    if os.path.exists(file_path) and not form.getvalue('overwrite'):
                        self.send_error(409, "File already exists")
                        return
                    
                    with open(file_path, 'wb') as f:
                        f.write(file_item.file.read())
                    
                    self.send_response(303)
                    self.send_header('Location', '/')
                    self.end_headers()
            except Exception as e:
                self.send_error(500, f"Upload failed: {str(e)}")
        else:
            self.send_error(404, "Not Found")

if __name__ == '__main__':
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, EnhancedHandler)
    print(f"🚀 Server started at http://localhost:{port}")
    print("✨ Features:")
    print("- Modern UI with file icons")
    print("- File upload with overwrite option")
    print("- File search and deletion")
    print("- Disk usage and server time display")
    print("- Responsive design with enhanced file listing")
    httpd.serve_forever()