import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from ultralytics import YOLO
from utils.image_processing import preprocess_image

def mask_iou(mask1, mask2):
    """Calculate IoU between two binary masks"""
    intersection = np.logical_and(mask1, mask2).sum()
    union = np.logical_or(mask1, mask2).sum()
    return intersection / union if union != 0 else 0

def create_ensemble_predictor(model_n_path, model_s_path, nms_iou_threshold=0.5):
    """Create ensemble predictor using N and S models"""
    model_n = YOLO(model_n_path)
    model_s = YOLO(model_s_path)

    def ensemble_predict(image, conf_threshold=0.4):
        # Run both models with very low confidence to get all predictions
        results_n = model_n.predict(image, conf=0.001, save=False, verbose=False)[0]
        results_s = model_s.predict(image, conf=0.001, save=False, verbose=False)[0]

        all_masks = []
        all_confs = []
        all_boxes = []

        # Process N model results
        if hasattr(results_n, 'masks') and results_n.masks is not None:
            masks_n = results_n.masks.data
            confs_n = results_n.boxes.conf.cpu().numpy()
            boxes_n = results_n.boxes.xyxy.cpu().numpy()

            for i in range(len(confs_n)):
                if hasattr(masks_n[i], 'cpu'):
                    mask = masks_n[i].cpu().numpy()
                else:
                    mask = np.array(masks_n[i])

                all_masks.append(mask)
                all_confs.append(confs_n[i])
                all_boxes.append(boxes_n[i])

        # Process S model results
        if hasattr(results_s, 'masks') and results_s.masks is not None:
            masks_s = results_s.masks.data
            confs_s = results_s.boxes.conf.cpu().numpy()
            boxes_s = results_s.boxes.xyxy.cpu().numpy()

            for i in range(len(confs_s)):
                if hasattr(masks_s[i], 'cpu'):
                    mask = masks_s[i].cpu().numpy()
                else:
                    mask = np.array(masks_s[i])

                all_masks.append(mask)
                all_confs.append(confs_s[i])
                all_boxes.append(boxes_s[i])

        if not all_masks:
            return [], []

        # Apply NMS on all predictions
        sorted_idxs = np.argsort(all_confs)[::-1]
        sorted_masks = [all_masks[i] for i in sorted_idxs]
        sorted_confs = [all_confs[i] for i in sorted_idxs]

        suppressed = [False] * len(sorted_masks)
        keep_masks = []
        keep_confs = []

        for i in range(len(sorted_masks)):
            if suppressed[i]:
                continue

            # Resize masks to same size for IoU calculation
            mask_i = cv2.resize(sorted_masks[i], (image.shape[1], image.shape[0]),
                               interpolation=cv2.INTER_NEAREST) > 0.5

            keep_masks.append(sorted_masks[i])
            keep_confs.append(sorted_confs[i])

            for j in range(i + 1, len(sorted_masks)):
                if suppressed[j]:
                    continue

                mask_j = cv2.resize(sorted_masks[j], (image.shape[1], image.shape[0]),
                                   interpolation=cv2.INTER_NEAREST) > 0.5

                iou = mask_iou(mask_i, mask_j)
                if iou > nms_iou_threshold:
                    suppressed[j] = True

        # Filter by confidence threshold
        filtered_masks = []
        filtered_confs = []
        for mask, conf in zip(keep_masks, keep_confs):
            if conf >= conf_threshold:
                filtered_masks.append(mask)
                filtered_confs.append(conf)

        return filtered_masks, filtered_confs

    return ensemble_predict

