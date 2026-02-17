%%writefile pairwise_app.py
# pairwise_app.py
import streamlit as st
import pandas as pd
import random
from PIL import Image
import json
import os

# Configuration
IMAGE_FOLDER = "images"                # <-- Changed to your folder name
RESULTS_FILE = "subjpilot_comparisons.csv"        # <-- Changed output CSV file name
IMAGE_PAIRS = []  # We'll generate these

# Initialize session state
if 'current_pair' not in st.session_state:
    st.session_state.current_pair = None
if 'comparisons' not in st.session_state:
    st.session_state.comparisons = []

# Load images
@st.cache_data
def load_image_paths():
    images = [f for f in os.listdir(IMAGE_FOLDER)
              if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return images[:9]   # <-- Changed to only load 9 images

# Generate pairs
def generate_pairs(images, n_pairs=36):   # <-- Changed for 9 pics with repetitions
    pairs = []
    # Generate pairs ensuring each image appears equally often
    all_pairs = []
    for i in range(len(images)):
        for j in range(i+1, len(images)):
            all_pairs.append((images[i], images[j]))

    # Repeat the pairs 5 times (for 9 images, there are 36 unique pairs)
    for _ in range(5):
        random.shuffle(all_pairs)
        pairs.extend(all_pairs)

    return pairs[:n_pairs*5] if n_pairs*5 < len(pairs) else pairs

# Main app
st.title("🌍 Subjective Pilot: Image Comparison Study")   # <-- Changed title
st.markdown("Which image do you prefer?")   # <-- Changed question

# Load or generate pairs
image_paths = load_image_paths()
if not IMAGE_PAIRS:
    # For 9 images, there are 36 unique pairs, repeated 5 times = 180 comparisons
    IMAGE_PAIRS = generate_pairs(image_paths, 36)  # 36 unique pairs

# Get current pair
if st.session_state.current_pair is None:
    st.session_state.current_pair = random.choice(IMAGE_PAIRS)

img1, img2 = st.session_state.current_pair

# Display images side by side
col1, col2 = st.columns(2)

with col1:
    try:
        image1 = Image.open(os.path.join(IMAGE_FOLDER, img1))
        st.image(image1, use_column_width=True)
        if st.button("Choose LEFT", key="left", use_container_width=True):
            # Record choice
            st.session_state.comparisons.append({
                'image1': img1,
                'image2': img2,
                'winner': img1,
                'timestamp': pd.Timestamp.now()
            })
            # Remove used pair from the list
            if len(IMAGE_PAIRS) > 0:
                IMAGE_PAIRS.remove(st.session_state.current_pair)
            if len(IMAGE_PAIRS) > 0:
                st.session_state.current_pair = random.choice(IMAGE_PAIRS)
            else:
                st.session_state.current_pair = None
            st.rerun()
    except:
        st.error(f"Could not load {img1}")

with col2:
    try:
        image2 = Image.open(os.path.join(IMAGE_FOLDER, img2))
        st.image(image2, use_column_width=True)
        if st.button("Choose RIGHT", key="right", use_container_width=True):
            st.session_state.comparisons.append({
                'image1': img1,
                'image2': img2,
                'winner': img2,
                'timestamp': pd.Timestamp.now()
            })
            # Remove used pair from the list
            if len(IMAGE_PAIRS) > 0:
                IMAGE_PAIRS.remove(st.session_state.current_pair)
            if len(IMAGE_PAIRS) > 0:
                st.session_state.current_pair = random.choice(IMAGE_PAIRS)
            else:
                st.session_state.current_pair = None
            st.rerun()
    except:
        st.error(f"Could not load {img2}")

# Skip button
if st.button("⏭️ Skip (Can't decide)", use_container_width=True):
    st.session_state.comparisons.append({
        'image1': img1,
        'image2': img2,
        'winner': 'skip',
        'timestamp': pd.Timestamp.now()
    })
    # Remove used pair from the list
    if len(IMAGE_PAIRS) > 0:
        IMAGE_PAIRS.remove(st.session_state.current_pair)
    if len(IMAGE_PAIRS) > 0:
        st.session_state.current_pair = random.choice(IMAGE_PAIRS)
    else:
        st.session_state.current_pair = None
    st.rerun()

# Progress (total 180 comparisons: 36 pairs × 5 repetitions)
total_comparisons = 180
progress = min(len(st.session_state.comparisons) / total_comparisons, 1.0)
st.progress(progress, text=f"Comparisons: {len(st.session_state.comparisons)}/{total_comparisons}")

# Display remaining pairs count
st.caption(f"Remaining pairs: {len(IMAGE_PAIRS)}")

# Save results periodically
if len(st.session_state.comparisons) % 10 == 0:
    df = pd.DataFrame(st.session_state.comparisons)
    df.to_csv(RESULTS_FILE, index=False)
    st.success(f"Saved {len(st.session_state.comparisons)} comparisons!")

# Export all data
if st.button("📥 Export All Data"):
    df = pd.DataFrame(st.session_state.comparisons)
    df.to_csv("subjpilot_results.csv", index=False)
    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False),
        file_name="subjpilot_comparison_results.csv",
        mime="text/csv"
    )

# Completion message
if len(st.session_state.comparisons) >= total_comparisons:
    st.balloons()
    st.success("🎉 Congratulations! You've completed all 180 comparisons!")
