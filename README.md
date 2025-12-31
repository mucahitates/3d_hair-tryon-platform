# 3D Hair Try-On Pipeline

This project takes user photos, generates a 3D head model, extracts the hair region,  
and lets the user try different hairstyles from our database on their own 3D avatar.

## Features

- Video → frame extraction (OpenCV)
- Smart frame selection (interval + frame difference threshold)
- 3D reconstruction with Metashape (head model)
- Hair region extraction on the 3D model (planned / WIP)
- Pipeline designed for fully automatic processing

## Tech Stack

- Python
- OpenCV (frame extraction & image processing)
- Agisoft Metashape (3D reconstruction)
- NumPy
- JSON-based config system

## Project Flow

1. User uploads a video or multiple photos.
2. System extracts meaningful frames (no duplicates, no tiny changes).
3. Frames are sent to Metashape for 3D reconstruction.
4. Hair region is segmented from the 3D head model.
5. User-selected hairstyle from the database is applied on the 3D avatar (planned).

## Config

All paths and parameters are managed via `config/config.json`:
- Input / output directories
- Frame extraction settings (interval, diff_threshold, resize size)
- User and file format settings

## Running

```bash
python main.py