def detect_rooftops_with_solar_potential(image_path, model_n_path, model_s_path,
                                                 conf_threshold=0.51, color_opacity=0.7,
                                                 display_original=True, panel_efficiency=0.20,
                                                 solar_radiation=1700, performance_ratio=0.75,
                                                 nms_iou_threshold=0.5):
    """
    Detect individual rooftops using ensemble of N and S models, display masked areas with different colors,
    calculate percentage of image covered by each rooftop, and calculate solar potential.

    Args:
        image_path (str): Path to the input image
        model_n_path (str): Path to the N model
        model_s_path (str): Path to the S model
        conf_threshold (float): Confidence threshold for detections
        color_opacity (float): Opacity of color overlays (0.0-1.0)
        display_original (bool): Whether to show masks on original image or just masks
        panel_efficiency (float): Solar panel yield/efficiency (default: 20%)
        solar_radiation (float): Annual average solar radiation on tilted panels (kWh/m²/year)
        performance_ratio (float): Performance ratio, coefficient for losses (range 0.5 to 0.9)
        nms_iou_threshold (float): IoU threshold for NMS in ensemble

    Returns:
        dict: Dictionary containing total coverage and individual rooftop information with solar potential
    """

    original_image = cv2.imread(image_path)
    if original_image is None:
        raise ValueError(f"Could not load image at {image_path}")

    # Convert from BGR to RGB for display
    original_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    gsd = 0.2647  # meters/pixel (Average value for around 115 meters zoom in India)
    height, width = original_image.shape[:2]
    image_pixels = height * width
    image_area = height * width * gsd * gsd

    processed_image = preprocess_image(original_image, sharpen_method='unsharp_mask', amount=1.5)

    # Create ensemble predictor
    ensemble_predictor = create_ensemble_predictor(model_n_path, model_s_path, nms_iou_threshold)

    # Get predictions from ensemble
    ensemble_masks, ensemble_confs = ensemble_predictor(processed_image, conf_threshold)

    rooftops = []
    total_coverage = 0
    total_energy_potential = 0

    if display_original:
        base_image = original_rgb.astype(np.float32) / 255.0
    else:
        base_image = np.ones_like(original_rgb, dtype=np.float32)

    # Generate colors for visualization
    np.random.seed(42)
    colors = []
    for _ in range(100):
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

    # Process ensemble predictions
    for i, (original_mask, confidence) in enumerate(zip(ensemble_masks, ensemble_confs)):
        # Resize mask to match image dimensions
        mask = cv2.resize(
            original_mask,
            (width, height),
            interpolation=cv2.INTER_NEAREST
        )

        # Convert to binary mask
        mask = mask > 0.5

        # Pixel area and percentage
        mask_area_pixels = np.sum(mask)
        percentage = (mask_area_pixels / image_pixels) * 100

        # Actual area in m²
        area_m2 = (percentage / 100) * image_area

        # Solar potential for this rooftop
        # E = A * r * H * PR
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

        # Adding label to the center of each rooftop
        if np.sum(mask) > 0:
            y_indices, x_indices = np.where(mask > 0)
            center_y = int(np.mean(y_indices))
            center_x = int(np.mean(x_indices))

            font = cv2.FONT_HERSHEY_SIMPLEX
            text = str(i+1)
            text_size = cv2.getTextSize(text, font, 1, 2)[0]

            cv2.rectangle(
                base_image,
                (center_x - text_size[0]//2 - 5, center_y - text_size[1]//2 - 5),
                (center_x + text_size[0]//2 + 5, center_y + text_size[1]//2 + 5),
                (1, 1, 1),
                -1
            )

            cv2.putText(
                base_image,
                text,
                (center_x - text_size[0]//2, center_y + text_size[1]//2),
                font,
                1,
                (0, 0, 0),
                2,
                cv2.LINE_AA
            )

        # Applying color to the mask
        color = colors[i % len(colors)]
        for c in range(3):
            composite_mask[:, :, c] = np.where(
                mask > 0,
                composite_mask[:, :, c] * (1 - color_opacity) + color[c] * color_opacity,
                composite_mask[:, :, c]
            )

    # Combining the original image with the colored masks
    if display_original:
        result = np.where(
            composite_mask > 0,
            base_image * (1 - color_opacity) + composite_mask * color_opacity,
            base_image
        )
    else:
        result = np.where(composite_mask > 0, composite_mask, base_image)

    result = np.clip(result, 0, 1)

    # Visualization
    plt.figure(figsize=(15, 12))
    plt.imshow(result)

    legend_elements = []
    for i, rooftop in enumerate(rooftops):
        color = colors[i % len(colors)]
        legend_elements.append(
            Patch(facecolor=color, edgecolor='black',
                  label=f"Rooftop {rooftop['id']}: {rooftop['percentage']:.2f}% - {rooftop['area_m2']:.2f}m² (conf: {rooftop['confidence']:.3f})")
        )

    legend_elements.append(
        Patch(facecolor='none', edgecolor='none',
              label=f"Total Coverage: {total_coverage:.2f}%")
    )
    legend_elements.append(
        Patch(facecolor='none', edgecolor='none',
              label=f"Total Energy Potential: {total_energy_potential:.2f} kWh/year")
    )

    if rooftops:
        plt.legend(handles=legend_elements, loc='upper right', fontsize='medium',
                   title='Rooftop Coverage & Solar Potential', title_fontsize='large')
    else:
        plt.text(0.5, 0.5, "No rooftops detected", horizontalalignment='center',
                 verticalalignment='center', transform=plt.gca().transAxes,
                 fontsize=14, bbox=dict(facecolor='white', alpha=0.8))

    plt.title('Rooftop Detection & Solar Potential Results')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('rooftop_detection_result.png', dpi=300, bbox_inches='tight')

    # Generate report
    with open("rooftop_solar_potential_report.txt", "w") as f:
        f.write(f"Rooftop Detection and Solar Potential Analysis Report\n")
        f.write(f"===========================================================\n\n")
        f.write(f"Image analyzed: {image_path}\n")
        f.write(f"Total area size: {image_area:.2f} m²\n")
        f.write(f"Total rooftop coverage: {total_coverage:.2f}%\n")
        f.write(f"Total available solar panel area: {total_coverage * image_area / 100:.2f} m²\n")
        f.write(f"Solar panel efficiency used: {panel_efficiency*100}%\n")
        f.write(f"Annual average solar radiation: {solar_radiation} kWh/m²/year\n")
        f.write(f"Performance ratio used: {performance_ratio}\n\n")

        f.write(f"Summary Results:\n")
        f.write(f"- Total potential annual energy generation: {total_energy_potential:.2f} kWh/year\n")
        f.write(f"- Number of rooftops detected: {len(rooftops)}\n\n")

        f.write(f"Individual Rooftop Analysis:\n")
        f.write(f"---------------------------\n")
        for rooftop in rooftops:
            f.write(f"\nRooftop {rooftop['id']}:\n")
            f.write(f"- Coverage: {rooftop['percentage']:.2f}% of the image\n")
            f.write(f"- Area: {rooftop['area_m2']:.2f} m²\n")
            f.write(f"- Energy potential: {rooftop['energy_potential_kwh_per_year']:.2f} kWh/year\n")
            f.write(f"- Detection confidence: {rooftop['confidence']:.3f}\n")

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

# Example usage:
if __name__ == "__main__":
    # Use the ensemble function
    results = detect_rooftops_with_solar_potential(
        image_path="image.jpg",
        model_n_path="../model_N.pt",
        model_s_path="../model_S.pt",
        conf_threshold=0.51,
        nms_iou_threshold=0.5
    )

    print(f"Total coverage: {results['total_coverage_percentage']:.2f}%")
    print(f"Total energy potential: {results['total_energy_potential']:.2f} kWh/year")
    print(f"Number of rooftops detected: {len(results['rooftops'])}")
