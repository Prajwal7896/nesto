from .correction_models import CorrectionReport


def create_correction_report(scene_id, floor_id):
    return CorrectionReport(
        scene_id=scene_id,
        floor_id=floor_id
    )