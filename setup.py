"""
VIBE1337 - True LLM-Driven AI Agent
Setup configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="vibe1337",
    version="2.1.0",
    author="VIBE1337 Contributors",
    description="A true LLM-driven AI agent where the LLM makes all decisions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oimiragieo/vibe1337",
    packages=find_packages(exclude=["tests", "docs", "ui"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "web": [
            "fastapi>=0.104.1",
            "uvicorn[standard]>=0.24.0",
            "pocketflow",
        ],
        "voice": [
            "numpy",
            "sounddevice",
            "scipy",
            "soundfile",
            "pocketflow",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "all": [
            # Web
            "fastapi>=0.104.1",
            "uvicorn[standard]>=0.24.0",
            # Voice
            "numpy",
            "sounddevice",
            "scipy",
            "soundfile",
            # Common
            "pocketflow",
            # Dev
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "vibe1337=vibe1337:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="ai agent llm chatbot assistant automation",
    project_urls={
        "Bug Reports": "https://github.com/oimiragieo/vibe1337/issues",
        "Source": "https://github.com/oimiragieo/vibe1337",
    },
)
