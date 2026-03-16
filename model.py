"""Simple ML model placeholder for CI/CD pipeline validation."""
import torch


def get_model_info():
    """Return basic model metadata."""
    return {
        "name": "placeholder_model",
        "version": "1.0",
        "framework": "PyTorch",
        "torch_version": torch.__version__,
    }


def check_environment():
    """Verify that the model runtime environment is ready."""
    info = get_model_info()
    print(f"Model environment ready! Using {info['framework']} {info['torch_version']}")
    return True


if __name__ == "__main__":
    check_environment()
