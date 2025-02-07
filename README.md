## 📖 Table of Contents

- [📖 Table of Contents](#-table-of-contents)
- [📍 Overview](#-overview)
- [📂 Repository Structure](#-repository-structure)
- [⚙️ Modules](#modules)
- [🚀 Getting Started](#-getting-started)
  - [🔧 Installation](#-installation)
  - [🤖 Running the app](#-running-the-app)
- [🛣 Project Roadmap](#-project-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [👏 Acknowledgments](#-acknowledgments)

## 📍 Overview



## 📂 Repository Structure

```sh
└── ai_fitness_trainer_v2/
    ├── backend/
    │   ├── main.py
    │   ├── requirements.txt
    │   ├── s_6_best.pt
    │   └── utils/
    │       ├── condition_check.py
    │       ├── countings.py
    │       └── yolo_model.py
    └── frontend/
        ├── .eslintrc.cjs
        ├── index.html
        ├── package-lock.json
        ├── package.json
        ├── postcss.config.js
        ├── public/
        ├── src/
        │   ├── App.css
        │   ├── App.jsx
        │   ├── App.test.jsx
        │   ├── components/
        │   ├── index.css
        │   ├── main.jsx
        │   ├── reportWebVitals.jsx
        │   ├── routes/
        │   └── setupTests.js
        ├── tailwind.config.js
        └── vite.config.js
```

---

## ⚙️ Modules

### Backend

- **`main.py`** - Runs the FastAPI server and handles requests.
- **`s_6_best.pt`** - Pre-trained YOLOv8 model for pose detection.
- **`utils/condition_check.py`** - Evaluates exercise correctness.
- **`utils/countings.py`** - Counts exercise repetitions.
- **`utils/yolo_model.py`** - Loads and processes pose detection using YOLO.

### Frontend

- **React-based UI** with routes and components.
- **Uses Vite for development.**
- **Styled using TailwindCSS.**

## 🚀 Getting Started

### 🔧 Installation

1. Clone the repository:

```sh
git clone https://github.com/vasanth_mark_23/ai_fitness_trainer_v2
```

2. Navigate to the project directory:

```sh
cd ai_fitness_trainer_v2
```

3. Install backend dependencies:

```sh
cd backend
pip install -r requirements.txt
```

4. Install frontend dependencies:

```sh
cd frontend
npm install
```

### 🤖 Running the app

1. Start the backend server:

```sh
cd backend
uvicorn main:app --reload
```

2. Start the frontend application:

```sh
cd frontend
npm run dev
```

---

## 🛣 Project Roadmap

> - [X] `ℹ️  Task 1: YOLOv8 Integration`
> - [X] `ℹ️  Task 2: React UI Implementation`
> - [X] `ℹ️  Task 3: FastAPI Backend`
> - [X] `ℹ️  Task 4: Documentation`

---

## 🤝 Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`feature-branch`).
3. Commit your changes.
4. Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👏 Acknowledgments

Special thanks to the contributors and open-source projects that made this possible!