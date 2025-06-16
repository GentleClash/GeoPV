import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from ultralytics import YOLO 
from utils.image_processing import preprocess_image

def detect_rooftops_with_solar_potential(image_path, model_path, conf_threshold=0.4, color_opacity=0.7,
                                         display_original=True, panel_efficiency=0.20,
                                         solar_radiation=1700, performance_ratio=0.75):
    """
    Detect individual rooftops in an image, display masked areas with different colors,
    calculate percentage of image covered by each rooftop, and calculate solar potential.

    Args:
        image_path (str): Path to the input image
        model_path (str): Path to the YOLOv12-seg model
        conf_threshold (float): Confidence threshold for detections
        color_opacity (float): Opacity of color overlays (0.0-1.0)
        display_original (bool): Whether to show masks on original image or just masks
        panel_efficiency (float): Solar panel yield/efficiency (default: 20%)
        solar_radiation (float): Annual average solar radiation on tilted panels (kWh/m²/year)
        performance_ratio (float): Performance ratio, coefficient for losses (range 0.5 to 0.9)

    Returns:
        dict: Dictionary containing total coverage and individual rooftop information with solar potential
    """
    
    original_image = cv2.imread(image_path)
    if original_image is None:
        raise ValueError(f"Could not load image at {image_path}")

    # Convert from BGR to RGB for display
    original_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    gsd = 0.1358 # meters/pixel (Average value for around 115 meters zoom in India)
    height, width = original_image.shape[:2]
    image_pixels = height * width
    image_area = height * width * gsd * gsd
    
    processed_image = preprocess_image(original_image, sharpen_method='unsharp_mask', amount=1.5)

    model = YOLO(model_path)
    results = model(processed_image, conf=conf_threshold)

    rooftops = []
    total_coverage = 0
    total_energy_potential = 0

    if display_original:
        base_image = original_rgb.astype(np.float32) / 255.0
    else:
        base_image = np.ones_like(original_rgb, dtype=np.float32)

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

    if hasattr(results[0], 'masks') and results[0].masks is not None:
        original_masks = results[0].masks.data

        for i, original_mask in enumerate(original_masks):
            if hasattr(original_mask, 'cpu'):
                original_mask = original_mask.cpu().numpy()
            else:
                original_mask = np.array(original_mask)

            mask = cv2.resize(
                original_mask,
                (width, height),
                interpolation=cv2.INTER_NEAREST
            )

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

    plt.figure(figsize=(15, 12))
    plt.imshow(result)

    legend_elements = []
    for i, rooftop in enumerate(rooftops):
        color = colors[i % len(colors)]
        legend_elements.append(
            Patch(facecolor=color, edgecolor='black',
                  label=f"Rooftop {rooftop['id']}: {rooftop['percentage']:.2f}% - {rooftop['area_m2']:.2f}m²")
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

    with open("rooftop_solar_potential_report.txt", "w") as f:
        f.write(f"Rooftop Detection and Solar Potential Analysis Report\n")
        f.write(f"=================================================\n\n")
        f.write(f"Image analyzed: {image_path}\n")
        f.write(f"Total area size: {image_area} m² \n")
        f.write(f"Total rooftop coverage: {total_coverage:.2f}%\n")
        f.write(f"Total available solar panel area: {total_coverage * image_area / 100:.2f} m²\n")
        f.write(f"Solar panel efficiency used: {panel_efficiency*100}%\n")
        f.write(f"Annual average solar radiation: {solar_radiation} kWh/m²/year\n")
        f.write(f"Performance ratio used: {performance_ratio}\n\n")

        f.write(f"Summary Results:\n")
        f.write(f"- Total potential annual energy generation: {total_energy_potential:.2f} kWh/year\n")

        f.write(f"Individual Rooftop Analysis:\n")
        f.write(f"---------------------------\n")
        for rooftop in rooftops:
            f.write(f"\nRooftop {rooftop['id']}:\n")
            f.write(f"- Coverage: {rooftop['percentage']:.2f}% of the image\n")
            f.write(f"- Area: {rooftop['area_m2']:.2f} m²\n")
            f.write(f"- Energy potential: {rooftop['energy_potential_kwh_per_year']:.2f} kWh/year\n")

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
            } for rooftop in rooftops
        ]
    }
