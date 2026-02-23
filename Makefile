.PHONY: proto-go proto-python proto clean init

proto: proto-go proto-python

proto-go:
	@echo "Generating Go gRPC code..."
	python -c "import os; os.makedirs('action-service/pb', exist_ok=True)"
	protoc -I=proto --go_out=action-service/pb --go_opt=paths=source_relative --go-grpc_out=action-service/pb --go-grpc_opt=paths=source_relative tracker.proto

proto-python:
	@echo "Generating Python gRPC code..."
	python -c "import os; os.makedirs('movement-service/pb', exist_ok=True)"
	python -m grpc_tools.protoc -I=proto --python_out=movement-service/pb --grpc_python_out=movement-service/pb tracker.proto
	python -c "open('movement-service/pb/__init__.py', 'a').close()"

init:
	@echo "Updating Python tools..."
	cd movement-service && python -m pip install --upgrade pip setuptools wheel
	@echo "Installing Python dependencies..."
	cd movement-service && python -m pip install -r requirements.txt
	@echo "Initializing Go module..."
	cd action-service && go mod tidy

clean:
	-rmdir /s /q action-service\pb
	-rmdir /s /q movement-service\pb