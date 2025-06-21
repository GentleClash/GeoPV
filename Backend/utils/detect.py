import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from ultralytics import YOLO
#from utils.image_processing import preprocess_image
from time import time
from torch.cuda import is_available

def mask_iou_vectorized(mask1, mask2) -> float:
    """Optimized IoU calculation between two binary masks"""
    intersection = np.logical_and(mask1, mask2).sum()
    union = np.logical_or(mask1, mask2).sum()
    return intersection / union if union != 0 else 0

def create_ensemble_predictor(model_n_path, model_s_path, nms_iou_threshold=0.5) -> callable:
    """Create ensemble predictor using N and S models with optimizations"""
    # Load models with GPU if available
    device = 'cuda' if is_available() else 'cpu'
    model_n = YOLO(model_n_path)
    model_s = YOLO(model_s_path)

    # Move models to device
    if device == 'cuda':
        model_n.to(device)
        model_s.to(device)

    def ensemble_predict(image, conf_threshold=0.51) -> tuple:
        # Get image dimensions once
        img_h, img_w = image.shape[:2]

        # Run both models with optimized settings
        results_n = model_n.predict(
            image,
            conf=0.001,
            save=False,
            verbose=False,
            device=device,
            half=True if device == 'cuda' else False,
            imgsz=640
        )[0]

        results_s = model_s.predict(
            image,
            conf=0.001,
            save=False,
            verbose=False,
            device=device,
            half=True if device == 'cuda' else False,
            imgsz=640
        )[0]

        all_masks = []
        all_confs = []
        target_size = (img_w, img_h)  # Cache target size

        # Process N model results with pre-filtering
        if hasattr(results_n, 'masks') and results_n.masks is not None:
            masks_n = results_n.masks.data
            confs_n = results_n.boxes.conf.cpu().numpy()

            # Pre-filter by confidence to reduce processing
            valid_indices = confs_n >= (conf_threshold * 0.5)  # Lower threshold for ensemble

            if np.any(valid_indices):
                for i in np.where(valid_indices)[0]:
                    if hasattr(masks_n[i], 'cpu'):
                        mask = masks_n[i].cpu().numpy()
                    else:
                        mask = np.array(masks_n[i])

                    all_masks.append(mask)
                    all_confs.append(confs_n[i])

        # Process S model results with pre-filtering
        if hasattr(results_s, 'masks') and results_s.masks is not None:
            masks_s = results_s.masks.data
            confs_s = results_s.boxes.conf.cpu().numpy()

            # Pre-filter by confidence
            valid_indices = confs_s >= (conf_threshold * 0.5)

            if np.any(valid_indices):
                for i in np.where(valid_indices)[0]:
                    if hasattr(masks_s[i], 'cpu'):
                        mask = masks_s[i].cpu().numpy()
                    else:
                        mask = np.array(masks_s[i])

                    all_masks.append(mask)
                    all_confs.append(confs_s[i])

        if not all_masks:
            return [], []

        # Convert to numpy arrays for vectorized operations
        all_confs: np.ndarray = np.array(all_confs)
        # Apply confidence threshold early
        valid_mask = all_confs >= conf_threshold
        if not np.any(valid_mask):
            return [], []

        filtered_masks = [all_masks[i] for i in np.where(valid_mask)[0]]
        filtered_confs = all_confs[valid_mask]

        # Optimized NMS with early termination
        sorted_idxs = np.argsort(filtered_confs)[::-1]
        keep_indices = []
        suppressed = np.zeros(len(sorted_idxs), dtype=bool)

        # Pre-resize all masks once
        resized_masks = []
        for idx in sorted_idxs:
            mask = cv2.resize(
                filtered_masks[idx],
                target_size,
                interpolation=cv2.INTER_NEAREST
            ) > 0.5
            resized_masks.append(mask)

        for i in range(len(sorted_idxs)):
            if suppressed[i]:
                continue

            keep_indices.append(sorted_idxs[i])
            mask_i = resized_masks[i]

            # Vectorized IoU computation for remaining masks
            if i + 1 < len(sorted_idxs):
                remaining_indices = np.arange(i + 1, len(sorted_idxs))
                remaining_indices = remaining_indices[~suppressed[i + 1:]]

                for j_idx in remaining_indices:
                    j = j_idx - (i + 1) + i + 1  # Adjust index
                    if j >= len(resized_masks) or suppressed[j]:
                        continue

                    mask_j = resized_masks[j]
                    iou = mask_iou_vectorized(mask_i, mask_j)

                    if iou > nms_iou_threshold:
                        suppressed[j] = True

        # Return kept masks and confidences
        final_masks = [filtered_masks[i] for i in keep_indices]
        final_confs = [filtered_confs[i] for i in keep_indices]

        return final_masks, final_confs

    return ensemble_predict

