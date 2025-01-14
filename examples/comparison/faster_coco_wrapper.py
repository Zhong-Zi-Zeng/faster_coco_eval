# Copyright (c) MiXaill76.
from collections import defaultdict
from pathlib import Path
from faster_coco_eval import COCO as _COCO
from faster_coco_eval import COCOeval_faster as _COCOeval
import faster_coco_eval.core.mask as _mask_util
from typing import Dict, Optional, Sequence, Union


class COCO(_COCO):
    """This class is almost the same as official pycocotools package.

    It implements some snake case function aliases. So that the COCO class has
    the same interface as LVIS class.

    Args:
        annotation_file (str, optional): Path of annotation file.
            Defaults to None.
    """

    def __init__(self,
                 annotation_file: Optional[Union[str, Path]] = None) -> None:
        super().__init__(annotation_file=annotation_file)
        self.img_ann_map = self.imgToAnns
        self.cat_img_map = self.catToImgs

    def get_ann_ids(self,
                    img_ids: Union[list, int] = [],
                    cat_ids: Union[list, int] = [],
                    area_rng: Union[list, int] = [],
                    iscrowd: Optional[bool] = None) -> list:
        """Get annotation ids that satisfy given filter conditions.

        Args:
            img_ids (list | int): Get annotations for given images.
            cat_ids (list | int): Get categories for given images.
            area_rng (list | int): Get annotations for given area range.
            iscrowd (bool, optional):  Get annotations for given crowd label.

        Returns:
            List: Integer array of annotation ids.
        """
        return self.getAnnIds(img_ids, cat_ids, area_rng, iscrowd)

    def get_cat_ids(self,
                    cat_names: Union[list, int] = [],
                    sup_names: Union[list, int] = [],
                    cat_ids: Union[list, int] = []) -> list:
        """Get category ids that satisfy given filter conditions.

        Args:
            cat_names (list | int): Get categories for given category names.
            sup_names (list | int): Get categories for given supercategory
                names.
            cat_ids (list | int):  Get categories  for given category ids.

        Returns:
            List: Integer array of category ids.
        """
        return self.getCatIds(cat_names, sup_names, cat_ids)

    def get_img_ids(self,
                    img_ids: Union[list, int] = [],
                    cat_ids: Union[list, int] = []) -> list:
        """Get image ids that satisfy given filter conditions.

        Args:
            img_ids (list | int): Get images for given ids
            cat_ids (list | int): Get images with all given cats

        Returns:
            List: Integer array of image ids.
        """
        return self.getImgIds(img_ids, cat_ids)

    def load_anns(self, ids: Union[list, int] = []) -> list:
        """Load annotations with the specified ids.

        Args:
            ids (list | int): Integer ids specifying annotations.

        Returns:
            List[dict]: Loaded annotation objects.
        """
        return self.loadAnns(ids)

    def load_cats(self, ids: Union[list, int] = []) -> list:
        """Load categories with the specified ids.

        Args:
            ids (list | int): Integer ids specifying categories.

        Returns:
            List[dict]: loaded category objects.
        """
        return self.loadCats(ids)

    def load_imgs(self, ids: Union[list, int] = []) -> list:
        """Load annotations with the specified ids.

        Args:
            ids (list): integer ids specifying image.

        Returns:
            List[dict]: Loaded image objects.
        """
        return self.loadImgs(ids)


class COCOPanoptic(COCO):
    """This wrapper is for loading the panoptic style annotation file."""

    def createIndex(self) -> None:
        """Create index."""
        # create index
        print('creating index...')
        # anns stores 'segment_id -> annotation'
        anns: Dict[int, list] = {}
        cats: Dict[int, dict] = {}
        imgs: Dict[int, dict] = {}
        img_to_anns, cat_to_imgs = defaultdict(list), defaultdict(list)
        if 'annotations' in self.dataset:
            for ann in self.dataset['annotations']:
                for seg_ann in ann['segments_info']:
                    # to match with instance.json
                    seg_ann['image_id'] = ann['image_id']
                    img_to_anns[ann['image_id']].append(seg_ann)
                    # segment_id is not unique in coco dataset orz...
                    # annotations from different images but
                    # may have same segment_id
                    if seg_ann['id'] in anns.keys():
                        anns[seg_ann['id']].append(seg_ann)
                    else:
                        anns[seg_ann['id']] = [seg_ann]

            # filter out annotations from other images
            img_to_anns_ = defaultdict(list)
            for k, v in img_to_anns.items():
                img_to_anns_[k] = [x for x in v if x['image_id'] == k]
            img_to_anns = img_to_anns_

        if 'images' in self.dataset:
            for img_info in self.dataset['images']:
                img_info['segm_file'] = img_info['file_name'].replace(
                    'jpg', 'png')
                imgs[img_info['id']] = img_info

        if 'categories' in self.dataset:
            for cat in self.dataset['categories']:
                cats[cat['id']] = cat

        if 'annotations' in self.dataset and 'categories' in self.dataset:
            for ann in self.dataset['annotations']:
                for seg_ann in ann['segments_info']:
                    cat_to_imgs[seg_ann['category_id']].append(ann['image_id'])

        print('index created!')

        self.anns = anns
        self.imgToAnns = img_to_anns
        self.catToImgs = cat_to_imgs
        self.imgs = imgs
        self.cats = cats

    def load_anns(self, ids: Union[list, int] = []) -> list:
        """Load annotations with the specified ids.

        ``self.anns`` is a list of annotation lists instead of a
        list of annotations.

        Args:
            ids (Union[List[int], int]): Integer ids specifying annotations.

        Returns:
            List: Loaded annotation objects.
        """
        anns = []

        if isinstance(ids, Sequence):
            # self.anns is a list of annotation lists instead of
            # a list of annotations
            for id in ids:
                anns += self.anns[id]
            return anns
        else:
            return self.anns[ids]


# just for the ease of import
COCOeval = _COCOeval
mask_util = _mask_util
