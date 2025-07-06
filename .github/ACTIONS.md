# GitHub Actions 构建流程说明

本项目包含了完整的GitHub Actions自动构建流程，支持多平台构建和自动发布。

## 工作流文件说明

### 1. `build.yml` - 主构建流程
- **触发条件**: 推送到main/master/develop分支，创建标签，或手动触发
- **功能**:
  - 在Windows、Linux、macOS三个平台上构建应用
  - 自动打包为可分发的压缩文件
  - 在创建Git标签时自动创建GitHub Release
  - 上传构建产物和构建信息

### 2. `test-build.yml` - 快速测试构建
- **触发条件**: 推送到test分支或feature分支
- **功能**:
  - 仅在Windows平台进行快速构建测试
  - 验证代码可以正常导入和基本构建
  - 适用于开发阶段的快速验证

### 3. `quality.yml` - 代码质量检查
- **触发条件**: 推送到main/master/develop分支或创建Pull Request
- **功能**:
  - 代码格式检查（Black）
  - 代码规范检查（flake8）
  - 类型检查（mypy）
  - 安全性检查
  - 项目结构检查
  - 依赖项安全扫描

## 使用说明

### 开发工作流

1. **日常开发**:
   ```bash
   # 在feature分支上开发
   git checkout -b feature/new-feature
   # 推送时会触发test-build进行快速验证
   git push origin feature/new-feature
   ```

2. **提交到主分支**:
   ```bash
   # 合并到develop分支会触发完整构建和质量检查
   git checkout develop
   git merge feature/new-feature
   git push origin develop
   ```

3. **发布版本**:
   ```bash
   # 创建标签会自动触发发布流程
   git tag v1.0.0
   git push origin v1.0.0
   ```

### 构建产物

构建完成后，可以在以下位置找到产物：

- **Actions页面**: GitHub仓库的Actions标签页
- **Artifacts**: 每次构建的临时产物（保留30天）
- **Releases**: 标签构建的正式发布版本（永久保留）

### 支持的平台

| 平台 | 文件格式 | 说明 |
|------|----------|------|
| Windows | `.zip` | 包含.exe可执行文件 |
| Linux | `.tar.gz` | 包含可执行文件 |
| macOS | `.tar.gz` | 包含.app应用包 |

### 环境要求

- Python 3.9
- PyQt5 >= 5.15.0
- pynput >= 1.7.0

### 自定义构建

如果需要修改构建流程，可以编辑对应的YAML文件：

- 修改Python版本: 更改`python-version`
- 添加新的依赖: 修改`requirements.txt`或在workflow中添加安装步骤
- 修改构建脚本: 更新`build_optimized.py`的调用
- 调整构建平台: 修改`matrix.include`部分

### 故障排除

1. **构建失败**:
   - 检查Actions页面的详细日志
   - 确认所有依赖都在`requirements.txt`中
   - 检查代码是否有语法错误

2. **Linux构建问题**:
   - 可能需要添加额外的系统依赖
   - 确认Qt相关库已正确安装

3. **macOS构建问题**:
   - 可能需要代码签名（需要Apple开发者账户）
   - 检查macOS特定的依赖项

### 高级配置

#### 启用代码签名（Windows）
如果需要为Windows可执行文件签名，可以添加以下步骤：

```yaml
- name: Sign Windows executable
  if: matrix.platform == 'windows'
  uses: dlemstra/code-sign-action@v1
  with:
    certificate: '${{ secrets.CERTIFICATE }}'
    password: '${{ secrets.CERTIFICATE_PASSWORD }}'
    folder: 'dist'
```

#### 自定义Release Notes
修改`build.yml`中的release notes生成部分，可以自动从CHANGELOG.md读取或使用commit信息。

#### 缓存优化
为了加速构建，可以添加pip缓存：

```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

## 注意事项

1. **私有仓库**: 确保有足够的GitHub Actions分钟数
2. **大文件**: 构建产物超过2GB需要使用Git LFS
3. **敏感信息**: 不要在workflow中硬编码密码或密钥
4. **权限**: 确保GITHUB_TOKEN有足够权限创建Release

## 监控和维护

- 定期检查Actions运行状态
- 更新依赖项版本
- 监控构建时间和资源使用
- 清理旧的Artifacts以节省存储空间
