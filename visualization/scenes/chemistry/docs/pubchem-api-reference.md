# PubChem PUG REST API 参考文档

> **官方文档**: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
>
> **更新日期**: 2026-03-23

---

## 目录

- [基础 URL 格式](#基础-url-格式)
- [获取分子 SDF 数据](#获取分子-sdf-数据)
- [常用接口示例](#常用接口示例)
- [返回格式说明](#返回格式说明)
- [错误响应格式](#错误响应格式)
- [速率限制](#速率限制)

---

## 基础 URL 格式

PubChem PUG REST API 使用 URL 路径来表达查询意图,基本格式为:

```
https://pubchem.ncbi.nlm.nih.gov/rest/pug/<input>/<operation>/[<output>][?<options>]
```

**三个核心部分**:
- **Input**: 指定要查询的记录(如 CID、名称、SMILES 等)
- **Operation**: 指定要执行的操作(如获取属性、记录、同义词等)
- **Output**: 指定输出格式(如 JSON、XML、SDF、TXT 等)

---

## 获取分子 SDF 数据

### 基本格式

```
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/SDF
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF
```

### `record_type` 参数

**2D vs 3D 坐标**:

```bash
# 获取 2D 坐标(默认)
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/SDF?record_type=2d

# 获取 3D 坐标
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/SDF?record_type=3d
```

**区别说明**:
- `record_type=2d`: 返回 2D 平面坐标,适用于化学结构展示
- `record_type=3d`: 返回 3D 空间坐标,包含完整的分子构象数据

**3D 坐标示例**:
```bash
# 获取阿司匹林的 3D SDF
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/SDF?record_type=3d

# 获取 CID 2244 的 3D 坐标
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/SDF?record_type=3d
```

### 其他 SDF 查询方式

```bash
# 通过 InChIKey 获取
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/BPGDAMSIGCZZLK-UHFFFAOYSA-N/SDF

# 通过 SMILES 获取(需要 POST)
POST https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/SDF
Body: smiles=CC(=O)Oc1ccccc1C(=O)O
```

---

## 常用接口示例

### 1. 通过 CAS 号查询 CID

```bash
# CAS 号(RN)转 CID
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/50-78-2/cids/TXT

# 通过 xref/RN 查询
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/xref/RN/50-78-2/cids/XML
```

**示例 - 获取阿司匹林的 CID**:
```bash
# CAS: 50-78-2 (Aspirin)
curl "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/50-78-2/cids/TXT"
# 返回: 2244
```

### 2. 通过 CID 获取 SMILES

```bash
# 获取 IsomericSMILES(包含立体化学信息)
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/property/IsomericSMILES/TXT

# 获取 CanonicalSMILES
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/property/CanonicalSMILES/TXT
```

**示例**:
```bash
curl "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/property/IsomericSMILES/TXT"
# 返回: CC(=O)OC1=CC=CC=C1C(=O)O
```

### 3. 获取分子属性

**单属性查询**:
```bash
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/property/MolecularWeight/JSON
```

**多属性查询**(逗号分隔):
```bash
# 获取分子量、TPSA、LogP
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/property/MolecularWeight,TPSA,XLogP/JSON

# 获取分子式、分子量、InChIKey
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/property/MolecularFormula,MolecularWeight,InChIKey/JSON
```

**批量查询多个 CID**:
```bash
# 批量获取 CID 1-5 的属性
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1,2,3,4,5/property/MolecularFormula,MolecularWeight,InChIKey/CSV
```

### 4. 可用属性列表

| 属性标签 | 说明 |
|---------|------|
| `MolecularFormula` | 分子式 |
| `MolecularWeight` | 分子量(g/mol) |
| `SMILES` | SMILES 字符串(含立体化学) |
| `CanonicalSMILES` | 规范 SMILES |
| `IsomericSMILES` | 异构 SMILES |
| `InChI` | IUPAC 国际化学标识符 |
| `InChIKey` | InChI 的哈希值(27 字符) |
| `IUPACName` | IUPAC 系统命名 |
| `XLogP` | 辛醇-水分配系数 |
| `TPSA` | 拓扑极性表面积 |
| `Complexity` | 分子复杂度 |
| `Charge` | 总电荷 |
| `HBondDonorCount` | 氢键供体数 |
| `HBondAcceptorCount` | 氢键受体数 |
| `RotatableBondCount` | 可旋转键数 |
| `HeavyAtomCount` | 重原子数(非氢) |
| `ExactMass` | 精确质量 |
| `MonoisotopicMass` | 单同位素质量 |

### 5. 获取同义词列表

```bash
# 通过名称获取同义词
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/synonyms/XML

# 通过 CID 获取同义词
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/synonyms/JSON
```

### 6. 通过名称查询 CID

```bash
# 精确匹配
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/cids/TXT

# 模糊匹配(包含关键词)
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/cids/XML?name_type=word

# 完整匹配
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/cids/XML?name_type=complete
```

---

## 返回格式说明

### 支持的输出格式

| 格式 | MIME Type | 说明 | 适用场景 |
|-----|-----------|------|---------|
| **JSON** | `application/json` | JSON 格式 | 程序化访问,最常用 |
| **XML** | `application/xml` | XML 格式 | 结构化数据 |
| **SDF** | `chemical/x-mdl-sdfile` | 结构数据文件 | 分子 2D/3D 坐标 |
| **CSV** | `text/csv` | 逗号分隔值 | 表格数据,Excel 兼容 |
| **TXT** | `text/plain` | 纯文本 | 单一属性值列表 |
| **PNG** | `image/png` | PNG 图像 | 分子结构图 |
| **ASNT** | - | ASN.1 文本格式 | NCBI 内部格式 |
| **ASNB** | `application/ber-encoded` | ASN.1 二进制 | Base64 编码 |
| **JSONP** | `application/javascript` | JSONP 格式 | 跨域请求 |

### 使用 HTTP Accept 头部指定格式

除了在 URL 中指定格式,也可以通过 HTTP 请求头指定:

```bash
curl -H "Accept: application/json" \
  "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244"

curl -H "Accept: chemical/x-mdl-sdfile" \
  "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244"

curl -H "Accept: image/png" \
  "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244"
```

### JSONP 示例

```bash
# 默认回调函数名 "callback"
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/property/MolecularFormula/JSONP

# 自定义回调函数名
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/property/MolecularFormula/JSONP?callback=my_callback
```

### PNG 图像选项

```bash
# 默认大小(300x300)
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/PNG

# 小图(100x100)
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/PNG?image_size=small

# 大图(300x300)
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/PNG?image_size=large

# 自定义尺寸
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/PNG?image_size=320x240

# 3D 结构图
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/PNG?record_type=3d
```

---

## 错误响应格式

### HTTP 状态码

| HTTP 状态码 | 错误代码 | 含义 |
|-----------|---------|------|
| **200** | - | 成功 |
| **202** | - | 已接受(异步操作中) |
| **400** | `PUGREST.BadRequest` | 请求格式错误(URL 语法错误等) |
| **404** | `PUGREST.NotFound` | 记录未找到(如无效的 CID) |
| **405** | `PUGREST.NotAllowed` | 请求不被允许(如无效的 MIME 类型) |
| **500** | `PUGREST.Unknown` | 未知错误 |
| **500** | `PUGREST.ServerError` | 服务器端问题(数据库故障等) |
| **501** | `PUGREST.Unimplemented` | 功能未实现 |
| **503** | `PUGREST.ServerBusy` | 服务器繁忙,请稍后重试 |
| **504** | `PUGREST.Timeout` | 请求超时 |

### 错误响应示例

**JSON 格式错误响应**:
```json
{
  "Fault": {
    "Code": "PUGREST.NotFound",
    "Message": "No records found for the given CID(s)",
    "Details": [
      "CID 999999999 not found"
    ]
  }
}
```

**XML 格式错误响应**:
```xml
<Fault>
  <Code>PUGREST.NotFound</Code>
  <Message>No records found for the given CID(s)</Message>
  <Details>
    <Detail>CID 999999999 not found</Detail>
  </Details>
</Fault>
```

**常见错误场景**:

1. **无效的 CID (404)**:
```bash
curl "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/999999999/property/MolecularWeight/JSON"
# 返回 404 + 错误信息
```

2. **无效的属性名 (400)**:
```bash
curl "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/property/InvalidProperty/JSON"
# 返回 400 + 错误信息
```

3. **服务器过载 (503)**:
```bash
# 高频请求时可能返回 503
# 建议:添加延迟,降低请求频率
```

---

## 速率限制

### 官方限制策略

PubChem API 对请求频率有严格限制,以保护共享服务器资源:

| 限制类型 | 数值 | 说明 |
|---------|-----|------|
| **每秒请求数** | ≤ 5 req/s | 任何用户/应用/组织 |
| **每分钟请求数** | ≤ 400 req/min | 每个 IP 地址 |
| **运行时间** | ≤ 300 sec/min | 服务器端计算时间 |

### 最佳实践

**1. 添加请求延迟**:
```python
import time
import requests

def fetch_with_delay(cid, delay=0.2):
    """添加 200ms 延迟,确保不超过 5 req/s"""
    time.sleep(delay)
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularWeight/JSON"
    return requests.get(url)
```

**2. 批量请求优化**:
```python
# 不推荐:逐个查询
for cid in cids:
    fetch_single(cid)  # 大量请求

# 推荐:批量查询
url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1,2,3,4,5/property/MolecularWeight/JSON"
response = requests.get(url)
```

**3. 错误重试机制**:
```python
import time
import requests

def fetch_with_retry(url, max_retries=3, delay=1):
    """遇到 503 错误时自动重试"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code == 503:
                time.sleep(delay * (attempt + 1))
                continue
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay)
    return None
```

**4. 使用 POST 请求处理大量数据**:
```bash
# POST 请求可以处理超过 URL 长度限制的 CID 列表
POST https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/property/MolecularFormula,MolecularWeight/CSV
Content-Type: application/x-www-form-urlencoded

cid=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
```

### 动态限流说明

PubChem 实施了**动态请求限流**机制:
- 根据服务器负载自动调整限流策略
- 高峰期可能降低允许的请求频率
- 建议:监控响应状态码,遇到 503 时降低请求频率

### 重要提示

- **无 API Key**: PubChem 不提供 API Key 或白名单服务
- **不可超出限制**: 无法申请提高配额
- **大数据集**: 如需处理大规模数据,请联系 PubChem 团队寻求优化建议
- **批量下载**: 考虑使用 [PubChem 批量数据下载](https://pubchem.ncbi.nlm.nih.gov/docs/bulk-data)服务

---

## 完整示例代码

### Python 示例

```python
import requests
import time

class PubChemAPI:
    """PubChem PUG REST API 封装"""

    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    DELAY = 0.2  # 200ms 延迟

    @classmethod
    def get_cid_by_name(cls, name):
        """通过名称获取 CID"""
        time.sleep(cls.DELAY)
        url = f"{cls.BASE_URL}/compound/name/{name}/cids/TXT"
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()

    @classmethod
    def get_smiles(cls, cid):
        """通过 CID 获取 SMILES"""
        time.sleep(cls.DELAY)
        url = f"{cls.BASE_URL}/compound/cid/{cid}/property/IsomericSMILES/TXT"
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()

    @classmethod
    def get_properties(cls, cid, properties):
        """获取多个属性"""
        time.sleep(cls.DELAY)
        props_str = ",".join(properties)
        url = f"{cls.BASE_URL}/compound/cid/{cid}/property/{props_str}/JSON"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    @classmethod
    def get_sdf_3d(cls, cid):
        """获取 3D SDF 坐标"""
        time.sleep(cls.DELAY)
        url = f"{cls.BASE_URL}/compound/cid/{cid}/SDF?record_type=3d"
        response = requests.get(url)
        response.raise_for_status()
        return response.text

# 使用示例
if __name__ == "__main__":
    # 1. 通过名称查询 CID
    cid = PubChemAPI.get_cid_by_name("aspirin")
    print(f"CID: {cid}")

    # 2. 获取 SMILES
    smiles = PubChemAPI.get_smiles(cid)
    print(f"SMILES: {smiles}")

    # 3. 获取多个属性
    props = PubChemAPI.get_properties(cid, ["MolecularWeight", "TPSA", "XLogP"])
    print(f"Properties: {props}")

    # 4. 获取 3D SDF
    sdf = PubChemAPI.get_sdf_3d(cid)
    print(f"SDF (前 100 字符): {sdf[:100]}")
```

### cURL 示例

```bash
# 1. 查询 CID
curl "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/cids/TXT"

# 2. 获取 SMILES
curl "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/property/IsomericSMILES/TXT"

# 3. 获取多个属性(JSON)
curl "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/property/MolecularWeight,TPSA,XLogP/JSON"

# 4. 获取 3D SDF
curl "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/SDF?record_type=3d" -o aspirin_3d.sdf

# 5. 获取 2D SDF
curl "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/SDF" -o aspirin_2d.sdf

# 6. 通过 CAS 号查询
curl "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/50-78-2/cids/TXT"

# 7. 批量查询(CSV 格式)
curl "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244,1983,5288826/property/MolecularFormula,MolecularWeight/CSV"

# 8. 使用 POST 请求
curl -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "cid=1,2,3,4,5" \
  "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/property/MolecularWeight/JSON"
```

---

## 参考资源

- **官方文档**: [PUG REST API Documentation](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest)
- **教程**: [PUG REST Tutorial](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest-tutorial)
- **动态限流**: [Dynamic Request Throttling](https://pubchem.ncbi.nlm.nih.gov/docs/dynamic-request-throttling)
- **程序化访问指南**: [Programmatic Access](https://pubchem.ncbi.nlm.nih.gov/docs/programmatic-access)
- **XML Schema**: [pug_rest.xsd](https://pubchem.ncbi.nlm.nih.gov/pug_rest/pug_rest.xsd)

---

## 相关论文

1. Kim S, Thiessen PA, Cheng T, Yu B, Bolton EE. **An update on PUG-REST: RESTful interface for programmatic access to PubChem**. *Nucleic Acids Res*. 2018 July 2; 46(W1):W563-570. doi:10.1093/nar/gky294.
   - [PubMed](https://pubmed.ncbi.nlm.nih.gov/29718389/) | [Full Text](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6030920/)

2. Kim S, Thiessen PA, Bolton EE, Bryant SH. **PUG-SOAP and PUG-REST: web services for programmatic access to chemical information in PubChem**. *Nucleic Acids Res*. 2015 Jul 1; 43(W1):W605-W611. doi: 10.1093/nar/gkv396.
   - [PubMed](https://pubmed.ncbi.nlm.nih.gov/25934803/)

---

**最后更新**: 2026-03-23
**文档来源**: PubChem Official Documentation
