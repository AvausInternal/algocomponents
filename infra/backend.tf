terraform {
  backend "gcs" {
    bucket = "data-factory-test-211001-tfstorage"
    prefix = "algocomponents"
  }
}
