import subprocess
import argparse
import sys
import os

def run_script(script_name, args=[]):
    cmd = [sys.executable, script_name] + args
    print(f"\n>>> Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"Error: {script_name} failed with return code {result.returncode}")
        sys.exit(result.returncode)

def main():
    parser = argparse.ArgumentParser(description="End-to-End Stock Forecasting & Portfolio Optimization Pipeline")
    parser.add_argument("--quick", action="store_true", help="Run in quick mode (few LSTM epochs) for verification")
    parser.add_argument("--epochs", type=int, default=100, help="Number of LSTM epochs (default: 100)")
    parser.add_argument("--step", choices=["all", "download", "pivot", "features", "baselines", "lstm", "optimize"], default="all")
    args = parser.parse_args()

    # Move to the script's directory to ensure correct file paths
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if args.step == "all":
        run_script("download_data.py")
        run_script("pivot_data.py")
        run_script("feature_engineering.py")
        run_script("train_ma_lr.py")
        
        lstm_args = ["--quick"] if args.quick else ["--epochs", str(args.epochs)]
        run_script("train_pca_lstm.py", lstm_args)
        
        run_script("portfolio_optimization.py")
        print("\nPipeline run completed successfully!")
    else:
        if args.step == "download":
            run_script("download_data.py")
        elif args.step == "pivot":
            run_script("pivot_data.py")
        elif args.step == "features":
            run_script("feature_engineering.py")
        elif args.step == "baselines":
            run_script("train_ma_lr.py")
        elif args.step == "lstm":
            lstm_args = ["--quick"] if args.quick else ["--epochs", str(args.epochs)]
            run_script("train_pca_lstm.py", lstm_args)
        elif args.step == "optimize":
            run_script("portfolio_optimization.py")

if __name__ == "__main__":
    main()
