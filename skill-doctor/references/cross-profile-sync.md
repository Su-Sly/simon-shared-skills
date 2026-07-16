# 跨 Profile 同步

当用户说"覆盖到所有 profile"：

```bash
SRC=~/.hermes/skills/skill-doctor/SKILL.md
for p in work work-web finance; do
  DST=~/.hermes/profiles/$p/skills/skill-doctor/SKILL.md
  [ -d "$(dirname "$DST")" ] && cp "$SRC" "$DST"
done
```

注意：references/ 目录也需要同步，否则子 profile 只拿到主文件但缺引用。
