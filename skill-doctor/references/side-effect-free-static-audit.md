# 无副作用静态审计

批量审计 Skill 库时，验证动作不能修改被审对象；否则后续 manifest、Git status、包哈希和“本次新增问题”都会失真。

## Python 语法检查

不要在源码树中执行：

```bash
python -m py_compile path/to/file.py
```

它会默认写入 `__pycache__/*.pyc`。

使用内存编译：

```python
from pathlib import Path

path = Path("path/to/file.py")
source = path.read_text(encoding="utf-8")
compile(source, str(path), "exec")
```

只需语法树时也可用：

```python
import ast
ast.parse(source, filename=str(path))
```

## 其他检查

- Shell：`bash -n file.sh`，不执行脚本。
- JSON/YAML：只解析，不格式化回写。
- Markdown：逐行状态机检查 fence；只把真实 Markdown 相对链接当硬错误，反引号内路径只是人工线索。
- 密钥扫描：命中后先做占位符、唯一字符数和熵分类；报告不回显原值。

## 审计前后门禁

1. 审计前记录被审根目录的文件清单、Git status 和包哈希。
2. 所有临时产物写入独立报告目录，不写入 Skill 包。
3. 扫描器排除 `__pycache__`、`.archive`、`.archived`、`.restore-backups`，但运行时资产盘点必须单独检查这些目录是否仍会被加载。
4. 审计后重跑文件清单和 Git status，差异必须归因。
5. 如果旧扫描器已生成缓存：先生成精确清理清单（路径、mtime、大小、范围），删除需按用户授权边界执行；清理后重新生成 manifest 和静态基线。
6. 只有“审计产物0写入被审树 + 当前 manifest hash与静态报告绑定”时，才能锁定最终基线。
