library(sf)
library(tidyverse)

name_abbr <- read_csv("Data/name_abbr - Edit.csv", locale = locale(encoding = "ISO-8859-1"))
world_map <- st_read("Data/world_map.json") %>%
  rename(abbr = "name") %>%
  left_join(name_abbr, by = "abbr")
write_sf(world_map, "Data/IMF_world_map.shp")
st_read("Data/IMF_world_map.shp")

