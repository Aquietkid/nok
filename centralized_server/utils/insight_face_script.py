import cv2
import insightface
import numpy as np
import os
from pathlib import Path

def verify_person(reference_paths, test_images, threshold=0.4, show_results=True):
    if not test_images:
        raise ValueError("No test images provided.")
    if not reference_paths:
        raise ValueError("No reference images provided.")

    app = insightface.app.FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=0)

    def get_embedding(img_path):
        img = cv2.imread(img_path)
        if img is None:
            raise FileNotFoundError(f"Could not read image at {img_path}")
        faces = app.get(img)
        if not faces:
            raise ValueError(f"No face found in {img_path}")
        return faces[0].embedding / np.linalg.norm(faces[0].embedding)

    # compute embeddings for all references
    reference_embeddings = []
    for ref in reference_paths:
        try:
            reference_embeddings.append(get_embedding(ref))
        except Exception as e:
            print(f"Skipping {ref}: {e}")

    if not reference_embeddings:
        raise ValueError("No valid reference embeddings found.")

    for img_path in test_images[:5]:
        if not os.path.exists(img_path):
            print(f"Skipping {img_path} (not found)")
            continue

        img = cv2.imread(img_path)
        faces = app.get(img)
        if not faces:
            print(f"No face found in {img_path}")
            continue

        for f in faces:
            emb = f.embedding / np.linalg.norm(f.embedding)

            for ref_emb, ref_path in zip(reference_embeddings, reference_paths):
                sim = np.dot(ref_emb, emb)
                label = "MATCH" if sim > (1 - threshold) else "NO MATCH"
                print(f"{img_path} vs {ref_path}: {label} (similarity={sim:.2f})")

                if show_results:
                    x1, y1, x2, y2 = f.bbox.astype(int)
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img, f"{label} ({sim:.2f})", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.imshow("Result", img)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()

                if label == "MATCH":
                    return True  # stop early if any match

    return False  # no matches