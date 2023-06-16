# GreenWaveSim
A discrete event traffic simulation for green-wave control

- main.py: 仿真程序入口
- athens.py: 保存仿真区域link，node，信号灯等数据的文件和一些常量
- sim.py: 实现了一个simulation类。
- net.py: 实现了network类（实现了车辆生成的方法），link类，net类，和继承自net类的trafficLightNode类。
- car.py: 实现了一个car类。
- util.py: 一些辅助函数和辅助变量定义