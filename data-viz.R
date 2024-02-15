# Load libraries
library(ggplot2)
library(cowplot)
library(dplyr)

# Load csv files
file_path <- "/Users/arijacob/Documents/Bios10602/Final-Project/SRR702063.annovar.hg38_multianno.exonic.csv"
alignment <- read.csv(file_path)
file_path_2 <- "/Users/arijacob/Documents/Bios10602/Final-Project/SRR702063.annovar.hg38_multianno.csv"
e_and_i <- read.csv(file_path_2)



# Create a dataframe for different counts
vriantByChr <- alignment %>%
  count(Chr) %>%
  filter(n > 30) %>%
  as.data.frame()

# Bar plot of mutation counts per chromosome 
ggplot(variantByChr, aes(x = Chr, y = n)) +
  geom_bar(stat = "identity", fill = "skyblue") +
  labs(title = "Number of variants per Chromosome", x = "Chromosomes", y = "Counts") +
  theme(axis.text.x = element_text(size = 8, angle = 45, hjust = 1))  # Adjust size, angle, and justification of x-axis labels

# Dataframe of variant type
variantByType <- alignment %>%
  count(ExonicFunc.refGene) %>%
  as.data.frame()

names(variantByType) <- c("exonic_mutation_type", "number")


#df of the other variants
variantOthers <- variantByType %>%
  filter(exonic_mutation_type != "nonsynonymous SNV" & 
           exonic_mutation_type != "synonymous SNV" & 
           exonic_mutation_type != "")

#bar plot of other variants
ggplot(variantOthers, aes(x = exonic_mutation_type, y = number)) +
  geom_bar(stat = "identity", fill = "skyblue") +
  labs(title = "Number of other variant types", x = "Variant type", y = "Counts") +
  theme(axis.text.x = element_text(size = 8, angle = 45, hjust = 1))  # Adjust size, angle, and justification of x-axis labels


#df of SNVs
variantSNV <- variantByType %>%
  filter(exonic_mutation_type == "nonsynonymous SNV" |
           exonic_mutation_type == "synonymous SNV")

#Bar plot of SNVs
ggplot(variantSNV, aes(x = exonic_mutation_type, y = number)) +
  geom_bar(stat = "identity", fill = "skyblue") +
  labs(title = "Number of Synonymous vs. Nonsynonymous SNV", x = "SNV type", y = "Counts") +
  theme(axis.text.x = element_text(size = 8, angle = 45, hjust = 1))  # Adjust size, angle, and justification of x-axis labels


#add chr length to df
lengthofChr <- c(248956422, 133797422, 135086622, 133275309, 114364328, 107043718, 101991189, 90338345, 83257441, 80373285, 58617616, 242193529, 64444167, 46709983, 50818468, 198295559, 190214555, 181538259, 170805979, 159345973, 145138636, 138394717, 156040895)
variantByChr <- variantByChr %>%
  mutate(length = lengthofChr)


#Scatter plot of variants vs chr length
ggplot(variantByChr, aes(x = length, y = n, label = Chr)) +
  geom_point(color = "blue")+
  theme_minimal() +
  labs(title = "Number of variants vs. length of chromosome", y = "Number of variants", x = "Length of Chromosome")+
  geom_text(nudge_x = -.5, nudge_y = -40, check_overlap = TRUE)


#Add the number of genes 
genes <- c(2541, 1017, 1567, 1299, 426, 854, 843, 1093, 1459, 367, 1609, 1354, 775, 309, 671, 1394, 926, 1186, 1306, 2508, 908, 1033, 1048)
variantByChr <- variantByChr %>%
  mutate (genes = genes)

#Add the number of exons
exons <- c(22345, 10273, 12459, 12399, 3784, 6837, 8106, 9986, 13179, 3333, 12169, 12506, 6492, 2539, 5173, 13517, 8299, 9946, 11406, 23045, 7823, 8941, 8568)
variantByChr <- variantByChr %>%
  mutate(exons = exons) 

#Add then number of introns
introns <- c(19831, 9256,10892, 11100, 3358, 6106 , 7263, 8893, 11720, 2966, 10560, 11152, 5717, 2230, 4502, 12123, 7373, 8760, 10100, 20537, 6915, 7908, 7520)
variantByChr <- variantByChr %>%
  mutate(introns = introns) 

#Scatter plot of number of variants against genes, exons, and introns
geneplot <- ggplot(variantByChr, aes(x=n, color = Chr))+
  geom_point(aes(y=genes, color = "pink"),
             color="black",
             fill="pink",
             shape=21,
             alpha=0.5,
             size=6,
             stroke = 1
  ) + geom_point(aes(y=exons, colour="lightgreen"),
                 color="black",
                 fill="lightgreen",
                 shape=21,
                 alpha=0.5,
                 size=6,
                 stroke = 1
  ) + geom_point(aes(y=introns, color = "lightblue"),
                 color="black",
                 fill="lightblue",
                 shape=21,
                 alpha=0.5,
                 size=6,
                 stroke = 1
  ) + 
  labs(title = "Variant Count against Gene, Exon, and Intron count of each chromosome", x = "Variants", y = "Count") 
