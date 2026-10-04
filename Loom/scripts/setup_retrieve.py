#!/usr/bin/env python3
"""
Poyi Loom — BM25 混合检索索引构建脚本 (setup_retrieve.py)
用法: python setup_retrieve.py [--force] [--incremental] [--wiki-path PATH]
"""

import os
import sys
import re
import json
import pickle
import hashlib
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

def ensure_dependencies():
    """检测并自动安装缺失的依赖库。"""
    required = {
        "jieba": "jieba",
        "rank_bm25": "rank-bm25",
        "numpy": "numpy"
    }
    missing = []
    for module_name, pip_name in required.items():
        try:
            __import__(module_name)
        except ImportError:
            missing.append(pip_name)
            
    if missing:
        print(f"[*] 检测到缺失的依赖库: {', '.join(missing)}，正在自动安装...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", *missing, "--quiet"],
                check=True
            )
            print("[OK] 依赖库安装成功！")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] 依赖安装失败，请手动运行: pip install {' '.join(missing)}")
            sys.exit(1)

def tokenize(text):
    """
    混合中英文分词。
    - 中文：jieba 精确模式
    - 英文：空格分割 + 小写化 + 去短词（≤2字符）
    - Wikilinks：提取 [[...]] 中内容作为完整 token
    """
    import jieba
    tokens = []
    # 提取 wikilinks 中的页面名
    wikilinks = re.findall(r'\[\[([^\]]+)\]\]', text)
    for wl in wikilinks:
        name = wl.split('|')[0].strip()
        tokens.append(f'wiki:{name.lower()}')
        
    # 移除 wikilinks 语法后对剩余文本分词
    clean_text = re.sub(r'\[\[[^\]]+\]\]', ' ', text)
    # 中文分词
    cn_tokens = list(jieba.cut(clean_text, cut_all=False))
    for t in cn_tokens:
        t = t.strip()
        if len(t) >= 2:
            tokens.append(t.lower())
    # 英文 token
    en_tokens = re.findall(r'[a-zA-Z0-9]+', clean_text)
    for t in en_tokens:
        if len(t) >= 2:
            tokens.append(t.lower())
    return tokens

def file_hash(filepath):
    """计算文件 SHA256 用于增量检测。"""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def collect_files(wiki_path):
    """收集所有 .md 文件，排除 .retrieve-bm25/、meta/ 和 .obsidian/。"""
    files = []
    exclude_dirs = {'.retrieve-bm25', 'meta', '.obsidian'}
    for root, dirs, filenames in os.walk(wiki_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in filenames:
            if f.endswith('.md'):
                files.append(os.path.join(root, f))
    return sorted(files)

def build_index(files, wiki_path, retrieve_dir, force=False, incremental=False):
    """构建 BM25 索引并持久化。"""
    from rank_bm25 import BM25Okapi
    
    manifest_path = os.path.join(retrieve_dir, 'manifest.json')
    index_path = os.path.join(retrieve_dir, 'index.pkl')
    
    # 检查是否需要重建
    if os.path.exists(retrieve_dir) and not force and not incremental:
        print(f"[INFO] 索引目录已存在: {retrieve_dir}")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8-sig') as fm:
                manifest = json.load(fm)
            print(f"  当前索引: {manifest.get('total_files', 0)} 个文件，构建于 {manifest.get('built_at')}")
        print("  使用 --force 参数强制重建，或 --incremental 执行增量检测更新。")
        return
        
    os.makedirs(retrieve_dir, exist_ok=True)
    
    old_manifest = {}
    if incremental and os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8-sig') as fm:
            old_manifest = json.load(fm)
            
    # 增量模式下，检测文件变化
    if incremental and old_manifest:
        old_hashes = old_manifest.get('file_hashes', {})
        changed_files = []
        for fp in files:
            h = file_hash(fp)
            if fp not in old_hashes or old_hashes[fp] != h:
                changed_files.append(fp)
        if not changed_files:
            print("[INFO] 增量模式: 自上次构建以来无文件变更，索引已是最新。")
            return
        print(f"[INFO] 增量模式: 检测到 {len(changed_files)}/{len(files)} 个文件变更。开始重建...")
    else:
        if force and os.path.exists(retrieve_dir):
            print("[INFO] 强制模式: 正在清除旧索引并重建...")
        else:
            print("[INFO] 开始构建完整 BM25 索引...")
            
    print(f"[INFO] 正在对 {len(files)} 个文档进行分词解析...")
    doc_texts = []
    doc_paths = []
    hashes = {}
    skipped = 0
    
    for i, fp in enumerate(files):
        try:
            with open(fp, 'r', encoding='utf-8-sig', errors='ignore') as fdoc:
                content = fdoc.read()
            tokens = tokenize(content)
            if len(tokens) < 5:
                skipped += 1
                continue
            doc_texts.append(tokens)
            doc_paths.append(fp)
            hashes[fp] = file_hash(fp)
        except Exception as e:
            print(f"  [WARN] 自动跳过文件 {fp}: {e}")
            skipped += 1
            
        if (i + 1) % 50 == 0:
            print(f"  已解析 {i + 1}/{len(files)} 个文件...")
            
    if not doc_texts:
        print("[ERROR] 未找到有效的可索引文档！")
        return
        
    print(f"[INFO] 正在为 {len(doc_texts)} 个文档构建 BM25 模型 (跳过 {skipped} 个过短/空文件)...")
    bm25 = BM25Okapi(doc_texts)
    
    print(f"[INFO] 正在保存序列化模型到 {index_path}...")
    index_data = {
        'bm25': bm25,
        'doc_paths': doc_paths,
        'doc_count': len(doc_paths)
    }
    with open(index_path, 'wb') as f_idx:
        pickle.dump(index_data, f_idx)
        
    # 保存 manifest.json
    manifest = {
        'built_at': datetime.now().isoformat(),
        'total_files': len(doc_paths),
        'skipped_files': skipped,
        'wiki_path': str(wiki_path),
        'index_path': str(index_path),
        'file_hashes': hashes,
        'version': '1.0.0'
    }
    with open(manifest_path, 'w', encoding='utf-8') as fm:
        json.dump(manifest, fm, indent=2, ensure_ascii=False)
        
    index_size_mb = os.path.getsize(index_path) / (1024 * 1024)
    print(f"[DONE] 索引构建成功: {len(doc_paths)} 个文档, 大小: {index_size_mb:.2f} MB")

def main():
    parser = argparse.ArgumentParser(description="Poyi Loom — BM25 Index Builder")
    parser.add_argument("-f", "--force", action="store_true", help="强制重建全量索引")
    parser.add_argument("-i", "--incremental", action="store_true", help="仅对发生变更的文件增量更新")
    parser.add_argument("-w", "--wiki-path", default=r"D:\Projects\Poyi\Loom\wiki", help="Loom Wiki 目录物理路径")
    
    args = parser.parse_args()
    
    print("=== Poyi Loom — BM25 Index Builder ===")
    wiki_path = Path(args.wiki_path).resolve()
    retrieve_dir = wiki_path / ".retrieve-bm25"
    
    print(f"Wiki 路径: {wiki_path}")
    print(f"索引目录: {retrieve_dir}\n")
    
    ensure_dependencies()
    
    if not wiki_path.exists():
        print(f"[ERROR] 目标 Wiki 目录不存在: {wiki_path}")
        sys.exit(1)
        
    files = collect_files(str(wiki_path))
    build_index(files, wiki_path, str(retrieve_dir), force=args.force, incremental=args.incremental)

if __name__ == "__main__":
    main()
