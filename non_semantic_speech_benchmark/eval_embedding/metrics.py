# coding=utf-8
# Copyright 2021 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""Metrics for evaluation.

1) Equal Error Rate (EER) metric.
2) D-Prime.
3) AUC.
"""

import math
from typing import Any, Iterable, Tuple, Optional

import numpy as np
import scipy.stats
from sklearn import metrics as skmetrics


def calculate_eer(labels, scores):
  """Returns the equal error rate for a binary classifier.

  EER is defined as the point on the DET curve where the false positive and
  false negative rates are equal.

  Args:
    labels: Ground truth labels for each data point.
    scores: Regression scores for each data point. A score of 1 indicates a
      classification of label 1.

  Returns:
    eer: The Equal Error Rate.
  """
  fpr, fnr = calculate_det_curve(labels, scores)
  min_diff_idx = np.argmin(np.abs(fpr - fnr))
  return np.mean((fpr[min_diff_idx], fnr[min_diff_idx]))


def calculate_det_curve(labels,
                        scores):
  """Calculates the false positive and negative rate at each score.

  The DET curve is related to the ROC curve, except it plots false positive rate
  against false negative rate.
  See https://en.wikipedia.org/wiki/Detection_error_tradeoff for a full
  description of the DET curve.

  Args:
    labels: Ground truth labels for each data point.
    scores: Regression scores for each data point. A score of 1 indicates a
      classification of label 1. Should be in range (0, 1).

  Returns:
    fpr, fnr
    All returned values are numpy arrays with the same length as scores.
    fpr: False positive rate at a given threshold value.
    fnr: False negative rate at a given threshold value.
  """

  scores = np.asarray(scores, dtype=float)
  labels = np.asarray(labels, dtype=float)
  indices = np.argsort(scores)
  labels = labels[indices]
  fnr = np.cumsum(labels) / np.sum(labels)
  fnr = np.insert(fnr, 0, 0)

  negative_labels = 1 - labels
  fpr = np.cumsum(negative_labels[::-1])[::-1]
  fpr /= np.sum(negative_labels)
  fpr = np.append(fpr, 0)

  return fpr, fnr


def calculate_auc(labels,
                  predictions,
                  sample_weight = None):
  return skmetrics.roc_auc_score(
      labels, predictions, sample_weight=sample_weight)


def dprime_from_auc(auc):
  """Returns a d-prime measure corresponding to an ROC area under the curve.

  D-prime denotes the sensitivity index:
  https://en.wikipedia.org/wiki/Sensitivity_index

  Args:
    auc: (float) Area under an ROC curve.

  Returns:
    Float value representing the separation of score distributions
    between negative and positive scores for a labeler (an algorithm or
    group of readers who assign continuous suspicion scores to a series
    of cases). The AUC is given by PHI(mu / sqrt(2)), where PHI is the
    cumulative distribution function of the normal distribution.
  """
  return math.sqrt(2) * scipy.stats.norm.ppf(auc)
