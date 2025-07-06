#!/usr/bin/env python3
"""
安全检查脚本
用于检查代码中的潜在安全问题
"""

import os
import re
import sys

def check_security_issues(filename):
    """检查单个文件的安全问题"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 检查硬编码密码或密钥
        password_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'pwd\s*=\s*["\'][^"\']+["\']',
            r'passwd\s*=\s*["\'][^"\']+["\']'
        ]
        
        for pattern in password_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append('Possible hardcoded password')
                break
        
        # 检查API密钥
        api_key_patterns = [
            r'(api_key|secret_key|access_key|private_key)\s*=\s*["\'][^"\']+["\']',
            r'(token|secret|key)\s*=\s*["\'][A-Za-z0-9]{20,}["\']'
        ]
        
        for pattern in api_key_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append('Possible hardcoded API key or secret')
                break
        
        # 检查危险函数使用
        dangerous_functions = [
            ('eval(', 'Use of eval() function'),
            ('exec(', 'Use of exec() function'),
            ('pickle.loads(', 'Use of pickle.loads() - potential security risk'),
            ('subprocess.call(', 'Use of subprocess.call() - check for shell injection'),
            ('os.system(', 'Use of os.system() - potential command injection')
        ]
        
        for func_call, message in dangerous_functions:
            if func_call in content:
                issues.append(message)
        
        # 检查SQL注入风险
        sql_patterns = [
            r'SELECT\s+.*\s+.*%.*%',
            r'INSERT\s+.*\s+.*%.*%',
            r'UPDATE\s+.*\s+.*%.*%',
            r'DELETE\s+.*\s+.*%.*%'
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append('Potential SQL injection risk')
                break
        
        # 检查文件路径遍历风险
        if re.search(r'\.\.[\\/]', content):
            issues.append('Potential path traversal vulnerability')
        
        # 报告结果
        if issues:
            print(f'⚠️ {filename}: {len(issues)} issue(s) found')
            for i, issue in enumerate(issues, 1):
                print(f'   {i}. {issue}')
        else:
            print(f'✅ {filename}: No security issues found')
            
        return len(issues) == 0
        
    except FileNotFoundError:
        print(f'⚠️ File not found: {filename}')
        return True  # 不算作错误
    except Exception as e:
        print(f'❌ Error checking {filename}: {e}')
        return False

def main():
    """主函数"""
    print("🔒 Running security checks...")
    
    # 要检查的文件列表
    files_to_check = [
        'main.py',
        'gui.py', 
        'config.py',
        'file_operations.py',
        'utils.py',
        'constants.py'
    ]
    
    # 扫描所有Python文件
    for root, dirs, files in os.walk('.'):
        # 跳过某些目录
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', 'env', 'build', 'dist', '.pytest_cache'}]
        
        for file in files:
            if file.endswith('.py') and file not in ['security_check.py', 'local_test_actions.py', 'test_build.py']:
                file_path = os.path.join(root, file)
                if file_path.startswith('./'):
                    file_path = file_path[2:]
                if file_path not in files_to_check:
                    files_to_check.append(file_path)
    
    # 检查所有文件
    all_clean = True
    total_files = 0
    
    for file_path in sorted(set(files_to_check)):
        if os.path.exists(file_path):
            total_files += 1
            if not check_security_issues(file_path):
                all_clean = False
    
    print(f"\n📊 Security check summary:")
    print(f"   Files checked: {total_files}")
    
    if all_clean:
        print("   ✅ No security issues found")
        return 0
    else:
        print("   ⚠️ Security issues found - please review")
        return 1

if __name__ == '__main__':
    sys.exit(main())