def detect_rooftops_with_solar_potential(image_path, model_n_path, model_s_path,
                                                 conf_threshold=0.51, color_opacity=0.7,
                                                 display_original=True, panel_efficiency=0.20,
                                                 solar_radiation=1700, performance_ratio=0.75,
                                                 nms_iou_threshold=0.5) -> dict:
    """
    Optimized version of rooftop detection with solar potential calculation.
    All core logic preserved with performance improvements.
    """

    preprocessing_time_start = time()
    original_image = cv2.imread(image_path)
    if original_image is None:
        raise ValueError(f"Could not load image at {image_path}")

    # Convert from BGR to RGB for display
    original_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    gsd = 0.1280  # meters/pixel
    height, width = original_image.shape[:2]
    image_pixels = height * width
    image_area = height * width * gsd * gsd

    #processed_image = preprocess_image(original_image, sharpen_method='unsharp_mask', amount=1.0)
    processed_image = original_image
    preprocessing_time_end = time()
    print(f"    Preprocessing time: {preprocessing_time_end - preprocessing_time_start:.2f} seconds")

    # Create ensemble predictor
    ensemble_time_start = time()
    ensemble_predictor_time_start = time()
    ensemble_predictor = create_ensemble_predictor(model_n_path, model_s_path, nms_iou_threshold)
    ensemble_predictor_time_end = time()
    print(f"        Ensemble predictor creation time: {ensemble_predictor_time_end - ensemble_predictor_time_start:.2f} seconds")

    # Get predictions from ensemble
    ensemble_masks_time_start = time()
    ensemble_masks, ensemble_confs = ensemble_predictor(processed_image, conf_threshold)
    ensemble_masks_time_end = time()
    print(f"        Ensemble prediction time: {ensemble_masks_time_end - ensemble_masks_time_start:.2f} seconds")
    ensemble_time_end = time()
    print(f"    Ensemble prediction time: {ensemble_time_end - ensemble_time_start:.2f} seconds")

    rooftops = []
    total_coverage = 0
    total_energy_potential = 0

    # Prepare base image
    if display_original:
        base_image = original_rgb.astype(np.float32) / 255.0
    else:
        base_image = np.ones_like(original_rgb, dtype=np.float32)

    # Pre-generate colors 
    np.random.seed(42)
    colors = []
    for _ in range(min(100, len(ensemble_masks) + 10)):  
        h = np.random.uniform(0, 1)
        s = np.random.uniform(0.7, 1.0)
        v = np.random.uniform(0.6, 1.0)

        h_i = int(h * 6)
        f = h * 6 - h_i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)

        if h_i == 0:
            r, g, b = v, t, p
        elif h_i == 1:
            r, g, b = q, v, p
        elif h_i == 2:
            r, g, b = p, v, t
        elif h_i == 3:
            r, g, b = p, q, v
        elif h_i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

        colors.append((r, g, b))

    composite_mask = np.zeros_like(base_image)

    # Vectorized processing 
    target_size = (width, height)
    #print(f"Target size for masks: {target_size}")

    # Process ensemble predictions

    composite_image_time_start = time()
    for i, (original_mask, confidence) in enumerate(zip(ensemble_masks, ensemble_confs)):
        # Resize mask to match image dimensions
        mask = cv2.resize(
            original_mask,
            target_size,
            interpolation=cv2.INTER_NEAREST
        )

        # Convert to binary mask
        mask = mask > 0.5

        # Vectorized area calculation
        mask_area_pixels = np.sum(mask)
        if mask_area_pixels == 0:  # Skip empty masks
            continue

        percentage = (mask_area_pixels / image_pixels) * 100
        area_m2 = (percentage / 100) * image_area

        # Solar potential calculation
        energy_potential = area_m2 * panel_efficiency * solar_radiation * performance_ratio

        total_coverage += percentage
        total_energy_potential += energy_potential

        rooftop_info = {
            'id': i+1,
            'percentage': percentage,
            'area_pixels': mask_area_pixels,
            'area_m2': area_m2,
            'energy_potential_kwh_per_year': energy_potential,
            'confidence': confidence,
        }
        rooftops.append(rooftop_info)

        # Optimized label placement
        if mask_area_pixels > 100:  # Only add labels to significant areas
            y_indices, x_indices = np.where(mask)
            center_y = int(np.mean(y_indices))
            center_x = int(np.mean(x_indices))

            font = cv2.FONT_HERSHEY_SIMPLEX
            text = str(i+1)
            text_size = cv2.getTextSize(text, font, 0.8, 2)[0]  

            cv2.rectangle(
                base_image,
                (center_x - text_size[0]//2 - 3, center_y - text_size[1]//2 - 3),
                (center_x + text_size[0]//2 + 3, center_y + text_size[1]//2 + 3),
                (1, 1, 1),
                -1
            )

            cv2.putText(
                base_image,
                text,
                (center_x - text_size[0]//2, center_y + text_size[1]//2),
                font,
                0.8,
                (0, 0, 0),
                2,
                cv2.LINE_AA
            )

        
        color = colors[i % len(colors)]
        mask_3d = np.stack([mask] * 3, axis=-1)
        color_array = np.array(color).reshape(1, 1, 3)

        composite_mask = np.where(
            mask_3d,
            composite_mask * (1 - color_opacity) + color_array * color_opacity,
            composite_mask
        )

    composite_image_time_end = time()
    print(f"    Composite image creation time: {composite_image_time_end - composite_image_time_start:.2f} seconds")
    plotlib_time_start = time()
    # Optimized final composition
    if display_original:
        mask_exists = composite_mask > 0
        result = np.where(
            mask_exists,
            base_image * (1 - color_opacity) + composite_mask * color_opacity,
            base_image
        )
    else:
        result = np.where(composite_mask > 0, composite_mask, base_image)

    result = np.clip(result, 0, 1)

    # Efficient visualization
    plt.figure(figsize=(12, 10))  
    plt.imshow(result)

    # Optimized legend creation
    legend_elements = []
    for i, rooftop in enumerate(rooftops[:20]):  # Limit legend entries for performance
        color = colors[i % len(colors)]
        legend_elements.append(
            Patch(facecolor=color, edgecolor='black',
                  label=f"R{rooftop['id']}: {rooftop['percentage']:.1f}% - {rooftop['area_m2']:.1f}m²")
        )

    if len(rooftops) > 20:
        legend_elements.append(
            Patch(facecolor='none', edgecolor='none',
                  label=f"... and {len(rooftops) - 20} more rooftops")
        )

    legend_elements.extend([
        Patch(facecolor='none', edgecolor='none',
              label=f"Total: {total_coverage:.2f}%"),
        Patch(facecolor='none', edgecolor='none',
              label=f"Energy: {total_energy_potential:.0f} kWh/year")
    ])

    if rooftops:
        plt.legend(handles=legend_elements, loc='upper right', fontsize='small',
                   title='Rooftop Results', title_fontsize='medium')
    else:
        plt.text(0.5, 0.5, "No rooftops detected", horizontalalignment='center',
                 verticalalignment='center', transform=plt.gca().transAxes,
                 fontsize=14, bbox=dict(facecolor='white', alpha=0.8))

    plt.title('Rooftop Detection & Solar Potential Results')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('rooftop_detection_result.png', dpi=200, bbox_inches='tight')  # Lower DPI
    plotlib_time_stop = time()
    print(f"    Matplotlib plotting time: {plotlib_time_stop - plotlib_time_start:.2f} seconds")
    plt.close()

    # Optimized report generation
    with open("rooftop_solar_potential_report.txt", "w") as f:
        f.write(f"Rooftop Detection and Solar Potential Analysis Report\n")
        f.write(f"===========================================================\n\n")
        f.write(f"Image: {image_path}\n")
        f.write(f"Total area: {image_area:.2f} m²\n")
        f.write(f"Rooftop coverage: {total_coverage:.2f}%\n")
        f.write(f"Solar panel area: {total_coverage * image_area / 100:.2f} m²\n")
        f.write(f"Panel efficiency: {panel_efficiency*100}%\n")
        f.write(f"Solar radiation: {solar_radiation} kWh/m²/year\n")
        f.write(f"Performance ratio: {performance_ratio}\n\n")

        f.write(f"Results:\n")
        f.write(f"- Annual energy: {total_energy_potential:.2f} kWh/year\n")
        f.write(f"- Rooftops detected: {len(rooftops)}\n\n")

        f.write(f"Individual Analysis:\n")
        f.write(f"-------------------\n")
        for rooftop in rooftops:
            f.write(f"\nRooftop {rooftop['id']}: {rooftop['percentage']:.2f}% "
                   f"({rooftop['area_m2']:.2f} m²) - {rooftop['energy_potential_kwh_per_year']:.2f} kWh/year "
                   f"(conf: {rooftop['confidence']:.3f})\n")

    return {
        'total_coverage_percentage': float(total_coverage),
        'total_energy_potential': float(total_energy_potential),
        'rooftops': [
            {
                'id': int(rooftop['id']),
                'percentage': float(rooftop['percentage']),
                'area_pixels': float(rooftop['area_pixels']),
                'area_m2': float(rooftop['area_m2']),
                'energy_potential_kwh_per_year': float(rooftop['energy_potential_kwh_per_year']),
                'confidence': float(rooftop['confidence']),
            } for rooftop in rooftops
        ]
    }

# Example usage with optimized parameters:
if __name__ == "__main__":
    overall_start_time = time()
    results = detect_rooftops_with_solar_potential(
        image_path="image.png",
        model_n_path="../model_N.pt",
        model_s_path="../model_S.pt",
        conf_threshold=0.51,
        nms_iou_threshold=0.5
    )
    overall_end_time = time()
    print(f"Overall processing time: {overall_end_time - overall_start_time:.2f} seconds")

    print(f"Total coverage: {results['total_coverage_percentage']:.2f}%")
    print(f"Total energy potential: {results['total_energy_potential']:.2f} kWh/year")
    print(f"Rooftops detected: {len(results['rooftops'])}")
