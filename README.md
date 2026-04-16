# PlanX3D

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)
![Blender](https://img.shields.io/badge/blender-4.2%2B-orange.svg)
![OpenCV](https://img.shields.io/badge/opencv-4.13%2B-green.svg)

Convert your 2D architectural blueprints into detailed 3D models with ease.

![PlanX3D 3D Model Preview](Images/Examples/blender_preview.png)

---

## Project Overview

PlanX3D was developed to solve the challenge of efficiently converting 2D architectural blueprints into 3D models — a process that traditionally requires significant time, effort, and expertise.

### Our Solution

- **Problem Statement**: Converting 2D blueprints into 3D models is often slow and complex.
- **Innovation**: PlanX3D uses advanced computer vision and machine learning techniques to automate this process, making it faster and more accessible.
- **Impact**: This tool can transform architectural visualization, urban planning, and construction workflows by reducing manual effort and improving accuracy.

---

## Features

- Accurate conversion of 2D blueprints into precise 3D models
- Support for multiple 2D blueprint file formats
- Customizable output in popular 3D formats (OBJ, FBX, GLTF)
- Automatic texture mapping for realistic finishes
- Cloud-based processing for handling large blueprints efficiently

---

## Online Demo

Try PlanX3D without installation. Visit our [Online Demo](demovideo) to see it in action.

---

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/ragulvl/PlanX3D.git
   cd PlanX3D
   ```

2. **Set up the environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements_core.txt
   ```

3. **Run the conversion**
   ```bash
   python cli_pipeline.py
   ```
   Or launch the GUI:
   ```bash
   python gui_converter.py
   ```

4. Find your 3D model in the `Target/` output directory.

---

## Prerequisites

- Python 3.7+
- OpenCV
- NumPy
- Blender 4.2+ (required for 3D model generation — [download here](https://www.blender.org/download/))

---

## Installation

Install core dependencies:
```bash
pip install -r requirements_core.txt
```

For the GUI:
```bash
pip install -r requirements_gui.txt
```

For the server:
```bash
pip install flask
```

Configure your Blender path in `Configs/system.ini` before running.

---

## Contributing

We welcome contributions. Please open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to [OpenCV](https://opencv.org/) and [Blender](https://www.blender.org/) for their powerful tools

---

## Team

- **Ragul VL** — [ragulvl](https://github.com/ragulvl)
- **Manoj M** — [manoj-mpp](https://github.com/manoj-mpp)
- **Dharshini M** — [dharsh2326](https://github.com/dharsh2326)

---

## Contact

Project Link: [https://github.com/ragulvl/PlanX3D](https://github.com/ragulvl/PlanX3D)

If you find this project useful, please consider giving it a star.
