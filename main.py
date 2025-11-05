import requests
import sys
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import threading
import get_cookie

base_url = "https://pan.baidu.com"
cookie = get_cookie.get_cookies_for_domain(base_url.split("://")[1], browser="firefox")
cookie_header = get_cookie.build_cookie_header(cookie)

# 构建请求URL
share_list_url = "https://pan.baidu.com/share/list"

# 用于线程安全的输出
output_lines = []
output_lock = threading.Lock()

def get_share_list(shorturl, dir_path="/", page=1, num=100):
    """获取分享链接的文件列表"""
    params = {
        "web": "1",
        "app_id": "250528",
        "desc": "1",
        "showempty": "0",
        "page": str(page),
        "num": str(num),
        "order": "time",
        "shorturl": shorturl,
        "root": "1" if dir_path == "/" else "0",
        "dir": dir_path,
        "view_mode": "1",
        "channel": "chunlei",
        "clienttype": "0",
    }
    
    headers = {
        "Cookie": cookie_header,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://pan.baidu.com/",
    }
    
    response = requests.get(share_list_url, params=params, headers=headers)
    return response.json()

def process_directory(shorturl, dir_path, indent, parent_names, is_last_list):
    """处理单个目录
    
    Args:
        shorturl: 分享链接短码
        dir_path: 当前目录路径
        indent: 缩进级别
        parent_names: 父目录名称列表
        is_last_list: 每个层级是否是最后一个元素的列表
    """
    result = get_share_list(shorturl, dir_path)
    
    if result.get("errno") != 0:
        error_msg = f"[错误] {result.get('errmsg', '未知错误')}"
        full_path = "/".join(parent_names) if parent_names else "/"
        prefix = build_tree_prefix(is_last_list)
        with output_lock:
            output_lines.append((full_path, f"{prefix}{error_msg}"))
        return []
    
    file_list = result.get("list", [])
    subdirs = []
    
    for idx, item in enumerate(file_list):
        filename = item.get("server_filename", "未命名")
        is_dir = item.get("isdir", 0)
        size = item.get("size", 0)
        is_last = (idx == len(file_list) - 1)
        
        # 构建完整路径
        current_path_parts = parent_names + [filename]
        full_path = "/".join(current_path_parts)
        
        # 构建树形前缀
        current_is_last_list = is_last_list + [is_last]
        prefix = build_tree_prefix(current_is_last_list)
        
        # 添加到输出
        size_str = f" ({format_size(size)})" if not is_dir else ""
        line = f"{prefix}{filename}{size_str}"
        
        with output_lock:
            output_lines.append((full_path, line))
        
        # 收集子目录
        if is_dir:
            sub_path = item.get("path", "")
            if sub_path:
                subdirs.append((sub_path, indent + 1, current_path_parts, current_is_last_list))
    
    return subdirs

def build_tree_prefix(is_last_list):
    """构建树形结构的前缀
    
    Args:
        is_last_list: 每个层级是否是最后一个元素的布尔值列表
    
    Returns:
        树形结构的前缀字符串
    """
    if not is_last_list:
        return ""
    
    prefix = ""
    for i, is_last in enumerate(is_last_list[:-1]):
        if is_last:
            prefix += "    "  # 4个空格
        else:
            prefix += "│   "  # 竖线 + 3个空格
    
    # 最后一个层级
    if is_last_list:
        if is_last_list[-1]:
            prefix += "└─"  # 最后一个元素
        else:
            prefix += "├─"  # 中间元素
    
    return prefix

def build_directory_tree_parallel(shorturl, max_workers=10):
    """并发构建目录树"""
    # 使用队列来管理待处理的目录: (路径, 缩进, 父目录名称列表, is_last列表)
    to_process = Queue()
    to_process.put(("/", 0, [], []))
    
    processed = set()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        
        while not to_process.empty() or futures:
            # 提交新任务
            while not to_process.empty() and len(futures) < max_workers:
                dir_path, indent, parent_names, is_last_list = to_process.get()
                
                if dir_path in processed:
                    continue
                    
                processed.add(dir_path)
                future = executor.submit(process_directory, shorturl, dir_path, indent, parent_names, is_last_list)
                futures[future] = dir_path
                display_path = "/".join(parent_names) if parent_names else "根目录"
                print(f"正在处理: {display_path}")
            
            # 处理完成的任务
            if futures:
                done, _ = as_completed(futures, timeout=10), None
                for future in list(done):
                    try:
                        subdirs = future.result()
                        for subdir_path, subdir_indent, subdir_parent_names, subdir_is_last_list in subdirs:
                            if subdir_path not in processed:
                                to_process.put((subdir_path, subdir_indent, subdir_parent_names, subdir_is_last_list))
                    except Exception as e:
                        print(f"处理目录 {futures[future]} 时出错: {e}")
                    finally:
                        del futures[future]

def format_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def save_to_file(shorturl, filename="baidu_disk_tree.txt"):
    """保存目录树到文件"""
    global output_lines
    output_lines = []
    
    print(f"正在获取分享链接的目录树: {shorturl}\n")
    build_directory_tree_parallel(shorturl, max_workers=50)
    
    # 按路径排序
    output_lines.sort(key=lambda x: x[0])
    
    # 写入文件
    output_path = Path(__file__).parent / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"百度网盘分享链接目录树\n")
        f.write(f"链接: {shorturl}\n")
        f.write("=" * 80 + "\n\n")
        
        for full_path, display_line in output_lines:
            f.write(display_line + "\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"总计: {len(output_lines)} 项\n")
    
    print(f"\n目录树已保存到: {output_path}")
    print(f"总计: {len(output_lines)} 项")
    
    # 同时保存一个包含完整路径的版本
    detailed_output_path = Path(__file__).parent / filename.replace(".txt", "_detailed.txt")
    with open(detailed_output_path, 'w', encoding='utf-8') as f:
        f.write(f"百度网盘分享链接目录树（详细版）\n")
        f.write(f"链接: {shorturl}\n")
        f.write("=" * 80 + "\n\n")
        
        for full_path, display_line in output_lines:
            f.write(f"{full_path}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write(f"总计: {len(output_lines)} 项\n")
    
    print(f"详细路径已保存到: {detailed_output_path}")

if __name__ == "__main__":
    shorturl = "xxx"
    save_to_file(shorturl)
