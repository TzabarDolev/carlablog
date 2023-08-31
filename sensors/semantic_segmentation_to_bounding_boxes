## The following code is a part of Sensors section at my Carla simulator research blog - https://carlablog.carrd.co/.
## Feel free to show your support via requested, suggestions and interesting ideas for future research material.

## At this case, we set a minimum size for and a maximum depth the bounding box.

def fill_bb(img_semantic, img_depth):
    
    bb = []

    # Reshape the 3D array to a 2D array where each row represents a unique pixel value
    semantic_tags = np.unique(img_semantic.reshape(-1, 3), axis=0)
    for tag in semantic_tags:
        if self.ref_dict[tuple(tag)] in self.annotations_cl:
            # create a mask for each semantic tag
            mask = np.all(img_semantic == tag, axis=-1) * 1

            # find groups of connected components
            num_labels, labels = cv2.connectedComponents(mask.astype('uint8'))

            for label in range(1, num_labels):  # Skip label 0 (background)
                component_mask = np.where(labels == label, 1, 0)
                # Find the coordinates of the painted pixels
                points = cv2.findNonZero(component_mask)

                # Find the bounding rectangle of the points
                x, y, w, h = cv2.boundingRect(points)

                if w > min_width and h > min_height and img_depth[int((y + h / 2)), int((x + w / 2))] < max_depth:

                    # Calculate the center and size of the bounding box in YOLO format
                    center_x = (x + w / 2) / img_semantic.shape[1]
                    center_y = (y + h / 2) / img_semantic.shape[0]

                    width = w / img_semantic.shape[1]
                    height = h / img_semantic.shape[0]

                    # Append the bounding box to the list
                    cl = self.annotations_tags[np.where(np.array(self.annotations_cl) == self.ref_dict[tuple(tag)])[0][0]]
                    bb.append((cl, center_x, center_y, width, height))

        if len(bb) == 0:
            return 0
        else:
            return bb
