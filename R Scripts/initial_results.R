dat <- read.csv("~/Downloads/initial_cohort05Nov19.csv", header = T, stringsAsFactors = F)
## dat$TEXT <- NULL

res <- read.csv("~/Desktop/CG_Data/caregivers_annotations19May2020.csv", header = T, stringsAsFactors = F)

## train <- read.csv("~/Desktop/CG_Data/learning_curves/balanced_spouse_train19May2020.csv", header = T, stringsAsFactors = F)

res$file_id <- as.numeric(gsub(".json", '', res$file_id))

colnames(res)[which(colnames(res) == "file_id")] <- "ROW_ID"

tmp <- merge(res, dat, by = "ROW_ID")

## Add "None"
tmp$label_var <- ifelse(tmp$label_var == "", "None", tmp$label_var)

## Drop
colnames(tmp) <- toupper(colnames(tmp))

## Make file smaller
## tmp$NOTE_TEXT <- NULL
## tmp$TEXT <- NULL
## tmp$TEXT_STRING <- NULL

## 26May20 notes: subset MIMIC and focus on those

write.csv(tmp, file = "~/Desktop/CG_Data/initial_results26May2020.csv", row.names = F)

