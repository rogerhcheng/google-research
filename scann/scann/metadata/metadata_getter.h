// Copyright 2021 The Google Research Authors.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.



#ifndef SCANN__METADATA_METADATA_GETTER_H_
#define SCANN__METADATA_METADATA_GETTER_H_

#include "absl/synchronization/mutex.h"
#include "scann/data_format/datapoint.h"
#include "scann/data_format/dataset.h"
#include "scann/data_format/features.pb.h"
#include "scann/utils/types.h"

namespace tensorflow {
namespace scann_ops {

template <typename T>
class MetadataGetter;

class UntypedMetadataGetter {
 public:
  virtual Status AppendMetadata(const GenericFeatureVector& gfv);

  virtual Status UpdateMetadata(DatapointIndex idx,
                                const GenericFeatureVector& gfv);

  virtual Status RemoveMetadata(DatapointIndex removed_idx);

  virtual bool needs_dataset() const;

  virtual tensorflow::scann_ops::TypeTag TypeTag() const = 0;

  virtual StatusOr<std::string> GetByDatapointIndex(
      DatapointIndex dp_idx) const {
    return UnimplementedError(
        StrCat("Cannot get metadata by datapoint index for "
               "metadata getter type ",
               typeid(*this).name(), "."));
  }

  virtual ~UntypedMetadataGetter();

 private:
  absl::Mutex mutex_;
};

template <typename T>
class MetadataGetter : public UntypedMetadataGetter {
 public:
  MetadataGetter() {}

  tensorflow::scann_ops::TypeTag TypeTag() const final {
    return TagForType<T>();
  }

  virtual Status GetMetadata(const TypedDataset<T>* dataset,
                             const DatapointPtr<T>& query,
                             DatapointIndex neighbor_index,
                             std::string* result) const = 0;

 private:
  TF_DISALLOW_COPY_AND_ASSIGN(MetadataGetter);
};

}  // namespace scann_ops
}  // namespace tensorflow

#endif
