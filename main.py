from scripts.config_loader import load_config
from scripts.frame_extractor import run_frame_extraction
from scripts.scoring import run_scoring
from scripts.metashape_launcher import run_metashape_headless

def main():
    config = load_config()

    if config["pipeline"]["run_frame_extraction"]:
        run_frame_extraction(config)

    if config["pipeline"]["run_scoring"]:
        run_scoring(config)

    if config["pipeline"]["run_metashape"]:
        run_metashape_headless()

if __name__ == "__main__":
    main()
