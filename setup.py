from pathlib import Path
from setuptools import setup, find_packages

here = Path(__file__).parent

with (here / 'README.md').open(encoding='utf8') as f:
    long_description = f.read()

setup(
    name='trio-chrome-devtools-protocol',
    version='0.1.0-dev',
    description='Trio driver for Chrome DevTools Protocol (CDP)',
    long_description=long_description,
    url='https://github.com/HyperionGray/trio-chrome-devtools-protocol',
    author='Mark E. Haase <mehaase@gmail.com>',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.7',
    keywords='trio chrome devtools protocol cdp',
    package_data={'trio_cdp': ['py.typed']},
    packages=find_packages(exclude=['build', 'docs', 'examples', 'tests']),
    install_requires=[
        'python-chrome-devtools-protocol',
        'trio',
        'trio_websocket',
    ],
)
