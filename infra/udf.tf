resource "google_bigquery_routine" "test_routine_terraform" {
  dataset_id      = "transform"
  routine_id      = "prep_email_to_ads"
  routine_type    = "SCALAR_FUNCTION"
  language        = "SQL"
  definition_body = "TO_HEX(SHA256(LOWER(TRIM(x))))"
  arguments {
    name      = "x"
    data_type = "{\"typeKind\" :  \"STRING\"}"
  }
  return_type = "{\"typeKind\" :  \"STRING\"}" # not necessary
  project     = var.gcp_project_name
}

# various options described here: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_routine