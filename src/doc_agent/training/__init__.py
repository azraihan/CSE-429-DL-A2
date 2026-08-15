# =============================================================================
# File:     src/doc_agent/training/__init__.py
# Layer:    Training package marker
#
# Contains:
#   datamodule.py   Lightning DataModule - splits, loaders, transforms
#   lit_modules.py  LightningModule wrappers per trainable component
#   train.py        the single training entry point
#   adapt.py        affordable adaptation - LoRA and quantization
#
# Every trainable component (enhancer, OCR reader, retriever) trains through the
# same Lightning path, so seeding, checkpointing, logging and split handling are
# defined once instead of three times.
# =============================================================================

