#!/usr/bin/python3

from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name = 'vital_sqi',
    version = '0.1.0',
    packages = find_packages(include = ["vital_sqi", "vital_sqi.*"]),
    description = "Signal quality control pipeline for electrocardiogram and "
                 "photoplethysmogram",
    long_description = long_description,
    author='Hai Ho, Khoa Le',
    author_email = 'haihb@oucru.org, khoaldv@oucru.org',
    py_modules = ['common', 'data', 'preprocess', 'sqi'],
    install_requires = ['numpy',
                      'matplotlib',
                      'scipy',
                      'sklearn',
                      'pandas',
                      'tqdm',
                      'plotly',
                      'dtw-python',
                      'py-ecg-detectors'],
    python_requires = '>3.6',
    zip_safe = False,
    url = 'https://github.com/meta00/vital_sqi',
    license = 'GPL 3.0',
    classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
)