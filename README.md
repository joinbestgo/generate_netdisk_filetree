# Baidu Netdisk Share Link Directory Tree Generator

A Python tool to generate a complete directory tree from Baidu Netdisk (Baidu Pan) share links with concurrent processing for faster execution.

## Features

- 🚀 **Concurrent Processing**: Uses multi-threading to speed up directory traversal
- 🌳 **Tree Structure Output**: Generates beautiful tree-style directory structure
- 📁 **Dual Output Formats**: Creates both tree view and full path list
- 📊 **File Size Display**: Shows file sizes in human-readable format
- 🔄 **Progress Tracking**: Real-time progress updates during processing

## Prerequisites

- Python 3.7+
- Firefox browser (for cookie extraction)
- Valid Baidu Netdisk account with active session

## Installation

1. Clone this repository or download the source code
2. Install required dependencies:

```bash
pip install requests
```

3. Ensure you have the cookie extraction module in your project. The tool depends on:

```python
from python.alice.service import get_cookie
```

## Configuration

### Required Modifications

Before running the script, you need to modify the following:

#### 1. Cookie Extraction Module Path

Update the import path to match your project structure:

```python
# Current path (line 14):
from python.alice.service import get_cookie

# Modify to your actual module path, for example:
from your_module.service import get_cookie
```

#### 2. Browser Selection

The script uses Firefox by default. If you use a different browser, modify line 17:

```python
# Current setting:
cookie = get_cookie.get_cookies_for_domain(base_url.split("://")[1], browser="firefox")

# Available options: "chrome", "firefox", "edge", "safari"
cookie = get_cookie.get_cookies_for_domain(base_url.split("://")[1], browser="chrome")
```

#### 3. Share Link Short URL

Modify the short URL at the bottom of the file (line 226):

```python
if __name__ == "__main__":
    # Replace with your share link short code
    shorturl = "YOUR_SHORT_URL_HERE"
    save_to_file(shorturl)
```

**How to get the short URL:**

- From share link: `https://pan.baidu.com/s/xxx`
- Extract the code after `/s/`: `xxx`
- Or use the shortened version: `xxx`

### Optional Modifications

#### 4. Concurrent Workers

Adjust the number of concurrent threads (line 205):

```python
# Current setting: 50 workers
build_directory_tree_parallel(shorturl, max_workers=50)

# Recommended range: 5-50
# Higher values = faster but may trigger rate limiting
build_directory_tree_parallel(shorturl, max_workers=20)
```

#### 5. Output File Names

Change the output file names (line 202):

```python
save_to_file(shorturl, filename="baidu_disk_tree.txt")

# Custom name:
save_to_file(shorturl, filename="my_directory_tree.txt")
```

#### 6. Items Per Page

Adjust the number of items fetched per request (line 31):

```python
def get_share_list(shorturl, dir_path="/", page=1, num=100):
    # num parameter: 1-100, default 100
```

## Usage

1. Make sure you're logged into Baidu Netdisk in your Firefox browser
2. Update the configuration as described above
3. Run the script:

```bash
python main.py
```

4. The script will generate two files:
   - `baidu_disk_tree.txt`: Tree-style directory structure
   - `baidu_disk_tree_detailed.txt`: Full path list

## Output Example

### Tree View (baidu_disk_tree.txt)

```
├─Python
│  ├─Course_Materials
│  │  ├─Lecture_01.pdf (2.50 MB)
│  │  ├─Lecture_02.pdf (3.20 MB)
│  │  └─Videos
│  │     ├─Day01
│  │     │  ├─Introduction.mp4 (150.30 MB)
│  │     │  └─Setup.mp4 (89.50 MB)
```

### Full Path List (baidu_disk_tree_detailed.txt)

```
Python
Python/Course_Materials
Python/Course_Materials/Lecture_01.pdf
Python/Course_Materials/Lecture_02.pdf
Python/Course_Materials/Videos
Python/Course_Materials/Videos/Day01
Python/Course_Materials/Videos/Day01/Introduction.mp4
```

## Troubleshooting

### Common Issues

1. **Cookie Error**: Make sure you're logged into Baidu Netdisk in the specified browser
2. **Rate Limiting**: If you get errors, reduce the `max_workers` value
3. **Import Error**: Ensure the cookie extraction module path is correct
4. **Permission Denied**: The share link may require a password or be expired
5. **Timeout Error**: Increase the timeout value in line 171:

```python
done, _ = as_completed(futures, timeout=10), None  # Increase timeout value
```

## Project Structure

```
sre_tools/
├── python/
│   ├── baidu_disk/
│   │   ├── main.py
│   │   ├── README.md
│   │   └── (other modules)
```

## Notes

- This tool is for personal use and educational purposes only
- Respect Baidu's terms of service and rate limits
- The share link must be publicly accessible or you must be logged in
- Large directories may take several minutes to process

## License

This tool is provided as-is for personal use.

## Contributing

Feel free to submit issues or pull requests for improvements.
