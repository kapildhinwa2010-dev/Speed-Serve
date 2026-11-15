# Speed-Serve

Model registry and request envelopes (service layer).

**Part of the [Kapildhinwa2010-dev Toolkit](https://github.com/kapildhinwa2010-dev/Kapildhinwa2010-dev).**

![CI](https://github.com/kapildhinwa2010-dev/Speed-Serve/actions/workflows/ci.yml/badge.svg)
![CodeQL](https://github.com/kapildhinwa2010-dev/Speed-Serve/actions/workflows/codeql.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- Versioned model registry with `latest` resolution
- Validated request envelopes
- Latency and payload-size statistics

## 📦 Install

```bash
pip install -r requirements.txt
```

## 🚀 Quick start

```python
from speed_serve import ServeRegistry, Envelope

registry = ServeRegistry()
registry.register('m', '1.0', lambda x: x * 2)
print(registry.serve('m', Envelope('r1', x)))
```

## 🧪 Tests

```bash
pytest tests/ -v
```

## 📄 License

MIT — see [LICENSE](LICENSE).
