# Code-Fixer LLM (online compiler auto-repair)

Flow: user code -> compiler -> error -> LLM fixes code -> compile again -> repeat
with the new error until the code compiles (max 6 attempts).
Languages: Java, C, C++, Python. Windows + NVIDIA RTX 3060 + VS Code.

## Step 1: Install tools (once)
1. Python 3.12 (python.org, tick "Add python.exe to PATH")
2. Git (git-scm.com), VS Code (+ Python extension)
3. PowerShell:
   winget install BrechtSanders.WinLibs.POSIX.UCRT
   winget install Microsoft.OpenJDK.21
4. CLOSE PowerShell, open a new one, check:
   py -3.12 --version
   gcc --version
   g++ --version
   javac -version
   git --version
   nvidia-smi        (shows your VRAM: 12 GB or 6 GB)

## Step 2: Open this folder in VS Code
File -> Open Folder -> this code-fixer folder.
Open a terminal (Ctrl+`) and run:
   py -3.12 -m venv env
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   .\env\Scripts\Activate.ps1
   python --version          (must be 3.12.x, and (env) must show)
Ctrl+Shift+P -> Python: Select Interpreter -> .\env\Scripts\python.exe
Activate the env again in every new terminal.

## Step 3: Install libraries
   pip install --upgrade pip
   pip install torch --index-url https://download.pytorch.org/whl/cu124
   pip install -r requirements.txt
   python -c "import torch; print(torch.cuda.is_available())"     (must print True)

## Step 4: Collect correct programs
   git clone --depth 1 https://github.com/TheAlgorithms/Python
   git clone --depth 1 https://github.com/TheAlgorithms/Java
   git clone --depth 1 https://github.com/TheAlgorithms/C
   git clone --depth 1 https://github.com/TheAlgorithms/C-Plus-Plus
   python copy_programs.py

## Step 5: Build the dataset (10-30 min)
   python make_data.py
Done when TOTAL is 2000+ and each language is above ~400.

## Step 6: Train (40-90 min, keep laptop plugged in, sleep = Never)
   python train.py
Done when it prints DONE. 6 GB VRAM: use the 0.5B model in train.py and merge.py.
Out of memory: set max_length=1024.

## Step 7: Merge
   python merge.py        (creates code-fixer-model/)

## Step 8: Test
   python test_repair.py  (one broken program per language)

## Step 9: Measure fix rate per language (for your report)
   python evaluate.py

## Step 10: Run the API
   uvicorn main:app --port 8000
Open http://localhost:8000/docs -> POST /fix -> Try it out.

## Step 11: Call it from your online compiler's frontend
   const res = await fetch("http://localhost:8000/fix", {
     method: "POST",
     headers: { "Content-Type": "application/json" },
     body: JSON.stringify({ code: userCode, language: "python" })
   });
   const data = await res.json();
   if (data.success) editor.setValue(data.fixed_code);
   else alert("Could not fully fix it. Last error:\n" + data.error);

Note: "correct" means the code compiles without errors. It may still give wrong output.
