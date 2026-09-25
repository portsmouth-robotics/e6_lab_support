from setuptools import find_packages, setup

package_name = 'e6_lab_support'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dobot',
    maintainer_email='technologylabs@port.ac.uk',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'hardware_test = e6_lab_support.hardware_test:main',
            'robot_setup = e6_lab_support.robot_setup:main',
            'pose_monitor = e6_lab_support.pose_monitor:main',
            'movement_demo = e6_lab_support.movement_demo:main',
        ],
    },
)
