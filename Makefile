.PHONY: proto-go proto-python proto clean init tidy run

ifeq ($(OS),Windows_NT)
    # Windows Settings
    VENV_MOVE := movement-service\venv\Scripts
    VENV_AUDIO := audio-service\venv\Scripts
    RM_DIR := rmdir /s /q
    PYTHON := python
else
    # Mac/Linux Settings
    VENV_MOVE := movement-service/venv/bin
    VENV_AUDIO := audio-service/venv/bin
    RM_DIR := rm -rf
    PYTHON := python3
endif

proto: proto-go proto-python tidy

proto-go:
	@echo "Generating Go gRPC code..."
	$(PYTHON) -c "import os; os.makedirs('action-service/pb', exist_ok=True)"
	protoc -I=proto --go_out=action-service/pb --go_opt=paths=source_relative --go-grpc_out=action-service/pb --go-grpc_opt=paths=source_relative tracker.proto

proto-python:
	@echo "Generating Python gRPC code for movement-service..."
	$(PYTHON) -c "import os; os.makedirs('movement-service/pb', exist_ok=True)"
	$(PYTHON) -m grpc_tools.protoc -I=proto --python_out=movement-service/pb --grpc_python_out=movement-service/pb tracker.proto
	$(PYTHON) -c "open('movement-service/pb/__init__.py', 'a').close()"
	
	@echo "Generating Python gRPC code for audio-service..."
	$(PYTHON) -c "import os; os.makedirs('audio-service/pb', exist_ok=True)"
	$(PYTHON) -m grpc_tools.protoc -I=proto --python_out=audio-service/pb --grpc_python_out=audio-service/pb tracker.proto
	$(PYTHON) -c "open('audio-service/pb/__init__.py', 'a').close()"

init:
	@echo "Creating virtual environments..."
	$(PYTHON) -m venv movement-service/venv
	$(PYTHON) -m venv audio-service/venv

	@echo "Updating Python tools..."
	$(VENV_MOVE)/python -m pip install --upgrade pip setuptools wheel
	$(VENV_AUDIO)/python -m pip install --upgrade pip setuptools wheel
	
	@echo "Installing movement-service dependencies..."
	$(VENV_MOVE)/python -m pip install -r movement-service/requirements.txt
	
	@echo "Installing audio-service dependencies..."
	$(VENV_AUDIO)/python -m pip install -r audio-service/requirements.txt
	
	@echo "Initializing Go module..."
	cd action-service && go mod tidy

tidy:
	@echo "Stripping unused Go dependencies and formatting code..."
	cd action-service && go mod tidy

clean:
	-$(RM_DIR) action-service/pb
	-$(RM_DIR) movement-service/pb
	-$(RM_DIR) audio-service/pb

run:
	@echo "Starting the Theremin Cluster..."
	$(PYTHON) launcher.py