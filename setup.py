import setuptools

setuptools.setup(
    name="yt-web",
    version="1.0",
    license="MIT",
    description="TEST",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["Flask==3.0.3",
                      "Flask-Session==0.5.0",
                      "Flask-SocketIO==5.3.6",
                      "yt-dlp"],
    entry_points={
    'console_scripts': [
        'yt-web = website_youtube_dl.youtube_dl_run:main',
        ],
    },
    include_package_data=True
    )
